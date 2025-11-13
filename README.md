# Smart Tourist Safety Monitoring & Incident Response System

Monorepo scaffold with API (FastAPI), AI stubs, Web dashboard (React+TS+Vite, Mapbox), PostGIS, Redis, and a smart contract skeleton for Polygon Amoy.

## Run locally

1. Copy env: `cp .env.example .env` and fill values.
2. Start services: `docker compose up --build`.
3. API: http://localhost:8000/docs
4. AI service: http://localhost:8001/docs
5. Web: http://localhost:5173
6. Adminer (DB UI): http://localhost:8080  (System: PostgreSQL, Server: db, User: postgres, Password: postgres, DB: safety)

## Apps

- apps/api: FastAPI backend with PostGIS, JWT auth stub, health checks
- apps/ai: AI/NLP stubs (dummy responses for now)
- apps/web: React+TS+Vite dashboard, Mapbox-ready + GPS mock controls
- contracts: Solidity DigitalIDRegistry + Hardhat config for Polygon Amoy (testnet)

## Next steps

- Implement DB migrations and models
- Implement auth + roles, geofences, alerts
- Replace AI stubs with real models
- Deploy API (Render/Railway), Web (Vercel), DB (managed Postgres with PostGIS)
