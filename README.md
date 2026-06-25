# CQ Silvopastoral Dashboard -- Backend (Phase 2)

FastAPI + PostgreSQL backend for the CQ Silvopastoral Dashboard. Adds user accounts, saved station/scenario storage, and a database-backed replacement for the species/region reference data that is currently hardcoded in the Phase 1 frontend's `app.js`.

This is a **separate repository from the frontend on purpose**. GitHub Pages only serves static files (HTML/CSS/JS) -- it cannot run a Python server. So the frontend stays exactly where it is, on GitHub Pages, and this backend gets deployed separately on a platform that can run a real server (Render, used here). The frontend then calls this API over the internet using `fetch()`, the same way it would call any other web API.

```
┌─────────────────────────┐         ┌──────────────────────────┐
│   Frontend (unchanged)   │  fetch  │   This backend            │
│   GitHub Pages           │ ──────> │   Render (FastAPI + PG)   │
│   index.html/css/js      │ <────── │                            │
└─────────────────────────┘  JSON   └──────────────────────────┘
```

---

## What this adds (vs. Phase 1)

| Feature | Phase 1 (frontend only) | Phase 2 (this backend) |
|---|---|---|
| Species/region data | Hardcoded in `app.js` | Stored in DB, served via API, editable without redeploying the frontend |
| User accounts | None | Register/login with hashed passwords + JWT tokens |
| Saved scenarios | None -- resets on page refresh | Persisted per user, per station, in PostgreSQL |
| Calculation logic | Client-side JavaScript | **Unchanged -- still client-side.** The backend stores data; it does not duplicate the profit/cartage math. This keeps the dashboard's real-time slider feel, since nothing needs a network round-trip just to update a number. |

---

## Project structure

```
app/
├── main.py              # FastAPI app instance, CORS, route registration
├── config.py            # Settings read from environment variables
├── database.py          # SQLAlchemy engine + session setup
├── models.py             # SQLAlchemy ORM models (users, stations, scenarios, reference data)
├── schemas.py            # Pydantic request/response shapes
├── auth.py               # Password hashing + JWT creation/validation
├── seed.py                # Populates species/region reference tables
└── routers/
    ├── auth.py            # POST /auth/register, /auth/login, GET /auth/me
    ├── stations.py        # CRUD for station profiles
    ├── scenarios.py        # CRUD for saved scenarios (nested under a station)
    └── reference.py         # GET /reference/species, /reference/regions (public)
requirements.txt
render.yaml               # One-click Render deployment blueprint
.env.example
```

---

## Running locally

Requires Python 3.11+.

```bash
# 1. Clone this repo and enter it
git clone https://github.com/JaberCQU/silvopastoral-backend.git
cd silvopastoral-backend

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# (the defaults work out of the box for local dev -- no editing required)

# 5. Seed the database with species/region reference data
python -m app.seed

# 6. Run the server
uvicorn app.main:app --reload
```

The API is now running at **http://127.0.0.1:8000**.

Visit **http://127.0.0.1:8000/docs** for interactive API documentation (Swagger UI) -- you can register a user, log in, and click "Authorize" to test every protected endpoint directly in the browser without writing any code.

By default this uses a local SQLite file (`silvopastoral.db`) so you can run and test everything with zero database setup. Production uses PostgreSQL instead -- see below.

---

## API reference

| Method | Endpoint | Auth required? | Description |
|---|---|---|---|
| GET | `/` | No | Health check |
| GET | `/reference/species` | No | List all tree species data (replaces hardcoded `SPECIES` in app.js) |
| GET | `/reference/regions` | No | List all region/saleyard data (replaces hardcoded `REGIONS` in app.js) |
| POST | `/auth/register` | No | Create a new user account |
| POST | `/auth/login` | No | Log in, returns a JWT access token |
| GET | `/auth/me` | Yes | Get the currently logged-in user's profile |
| POST | `/stations` | Yes | Create a station profile |
| GET | `/stations` | Yes | List the current user's stations |
| GET | `/stations/{id}` | Yes | Get one station (must be owned by current user) |
| DELETE | `/stations/{id}` | Yes | Delete a station |
| POST | `/stations/{id}/scenarios` | Yes | Save a new scenario under a station |
| GET | `/stations/{id}/scenarios` | Yes | List scenarios for a station |
| GET | `/stations/{id}/scenarios/{sid}` | Yes | Get one scenario |
| PUT | `/stations/{id}/scenarios/{sid}` | Yes | Update a scenario |
| DELETE | `/stations/{id}/scenarios/{sid}` | Yes | Delete a scenario |

"Auth required" endpoints expect an `Authorization: Bearer <token>` header, using the token returned by `/auth/login`.

---

## Deploying to Render (production)

Render's free tier provides both a web service and a PostgreSQL database, which is enough for a student project demo.

1. Push this backend to its own GitHub repository (separate from the frontend repo)
2. Go to [render.com](https://render.com) and sign in with GitHub
3. Click **New > Blueprint**, and select this repository
4. Render will read `render.yaml` and automatically provision:
   - A free PostgreSQL database
   - A free web service running this API, already wired to that database
5. Once deployed, go to the web service's **Environment** tab and update `ALLOWED_ORIGINS` to your actual GitHub Pages URL (e.g. `https://jabercqu.github.io`)
6. After the first deploy, run the seed script once via Render's **Shell** tab (under the web service):
   ```bash
   python -m app.seed
   ```
7. Your API is now live at a URL like `https://cq-silvopastoral-api.onrender.com`

**Note on Render's free tier:** the free web service "spins down" after 15 minutes of inactivity and takes 30-60 seconds to wake up on the next request. This is fine for a class demo but worth mentioning to your professor if a request seems slow on first load.

---

## Connecting the frontend to this API

The Phase 1 frontend currently reads species/region data from hardcoded JavaScript objects (`SPECIES` and `REGIONS` in `app.js`). To connect it to this live API instead, two changes are needed in the frontend repo:

1. Replace the hardcoded `SPECIES` / `REGIONS` objects with a `fetch()` call to this API on page load:
   ```javascript
   const API_BASE = 'https://cq-silvopastoral-api.onrender.com';

   async function loadReferenceData() {
     const [species, regions] = await Promise.all([
       fetch(`${API_BASE}/reference/species`).then(r => r.json()),
       fetch(`${API_BASE}/reference/regions`).then(r => r.json()),
     ]);
     // Convert the returned array into the same {key: {...}} shape
     // the rest of app.js already expects, so no other code changes.
     return {
       SPECIES: Object.fromEntries(species.map(s => [s.key, s])),
       REGIONS: Object.fromEntries(regions.map(r => [r.key, r])),
     };
   }
   ```
2. Add a simple login form and "Save scenario" / "Load scenario" buttons that call the `/auth` and `/stations/.../scenarios` endpoints.

This is intentionally left as a separate frontend change rather than bundled into this backend repo, so each repo's commit history stays focused on one concern -- backend API work here, frontend integration work there.

---

## Why these technology choices

- **FastAPI** -- automatic interactive API docs (`/docs`), built-in request validation via Pydantic, and async support if usage grows
- **SQLAlchemy** -- lets the same code run against SQLite (zero-setup local dev) or PostgreSQL (production) with no code changes, only a different `DATABASE_URL`
- **JWT (python-jose) + bcrypt (passlib)** -- the standard pattern documented in FastAPI's own official security tutorial, rather than a custom auth scheme that would be harder to verify as correct
- **Render** -- free tier covers both the API and the database, with one-click deployment from `render.yaml`, avoiding the steeper setup of AWS/Azure for a student-project stage

---

## Roadmap beyond Phase 2

- **Phase 3**: Add PostGIS to the database, Mapbox GL JS on the frontend, for real paddock-level spatial mapping
- **Phase 4**: Replace manual beef-price/carbon-price sliders with live data feeds (MLA, Clean Energy Regulator)
- **Phase 5**: React Native mobile app calling this same API
