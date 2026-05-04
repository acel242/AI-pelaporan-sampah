# Python Backend Rules — FastAPI + SQLAlchemy

Loads automatically when working in `backend/**` or `api/**` paths.

## Skill Reference

Use the `python-backend` skill for detailed patterns on:
- FastAPI project structure, async routes, dependency injection
- SQLAlchemy async, transactions, eager loading, migrations
- JWT/OAuth2, password hashing, CORS, API keys
- Upstash Redis caching and rate limiting
- Security hardening

Location: `~/.agents/skills/python-backend/SKILL.md`

---

## Project Structure

```
backend/
├── main.py              # FastAPI app entry, CORS, middleware, lifespan
├── api/
│   └── v1/
│       ├── router.py    # APIRouter aggregation
│       ├── deps.py      # Shared dependencies (get_db, get_admin_key)
│       └── endpoints/   # One file per resource
├── core/
│   ├── config.py        # Settings from env
│   ├── security.py      # Admin key, password hashing
│   └── database.py      # AsyncSessionLocal, get_db
├── models/              # SQLAlchemy ORM models
├── schemas/             # Pydantic request/response models
└── services/            # Business logic layer
```

## Key Files in This Project

- `backend/main.py` — FastAPI app with CORS, lifespan events
- `backend/core/config.py` — `DATABASE_URL`, `SECRET_KEY`, `ALLOWED_ORIGINS`
- `backend/core/security.py` — admin key validation
- `backend/core/database.py` — `AsyncSessionLocal`, `get_db` dependency
- `models.py` (root) — SQLAlchemy models (Report, ReportUpdate, Category)
- `database.py` (root) — SQLite connection

## Async Everything

```python
# ✅ CORRECT — async route
@router.get("/reports")
async def list_reports(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ReportModel).order_by(desc(ReportModel.created_at)))
    return result.scalars().all()

# ❌ WRONG — blocks event loop
@router.get("/reports")
async def list_reports_blocking(db: Session = Depends(get_db)):
    items = db.query(ReportModel).all()  # Sync!
    return items
```

Use `await db.execute()` not `db.execute()` for SQLAlchemy async.

## Pydantic Schemas (Pydantic v2)

```python
from pydantic import BaseModel, Field
from datetime import datetime

class ReportCreate(BaseModel):
    kategori: str = Field(..., description="Waste category code")
    deskripsi: str = Field(..., min_length=1, max_length=500)
    lokasi: str = Field(..., min_length=1, max_length=255)
    latitude: float | None = None
    longitude: float | None = None

class ReportResponse(BaseModel):
    id: int
    kategori: str
    status: str
    deskripsi: str
    lokasi: str
    created_at: datetime
    model_config = {"from_attributes": True}

class ReportStatusUpdate(BaseModel):
    status: str = Field(..., description="New status: BARU, DIVERIFIKASI, DALAM_PROSES, SELESAI, DITUTUP")
```

## Admin Auth

Admin endpoints require `X-Admin-Key` header:

```python
from fastapi import Header, HTTPException

async def get_admin_key(x_admin_key: str = Header(...)):
    if x_admin_key != settings.SECRET_KEY:
        raise HTTPException(401, "Invalid admin key")
    return x_admin_key

@router.patch("/reports/{id}/status", dependencies=[Depends(get_admin_key)])
async def update_report_status(...):
    ...
```

## Redis / Upstash Caching

If adding caching, follow the `python-backend` skill's Upstash patterns:

```python
from upstash_redis import Redis

redis = Redis.from_env()

@app.get("/reports/stats")
async def get_stats():
    cached = redis.get("reports:stats")
    if cached:
        return cached
    stats = compute_stats()
    redis.setex("reports:stats", 300, stats)
    return stats
```

## Report Status Flow

```
BARU → DIVERIFIKASI → DALAM_PROSES → SELESAI → DITUTUP
```

## REST Conventions

| Method | Path | Status |
|--------|------|--------|
| GET | `/api/v1/reports` | 200 (paginated) |
| GET | `/api/v1/reports/{id}` | 200 |
| POST | `/api/v1/reports` | 201 |
| PATCH | `/api/v1/reports/{id}/status` | 200 (admin) |
| GET | `/api/v1/reports/stats` | 200 |
| GET | `/api/v1/reports/hotspots` | 200 (GeoJSON) |
| GET | `/api/v1/categories` | 200 |

- URL paths: **kebab-case**, plural
- No verbs in URLs
- Error format: RFC 7807 problem details

## Validation Rules

- Use **Pydantic v2** `BaseModel` for all request/response
- Always set `response_model` on POST endpoints
- Validate `kategori` against known category codes: `SAMPAH_TERBANG`, `SAMPAH_TIMBUNAN`, `SAMPAH_MASIF`, `SAMPAH_SUNGAI`, `LAIN_LAIN`
- Validate `status` transitions (see status flow above)
- Validate coordinates are within valid lat/lng ranges

## Security Rules

- Never log `request.body()` or headers with auth tokens
- Validate `Content-Type` on file uploads (image/*)
- Admin-only routes require `X-Admin-Key`
- Sanitize `deskripsi` before storing (no HTML injection)
- Validate coordinate bounds: lat ∈ [-90, 90], lng ∈ [-180, 180]

## Lint & Format

```bash
ruff check backend/ api/
black backend/ api/
```
Run before every commit.
