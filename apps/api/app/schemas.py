from pydantic import BaseModel, EmailStr
from typing import Optional, List
from enum import Enum

class Role(str, Enum):
    tourist = "tourist"
    operator = "operator"
    police = "police"
    admin = "admin"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: Role = Role.operator

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: Role
    class Config:
        from_attributes = True

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class GeofenceRisk(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class GeofenceCreate(BaseModel):
    name: str
    risk_level: GeofenceRisk = GeofenceRisk.low
    # GeoJSON Polygon coordinates [[[lng,lat], ...]]
    coordinates: List[List[List[float]]]

class GeofenceOut(BaseModel):
    id: int
    name: str
    risk_level: GeofenceRisk
    active: bool
    class Config:
        from_attributes = True

class LocationIn(BaseModel):
    user_id: Optional[int] = None
    lat: float
    lng: float
    speed: Optional[int] = None
    source: Optional[str] = "web"

class AlertOut(BaseModel):
    id: int
    type: str
    user_id: Optional[int]
    geofence_id: Optional[int]
    severity: int
    status: str
    class Config:
        from_attributes = True
