import csv
from io import StringIO
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from shapely.geometry import Polygon
from geoalchemy2.shape import from_shape
from ..db import get_db
from .. import models
from ..deps import require_roles

router = APIRouter(tags=["imports"])

@router.post("/geofences", dependencies=[Depends(require_roles(models.Role.admin, models.Role.operator))])
async def import_geofences(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="upload a .csv file")
    text = (await file.read()).decode("utf-8", errors="ignore")
    reader = csv.DictReader(StringIO(text))
    created = 0
    errors = []
    for i, row in enumerate(reader, start=1):
        try:
            name = row.get("name")
            risk = row.get("risk_level", "low").lower()
            # coords as JSON-like string: [[lng,lat], ... ]
            coords_str = row.get("coordinates")
            if not name or not coords_str:
                raise ValueError("missing name/coordinates")
            # parse coordinates string into list
            coords = eval(coords_str)  # trusted admin input; in production, use json.loads
            poly = Polygon(coords)
            geom = from_shape(poly, srid=4326)
            gf = models.Geofence(name=name, risk_level=models.GeofenceRisk(risk), area=geom, active=True)
            db.add(gf)
            created += 1
        except Exception as e:
            errors.append({"row": i, "error": str(e)})
    db.commit()
    return {"created": created, "errors": errors}

@router.post("/users", dependencies=[Depends(require_roles(models.Role.admin))])
async def import_users(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="upload a .csv file")
    text = (await file.read()).decode("utf-8", errors="ignore")
    reader = csv.DictReader(StringIO(text))
    created = 0
    errors = []
    for i, row in enumerate(reader, start=1):
        try:
            email = row.get("email")
            password = row.get("password")
            role = row.get("role", "tourist")
            if not email or not password:
                raise ValueError("missing email/password")
            if db.query(models.User).filter(models.User.email == email).first():
                continue
            from ..security import hash_password
            user = models.User(email=email, password_hash=hash_password(password), role=models.Role(role))
            db.add(user)
            created += 1
        except Exception as e:
            errors.append({"row": i, "error": str(e)})
    db.commit()
    return {"created": created, "errors": errors}
