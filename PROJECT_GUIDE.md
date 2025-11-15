# Smart Tourist Safety – Full Project Guide

This guide covers everything you need to run, deploy, demo, and extend the Smart Tourist Safety system.

## Live URLs
- API (Render): https://smart-tourist-safety-api.onrender.com
  - Health: https://smart-tourist-safety-api.onrender.com/healthz
  - Swagger Docs: https://smart-tourist-safety-api.onrender.com/docs
- Web (Netlify): https://smart-toursit-safety-system.netlify.app
- GitHub repo: https://github.com/PiyushN6/Smart-Tourist-Safety-system

## Overview
A geofencing safety system:
- Operators/Admins define polygon geofences with a risk level.
- Location ingests trigger alerts when a user enters a risky geofence.
- Alerts can be acknowledged and resolved.

## Architecture
- Web UI: Vite + React + Mapbox GL
- API: FastAPI (Python) + SQLAlchemy + GeoAlchemy2
- DB: PostgreSQL + PostGIS
- Optional: Redis (future use)
- Map: Mapbox tiles

High-level data flow:
1) Web sends requests to API.
2) API stores geofences (PostGIS geometry) and alerts in Postgres.
3) Ingested location runs point-in-polygon and creates alerts.
4) Web shows live alerts and geofences on the map.

## Repository layout
- apps/
  - api/ → FastAPI app
  - web/ → Vite React app
- docs/templates/
  - users.csv → seed users (email,password,role)
  - geofences.csv → seed geofences (name,risk_level,coordinates)
- docker-compose.yml (local stack for API+DB+Web)
- DEPLOY.md (step-by-step deploy)
- PROJECT_GUIDE.md (this file)

## Environment variables
API (Render)
- PROJECT_NAME=smart-tourist-safety
- ENV=prod
- JWT_SECRET=<strong_random_string>
- DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DBNAME
- ALLOW_ORIGINS=https://smart-toursit-safety-system.netlify.app,http://localhost:5173
- POLYGON_RPC_URL=https://rpc-amoy.polygon.technology (not required today)
- CONTRACT_ADDRESS= (empty for now)
- REDIS_URL=redis://HOST:6379/0 (optional)

Web (Netlify)
- VITE_API_URL=https://smart-tourist-safety-api.onrender.com
- VITE_MAPBOX_TOKEN=pk.your_mapbox_public_token
- NODE_VERSION=20

## Local development
Prereqs: Docker Desktop, Node 20, Python 3.11 (optional if not using local venv)

Option A: Docker Compose
- docker compose up -d
- API: http://localhost:8000/docs
- Web: http://localhost:5173
- DB Admin (if enabled): http://localhost:8080

Option B: Run separately
- DB: run your own Postgres with PostGIS
- API:
  - cd apps/api
  - python -m venv .venv && .venv/Scripts/activate (Windows) or source .venv/bin/activate
  - pip install -r requirements.txt
  - set env vars (DATABASE_URL, JWT_SECRET, etc.)
  - uvicorn app.main:app --host 0.0.0.0 --port 8000
- Web:
  - cd apps/web
  - npm install
  - set VITE_MAPBOX_TOKEN and (optional) VITE_API_URL
  - npm run dev

## Database setup (PostGIS)
- On Render Postgres run once:
  - CREATE EXTENSION IF NOT EXISTS postgis;
- On local Postgres, ensure PostGIS extension is installed.

## API quickstart
- Open Swagger: /docs
- Register admin (POST /auth/register)
  - Body: {"email":"admin@example.com","password":"Admin@123","role":"admin"}
- Login (POST /auth/login)
  - Form: username=admin@example.com&password=Admin@123
  - Copy access_token
- Authorize in Swagger (top-right) → paste Bearer token

## CSV import formats
- Users (POST /imports/users; admin only)
  - headers: email,password,role
- Geofences (POST /imports/geofences; admin/operator)
  - headers: name,risk_level,coordinates
  - coordinates value: JSON array of [lng,lat] forming a closed ring
    - Example: [[77.2090,28.6139],[77.2190,28.6139],[77.2190,28.6239],[77.2090,28.6239],[77.2090,28.6139]]

## Web usage
- Open the Netlify site.
- Paste JWT token or use Login form.
- Use “Refresh geofences” and “Refresh alerts”.
- Create geofence (name, risk, and JSON ring in the textarea).
- Move the marker or set center; click “Ingest here”.
- See alerts, Acknowledge, Resolve. Use filters and pagination.

## Demo script (5–7 minutes)
1) Health check: open /healthz; open /docs.
2) Register admin and login; paste token into the Web app.
3) Import or create a geofence; refresh geofences (map overlays appear).
4) Move to inside the geofence and click “Ingest here”.
5) Observe a new alert; Acknowledge then Resolve; show filters.

## Roles
- admin: full access including user import
- operator: manage geofences and view alerts
- tourist: view-only; no write operations (UI hides write controls for tourists)

## Validation (recommended improvements)
- Geofence create: ensure polygon is closed, min 4 vertices, valid coordinates.
- Clear error messages for invalid inputs.

## Tests (suggested)
- Unit tests for polygon in/out cases.
- Integration tests for alert lifecycle: new → ack → resolved.
- Dedup test: ingest same user+geofence within 5 minutes → one alert only.

## Deployment summary
API (Render → Python runtime)
- Root directory: apps/api
- Build command: pip install -r requirements.txt
- Start command: uvicorn app.main:app --host 0.0.0.0 --port 8000
- Env: set as above; enable PostGIS in DB.

Web (Netlify)
- Base directory: apps/web
- Build command: npm install && npm run build (or npm ci if you add package-lock.json)
- Publish directory: apps/web/dist
- Env: VITE_API_URL, VITE_MAPBOX_TOKEN, NODE_VERSION=20

CORS
- API env ALLOW_ORIGINS should include your exact Netlify domain and http://localhost:5173

## Troubleshooting
- 404 at /: normal unless you use the friendly root; use /docs or /healthz.
- 405 at /auth/register: must be POST, not GET.
- CORS error in web console: add your Netlify URL to ALLOW_ORIGINS and restart API.
- Blank map: check VITE_MAPBOX_TOKEN; redeploy.
- geometry type does not exist: enable PostGIS (CREATE EXTENSION postgis).

## Security & operations
- Keep JWT_SECRET long and private; rotate occasionally.
- Restrict Mapbox token to your site domain.
- Consider enabling rate limiting (ingest/imports).
- Use custom domains for Netlify/Render if desired.

## Roadmap / Future work
- Draw geofences on map interactively.
- Alerts CSV export.
- Blockchain (DigitalIDRegistry) integration and verify endpoint.

## Credits
- Map data © Mapbox.
- Built with FastAPI, Postgres/PostGIS, React, Vite.
