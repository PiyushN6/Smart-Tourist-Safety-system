from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from geoalchemy2.shape import from_shape
from shapely.geometry import Polygon
from ..db import get_db
from .. import models
from ..schemas import GeofenceCreate, GeofenceOut
from ..deps import require_roles

router = APIRouter(tags=["geofences"])

@router.post("/", response_model=GeofenceOut, dependencies=[Depends(require_roles(models.Role.admin, models.Role.operator))])
def create_geofence(body: GeofenceCreate, db: Session = Depends(get_db)):
    try:
        poly = Polygon(body.coordinates[0])
    except Exception:
        raise HTTPException(status_code=400, detail="invalid polygon coordinates")
    geom = from_shape(poly, srid=4326)
    gf = models.Geofence(name=body.name, risk_level=body.risk_level, area=geom, active=True)
    db.add(gf)
    db.commit()
    db.refresh(gf)
    return gf

@router.get("/", response_model=list[GeofenceOut])
def list_geofences(db: Session = Depends(get_db)):
    rows = db.query(models.Geofence).all()
    return rows

@router.delete("/{gid}", dependencies=[Depends(require_roles(models.Role.admin, models.Role.operator))])
def delete_geofence(gid: int, db: Session = Depends(get_db)):
    gf = db.get(models.Geofence, gid)
    if not gf:
        raise HTTPException(status_code=404, detail="not found")
    db.delete(gf)
    db.commit()
    return {"ok": True}

@router.get("/geojson")
def geofences_geojson(db: Session = Depends(get_db)):
    rows = db.query(
        models.Geofence.id,
        models.Geofence.name,
        models.Geofence.risk_level,
        func.ST_AsGeoJSON(models.Geofence.area)
    ).all()
    features = []
    for gid, name, risk, gj in rows:
        try:
            geometry = None
            if gj:
                # ST_AsGeoJSON returns a JSON string
                import json
                geometry = json.loads(gj)
            features.append({
                "type": "Feature",
                "geometry": geometry,
                "properties": {
                    "id": gid,
                    "name": name,
                    "risk_level": risk.value if hasattr(risk, 'value') else str(risk),
                },
            })
        except Exception:
            continue
    return {"type": "FeatureCollection", "features": features}

