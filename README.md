# AI Pelaporan Sampah - EcoLapor

Sistem AI agent untuk automasi pelaporan sampah di Manado, Sulawesi Utara.

## Arsitektur

```
[Telegram] → [GoBcaEnv Agent] → [SQLite Database]
                    ↓
            [OpenAI LLM + Function Calling]
```

## Struktur Proyek

```
AI-pelaporan-sampah/
├── bot/                    # Telegram bot + agent
│   ├── main.py            # Entry point, handlers
│   ├── agent.py           # LLM agent + tool definitions
│   ├── tools.py           # Tool implementations
│   ├── database.py        # SQLite operations
│   └── .env.example       # Environment template
├── pelaporan-sampah/       # React frontend (existing)
│   └── src/
│       ├── pages/
│       │   ├── Warga.jsx  # Warga form
│       │   ├── Admin.jsx  # Admin dashboard
│       │   └── Login.jsx  # Login page
│       └── App.jsx
├── requirements.txt        # Python dependencies
└── README.md
```

## Quick Start

### 1. Setup Telegram Bot

1. Buka @BotFather di Telegram
2. Ketik `/newbot`
3. Ikuti instruksi, copy bot token

### 2. Setup Environment

```bash
cd bot
cp .env.example .env
# Edit .env:
#   TELEGRAM_BOT_TOKEN=your_token
#   OPENAI_API_KEY=your_key
```

### 3. Run

```bash
pip install -r requirements.txt
python bot/main.py
```

## Fitur

### Untuk Warga
- 📝 Submit laporan sampah via chat
- 📋 Cek status laporan sendiri

### Untuk Admin
- 📊 Dashboard semua laporan
- 🔄 Update status laporan (Menunggu → Selesai)

## Teknologi

- **Python 3.11+**
- **python-telegram-bot** - Telegram API
- **OpenAI API** - LLM with function calling
- **SQLite** - Database (via aiosqlite)
- **FastAPI** - (备选, untuk API backend)
