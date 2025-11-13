from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from geoalchemy2 import load_spatialite  # not used but keeps GeoAlchemy import order
from .core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
