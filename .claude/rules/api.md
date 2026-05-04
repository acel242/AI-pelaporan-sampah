# API Rules — FastAPI Backend

Loads automatically when working in `backend/**` or `api/**` paths.

## Skill Reference

Use the `python-backend` skill for detailed patterns on:
- FastAPI project structure, async routes, dependency injection
- SQLAlchemy async, transactions, eager loading, migrations
- JWT/OAuth2, password hashing, CORS, API key security
- Upstash Redis caching and rate limiting
- Pydantic v2 validation patterns

Location: `~/.agents/skills/python-backend/SKILL.md`

---

## REST Conventions

### URL Structure

```
/api/v1/{resource}
/api/v1/{resource}/{id}
/api/v1/{resource}/{id}/sub-resource
```

- **kebab-case** for paths
- **plural** resource names
- **No verbs** in URLs — use HTTP methods

### HTTP Status Codes

| Code | Use |
|------|-----|
| 200 | Successful GET, PATCH |
| 201 | Successful POST |
| 204 | Successful DELETE |
| 400 | Validation error |
| 401 | Not authenticated |
| 403 | Not authorized |
| 404 | Resource not found |
| 409 | Conflict / invalid state transition |
| 422 | Unprocessable entity |
| 500 | Internal server error |

### Pagination

```python
from fastapi import Query
from sqlalchemy import func, select

@router.get("/reports")
async def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(ReportModel).offset(skip).limit(limit))
    total = await db.execute(select(func.count(ReportModel.id)))
    return {"data": list(result.scalars().all()), "total": total.scalar(), "skip": skip, "limit": limit}
```

### Error Response Format (RFC 7807)

```python
raise HTTPException(
    status_code=404,
    detail={
        "type": "https://ai-pelaporan.app/errors/not-found",
        "title": "Resource not found",
        "detail": "Report with id 123 does not exist",
        "instance": "/api/v1/reports/123",
    }
)
```

## Pydantic Schemas

```python
from pydantic import BaseModel, Field

class ReportCreate(BaseModel):
    kategori: str = Field(..., description="Waste category code")
    deskripsi: str = Field(..., min_length=1, max_length=500)
    lokasi: str = Field(..., min_length=1, max_length=255)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)

class ReportResponse(BaseModel):
    id: int
    kategori: str
    status: str
    deskripsi: str
    lokasi: str
    latitude: float | None
    longitude: float | None
    created_at: datetime
    model_config = {"from_attributes": True}
```

## Status Transition Validation

Valid transitions:
```
BARU → DIVERIFIKASI → DALAM_PROSES → SELESAI → DITUTUP
```

Reject invalid transitions with HTTP 409.

## Admin Auth

```python
async def get_admin_key(x_admin_key: str = Header(...)):
    if x_admin_key != settings.SECRET_KEY:
        raise HTTPException(401, "Invalid admin key")
    return x_admin_key
```

## Async DB

All DB operations must be `async` — use `await db.execute()` not `db.execute()`.

## Security Rules

- Never log `request.body()` or auth headers
- Validate coordinates: lat ∈ [-90, 90], lng ∈ [-180, 180]
- Sanitize `deskripsi` (no HTML injection)
- Validate `kategori` against known codes
- Validate status transitions

## Key Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | None | Health check |
| GET | `/reports` | None | List (paginated) |
| POST | `/reports` | Admin | Create report |
| GET | `/reports/{id}` | None | Get detail |
| PATCH | `/reports/{id}/status` | Admin | Update status |
| GET | `/reports/stats` | None | Aggregated stats |
| GET | `/reports/hotspots` | None | GeoJSON for map |
| GET | `/categories` | None | List categories |

## Lint & Format

```bash
ruff check backend/ api/
black backend/ api/
```
Run before every commit.
