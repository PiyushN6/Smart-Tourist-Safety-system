from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum, JSON
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from .db import Base
import enum

class Role(str, enum.Enum):
    tourist = "tourist"
    operator = "operator"
    police = "police"
    admin = "admin"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(Role), default=Role.operator, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class GeofenceRisk(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"

class Geofence(Base):
    __tablename__ = "geofences"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    risk_level = Column(Enum(GeofenceRisk), default=GeofenceRisk.low, nullable=False)
    area = Column(Geometry(geometry_type='POLYGON', srid=4326), nullable=False)
    active = Column(Boolean, default=True)

class LocationSource(str, enum.Enum):
    web = "web"
    mobile = "mobile"
    wearable = "wearable"

class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    ts = Column(DateTime, default=datetime.utcnow, index=True)
    position = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    speed = Column(Integer, nullable=True)
    source = Column(Enum(LocationSource), default=LocationSource.web)

class AlertType(str, enum.Enum):
    panic = "panic"
    geofence_breach = "geofence_breach"

class AlertStatus(str, enum.Enum):
    new = "new"
    ack = "ack"
    resolved = "resolved"

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True)
    type = Column(Enum(AlertType), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    geofence_id = Column(Integer, ForeignKey("geofences.id"), nullable=True)
    ts = Column(DateTime, default=datetime.utcnow)
    location = Column(Geometry(geometry_type='POINT', srid=4326), nullable=True)
    severity = Column(Integer, default=1)
    status = Column(Enum(AlertStatus), default=AlertStatus.new)
    details = Column(JSON, nullable=True)
