from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import health, auth, geofences, locations, blockchain, alerts, imports
from .db import Base, engine
from sqlalchemy import text
from .core.config import settings

app = FastAPI(
    title="Smart Tourist Safety API",
    openapi_components={
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
    },
    openapi_security=[{"bearerAuth": []}],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.ALLOW_ORIGINS.split(",")] if settings.ALLOW_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    # Ensure PostGIS extension exists, then create tables for MVP.
    with engine.connect() as conn:
        try:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        except Exception:
            pass
    Base.metadata.create_all(bind=engine)

app.include_router(health.router)
app.include_router(auth.router, prefix="/auth")
app.include_router(geofences.router, prefix="/geofences")
app.include_router(locations.router, prefix="/locations")
app.include_router(blockchain.router, prefix="/digital-ids")
app.include_router(alerts.router, prefix="/alerts")
app.include_router(imports.router, prefix="/imports")
