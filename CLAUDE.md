# AI-pelaporan-sampah — EcoLapor Waste Reporting System

> Indonesian waste reporting and tracking system (Sistem Pelaporan Sampah) with Telegram bot and FastAPI backend.

## Agent Skills Stack

This project uses OpenClaw agent skills to guide development:

| Skill | When It Applies | Key Patterns |
|-------|----------------|--------------|
| `python-backend` | `backend/**`, `api/**` | FastAPI async routes, SQLAlchemy, admin auth, status transitions |
| `github` | `.github/**`, `gh` commands | PR workflow, branch strategy, CI, Vercel deployment |
| `healthcheck` | Production audits | `openclaw security audit`, host hardening, webhook security |
| `tmux` | `start-tunnel.sh`, tunnel sessions | Cloudflare tunnel, webhook testing |
| `docx` | `docs/**`, `.docx` files | Proposal document generation |
| `find-skills` | Skill discovery | `npx skills find`, install new capabilities |
| `ui-ux-pro-max` | `pelaporan-sampah/**` | React frontend design, hotspot map, design tokens |
| `writing-plans` | `docs/**` proposals | Multi-step proposal/implementation planning |

**Tip:** Rules in `.claude/rules/*.md` load automatically when you work in matching paths. They reference the full skill content for detailed patterns.

## Project Overview

AI-pelaporan-sampah enables citizens to report illegal dumping, uncollected trash, and other waste issues via Telegram. Reports are categorized, geotagged, forwarded to relevant handlers, and tracked until resolution.

- **Waste reports** — photo + location + category, submitted via Telegram bot
- **Category routing** — auto-routes to relevant handler (DLH, RT/RW, cleaning service)
- **Status tracking** — reporter gets updates as status changes
- **Admin dashboard** — view reports, update statuses, generate reports
- **Analytics** — hotspot mapping, response time metrics, volume stats

## Tech Stack

| Layer | Technology |
|-------|------------|
| Bot | Python 3.11+, `python-telegram-bot` v20+ |
| Backend API | Python 3.11+, FastAPI, SQLAlchemy (async) |
| Database | SQLite (`pelaporan.db`) — production: PostgreSQL |
| Deployment | Vercel (serverless functions), Railway (bot) |
| Maps | OpenStreetMap / Nominatim (no API key required) |

## Key Commands

```bash
# Deploy everything (backend + bot as Vercel serverless)
bash deploy.sh

# Start cloudflare tunnel for local webhook testing
bash start-tunnel.sh

# Run bot only (polling mode)
python bot/main.py

# Run backend only
python -m uvicorn backend.main:app --reload --port 8000

# Lint
ruff check .
black .
```

## Directory Structure

```
AI-pelaporan-sampah/
├── bot/                # Telegram bot (python-telegram-bot)
│   ├── handlers/       # Message/callback/query handlers
│   ├── services/       # Report creation, status updates, geocoding
│   ├── keyboards/      # Inline keyboards (category, status)
│   └── main.py         # Entry point
├── backend/            # FastAPI REST API
│   ├── api/            # Route modules (v1/)
│   ├── core/           # Config, security, db session
│   ├── models/         # SQLAlchemy ORM models
│   ├── schemas/        # Pydantic schemas
│   └── main.py
├── data/               # SQLite DB, exports, report images
├── deploy.sh           # Deploy to Vercel
├── start-tunnel.sh     # Start Cloudflare tunnel for webhooks
└── CLAUDE.md           # This file
```

## Environment Variables

```env
# Bot
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_ADMIN_IDS=123456,789012

# Backend
DATABASE_URL=sqlite+aiosqlite:///./data/pelaporan.db
SECRET_KEY=change-me-in-production
ALLOWED_ORIGINS=https://your-app.vercel.app

# Tunnel (local dev only)
TUNNEL_URL=https://your-tunnel.trycloudflare.com

# Storage
IMAGE_STORAGE_PATH=./data/reports
```

## API Endpoints

Base URL: `https://your-app.vercel.app/api/v1` (or `http://localhost:8000/api/v1` locally)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/reports` | List reports (paginated, filterable) |
| POST | `/reports` | Create report (admin/internal) |
| GET | `/reports/{id}` | Get report detail |
| PATCH | `/reports/{id}/status` | Update report status |
| GET | `/reports/stats` | Aggregated statistics |
| GET | `/reports/hotspots` | GeoJSON hotspots for map |
| GET | `/categories` | List waste categories |

## Report Status Flow

```
BARU (new) → DIVERIFIKASI (routed) → DALAM_PROSES (handling) → SELESAI (done) → DITUTUP (closed)
```

## Waste Categories

| Category | Description | Handler |
|----------|-------------|---------|
| SAMPAH_TERBANG | Wind-blown litter | DLH |
| SAMPAH_TIMBUNAN | Dumped waste | DLH + RT |
| SAMPAH_MASIF | Large accumulation | DLH |
| SAMPAH_SUNGAI | River pollution | DLH |
| LAIN_LAIN | Other | RT/RW |

## Database Schema (SQLite)

Main tables: `reports`, `report_updates`, `categories`, `admins`, `handler_stats`

## Development Notes

- Use `start-tunnel.sh` to test webhooks locally — Ngrok/Cloudflare tunnel
- Images stored locally in `data/reports/`; in production use S3/R2
- All report mutations are idempotent — safe to retry on network failure
- Bot polling and webhook can run simultaneously (bot auto-detects mode)

## Deployment

```bash
# Full deploy (Vercel for backend, Railway for bot)
bash deploy.sh

# Or step by step:
cd backend && vercel --prod    # Deploy API as serverless
python bot/main.py             # Run bot on Railway
```
