from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models
from ..deps import require_roles

router = APIRouter(tags=["alerts"])

@router.get("/", response_model=list)
def list_alerts(
    db: Session = Depends(get_db),
    status: str | None = Query(default=None, description="Filter by status: new|ack|resolved"),
    risk: str | None = Query(default=None, description="Filter by geofence risk: low|medium|high"),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
):
    q = db.query(models.Alert)
    # Filter by status
    if status:
        try:
            st = models.AlertStatus(status)
            q = q.filter(models.Alert.status == st)
        except Exception:
            pass
    # Filter by geofence risk via join
    if risk:
        try:
            rk = models.GeofenceRisk(risk)
            from sqlalchemy import and_
            q = q.join(models.Geofence, models.Geofence.id == models.Alert.geofence_id).filter(models.Geofence.risk_level == rk)
        except Exception:
            pass
    rows = q.order_by(models.Alert.id.desc()).offset(offset).limit(limit).all()
    # Pydantic model not defined for full alert; return minimal fields
    return [
        {
            "id": a.id,
            "type": a.type.value if hasattr(a.type, 'value') else str(a.type),
            "user_id": a.user_id,
            "geofence_id": a.geofence_id,
            "severity": a.severity,
            "status": a.status.value if hasattr(a.status, 'value') else str(a.status),
        }
        for a in rows
    ]

@router.post("/{alert_id}/acknowledge", dependencies=[Depends(require_roles(models.Role.admin, models.Role.operator, models.Role.police))])
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    a = db.get(models.Alert, alert_id)
    if not a:
        return {"ok": False, "error": "not found"}
    a.status = models.AlertStatus.ack
    db.commit()
    return {"ok": True, "id": a.id, "status": a.status.value}

@router.post("/{alert_id}/resolve", dependencies=[Depends(require_roles(models.Role.admin, models.Role.operator, models.Role.police))])
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    a = db.get(models.Alert, alert_id)
    if not a:
        return {"ok": False, "error": "not found"}
    a.status = models.AlertStatus.resolved
    db.commit()
    return {"ok": True, "id": a.id, "status": a.status.value}
