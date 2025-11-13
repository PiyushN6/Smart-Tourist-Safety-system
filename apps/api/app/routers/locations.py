from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from ..db import get_db
from .. import models
from ..schemas import LocationIn, AlertOut
from ..deps import require_roles
from datetime import datetime, timedelta

router = APIRouter(tags=["locations"])

@router.post("/ingest", response_model=list[AlertOut], dependencies=[Depends(require_roles(models.Role.tourist, models.Role.operator, models.Role.police, models.Role.admin))])
def ingest_location(body: LocationIn, db: Session = Depends(get_db)):
    pt = Point(body.lng, body.lat)
    geom = from_shape(pt, srid=4326)

    loc = models.Location(
        user_id=body.user_id,
        position=geom,
        speed=body.speed,
        source=models.LocationSource(body.source or "web"),
    )
    db.add(loc)
    db.flush()

    # Find intersecting active geofences
    gfs = db.query(models.Geofence).filter(
        models.Geofence.active == True,
        func.ST_Intersects(models.Geofence.area, func.ST_SetSRID(func.ST_Point(body.lng, body.lat), 4326))
    ).all()

    alerts_created = []
    window_start = datetime.utcnow() - timedelta(minutes=5)
    for gf in gfs:
        # Dedup: if a recent non-resolved alert exists for same user+geofence, skip
        existing = db.query(models.Alert).filter(
            models.Alert.type == models.AlertType.geofence_breach,
            models.Alert.user_id == body.user_id,
            models.Alert.geofence_id == gf.id,
            models.Alert.ts >= window_start,
            models.Alert.status != models.AlertStatus.resolved,
        ).first()
        if existing:
            continue
        alert = models.Alert(
            type=models.AlertType.geofence_breach,
            user_id=body.user_id,
            geofence_id=gf.id,
            location=geom,
            severity=2 if gf.risk_level.value == "high" else 1,
        )
        db.add(alert)
        alerts_created.append(alert)

    db.commit()
    # refresh ids
    for a in alerts_created:
        db.refresh(a)

    return alerts_created
