# Waste Report Skill — AI-pelaporan-sampah

Instructions for building, running, linting, and deploying the waste reporting system.

## Project Structure

```
AI-pelaporan-sampah/
├── bot/                # python-telegram-bot v20+ — Telegram bot
│   ├── handlers/       # Update handlers (message, callback, inline query)
│   ├── services/       # Business logic (report creation, geocoding)
│   ├── keyboards/      # Inline keyboard builders
│   └── main.py         # Entry point
├── backend/            # FastAPI — REST API
│   ├── api/v1/         # Route handlers
│   ├── core/           # Config, db, security
│   ├── models/         # SQLAlchemy ORM
│   ├── schemas/        # Pydantic schemas
│   └── main.py         # App factory
├── data/               # SQLite DB (pelaporan.db), report images
├── deploy.sh           # Deploy to Vercel
└── start-tunnel.sh     # Cloudflare tunnel for webhook testing
```

## Commands

### Run Everything

```bash
# Backend + Bot (polling)
python -m uvicorn backend.main:app --reload --port 8000 &
python bot/main.py
```

### Run Components Individually

```bash
# Bot only (polling)
python bot/main.py

# Backend only
python -m uvicorn backend.main:app --reload --port 8000

# Local webhook testing
bash start-tunnel.sh
```

### Lint & Format

```bash
# Python
ruff check .
black .
```

### Deploy

```bash
# Deploy to Vercel (backend as serverless functions)
cd backend && vercel --prod

# Deploy bot to Railway
railway up

# Or use the deploy script
bash deploy.sh
```

## Bot Development

### Report Flow

```
User sends photo/location → Bot asks for category → User selects category → Report created → Admin notified
```

### Adding a New Category

1. Add to `bot/keyboards/categories.py`
2. Add handler in `bot/handlers/report.py`
3. Update `backend/models/report.py` if new fields needed

```python
# bot/keyboards/categories.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

WASTE_CATEGORIES = [
    ("SAMPAH_TERBANG", "🌀 Sampah Terbangkan"),
    ("SAMPAH_TIMBUNAN", "🗑️ Timbunan Sampah"),
    ("SAMPAH_MASIF", "📦 Sampah Masif"),
    ("SAMPAH_SUNGAI", "🌊 Pencemaran Sungai"),
    ("LAIN_LAIN", "❓ Lainnya"),
]

def category_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(label, callback_data=f"cat:{code}")]
        for code, label in WASTE_CATEGORIES
    ]
    return InlineKeyboardMarkup(keyboard)
```

### Geocoding

Uses Nominatim (OpenStreetMap) — no API key needed:

```python
# bot/services/geocode.py
from geopy.geocoders import Nominatim

async def get_location_name(lat: float, lon: float) -> str:
    locator = Nominatim(user_agent="AI-pelaporan-sampah")
    location = locator.reverse(f"{lat}, {lon}", language="id")
    return location.address if location else f"{lat},{lon}"
```

### Handling Photo + Location

```python
async def handle_report_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]  # highest resolution
    file = await context.bot.get_file(photo.file_id)
    local_path = f"data/reports/{photo.file_id}.jpg"
    await file.download_to_drive(local_path)

    # Store in user_data temporarily
    context.user_data["pending_report"] = {"photo_path": local_path}
    await update.message.reply_text(
        "📍 Kirim lokasi anda (share location):",
        reply_markup=location_keyboard()
    )
```

### Webhook Mode (Production)

```python
# bot/main.py
app = ApplicationBuilder().token(TOKEN).build()
app.run_webhook(
    listen="0.0.0.0",
    port=8443,
    url_path=TOKEN,
    webhook_url=f"{BASE_URL}/{TOKEN}",
)
```

## Backend Development

### Adding an Endpoint

1. Create schema in `backend/schemas/report.py`
2. Add route in `backend/api/v1/reports.py`
3. Register router in `backend/main.py`

```python
# backend/schemas/report.py
from pydantic import BaseModel
from datetime import datetime

class ReportCreate(BaseModel):
    category: str
    latitude: float
    longitude: float
    description: str | None = None

class ReportResponse(ReportCreate):
    id: int
    status: str
    created_at: datetime
    class Config:
        from_attributes = True
```

### Status Update Webhook (for external integrators)

```python
@router.patch("/{report_id}/status")
async def update_status(
    report_id: int,
    status: str,
    admin_key: str = Header(..., alias="X-Admin-Key"),
    db: Session = Depends(get_db)
):
    if admin_key != settings.ADMIN_KEY:
        raise HTTPException(403, "Invalid admin key")
    # ... update logic
```

## Deployment Notes

### Vercel (Backend)

`vercel.json` at backend root:

```json
{
  "builds": [{ "src": "main.py", "use": "@vercel/python" }],
  "routes": [{ "src": "/(.*)", "dest": "main.py" }]
}
```

### Railway (Bot)

Set `TELEGRAM_BOT_TOKEN` and `DATABASE_URL` in Railway environment variables.

## Environment Variables

```bash
# bot/.env
TELEGRAM_BOT_TOKEN=...
TELEGRAM_ADMIN_IDS=123456,789012

# backend/.env
DATABASE_URL=sqlite+aiosqlite:///./data/pelaporan.db
SECRET_KEY=...
ALLOWED_ORIGINS=https://your-app.vercel.app

# Tunnel (local dev)
TUNNEL_URL=https://your-tunnel.trycloudflare.com
```
