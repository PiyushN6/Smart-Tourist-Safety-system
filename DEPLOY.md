# Smart Tourist Safety - Deployment Guide

This guide helps you deploy the API and Web UI today. You can refine features later.

## Prerequisites
- Mapbox access token
- Postgres with PostGIS (managed DB like Render/Railway/Supabase; enable PostGIS extension)
- Optional: Redis (for future features; current app can run without it)

## Environment variables
Create these in your hosting providers:

API (.env or provider dashboard)
- PROJECT_NAME=smart-tourist-safety
- ENV=prod
- JWT_SECRET=replace_with_strong_secret
- DATABASE_URL=postgresql+psycopg://<user>:<pass>@<host>:<port>/<db>
- REDIS_URL=redis://<host>:<port>/0 (optional)
- POLYGON_RPC_URL=https://rpc-amoy.polygon.technology
- CONTRACT_ADDRESS= (keep empty if not using blockchain yet)
- ALLOW_ORIGINS=https://your-web-domain.com,http://localhost:5173

Web (if using Vite env)
- VITE_MAPBOX_TOKEN=your_mapbox_token

## Database setup (managed Postgres)
1) Create a Postgres instance
2) Enable PostGIS extension
   - Run: CREATE EXTENSION IF NOT EXISTS postgis;
3) Note the full connection string and set as DATABASE_URL for the API

## Deploy API (Render/Railway example)
- Repo path: apps/api
- Start command: uvicorn app.main:app --host 0.0.0.0 --port 8000
- Python version: 3.11
- Build: pip install -r requirements.txt (if requirements.txt exists), or your service’s auto-detect
- Expose port 8000
- Set environment variables listed above

Verify after deploy:
- Open https://your-api-domain.com/docs
- Click Authorize and paste a JWT (or register then login to get one)

## Deploy Web (Netlify/Vercel example)
- Repo path: apps/web
- Build command: npm ci && npm run build
- Publish directory: apps/web/dist
- Environment variables: VITE_MAPBOX_TOKEN
- API base URL: In the app requests, the code uses http://localhost:8000 by default. For production, set an env or replace base URLs to your API domain.
  - Quick option: add a VITE_API_URL var and replace fetch URLs to use import.meta.env.VITE_API_URL

## CORS
- Set ALLOW_ORIGINS in API env to your web domain(s), comma-separated
  - Example: https://your-web-domain.com,https://staging-web.netlify.app

## Seeding demo data quickly
- Use the provided CSVs in docs/templates
  - Upload users: POST /imports/users (admin only)
  - Upload geofences: POST /imports/geofences (admin/operator)
- Or register an admin via /auth/register then login at /auth/login

## Demo flow (script)
1) Register or import users (admin/operator)
2) Login to get JWT
3) In Web UI, paste token or use Login form
4) Create a geofence (polygon) or import from CSV
5) Center the map on a test location inside the geofence; click Ingest
6) See a New alert appear; Acknowledge then Resolve
7) Use filters (status/risk) and pagination to navigate alerts

## Troubleshooting
- 401 Unauthorized: ensure you used Bearer token with correct scheme
- CORS blocked: add your web domain to ALLOW_ORIGINS
- Map blank: verify VITE_MAPBOX_TOKEN
- PostGIS errors: ensure extension is installed in your DB

## Optional production hardening
- HTTPS enforced via your provider
- Rotate JWT_SECRET
- Add rate limiting at reverse proxy (e.g., Nginx) or in-app later
