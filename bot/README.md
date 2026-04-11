# GoBcaEnv - EcoLapor Telegram Agent

AI Agent untuk automasi pelaporan sampah di Manado.

## Setup

```bash
cd bot
cp .env.example .env
# Edit .env with your tokens

pip install -r ../requirements.txt
```

## Run

```bash
python main.py
```

## Commands

- `/start` - Start conversation
- `/help` - Show help
- `/all_reports` - (Admin) View all reports
- `/update_status <id> <status>` - (Admin) Update report status

## Environment Variables

| Variable | Description |
|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token from @BotFather |
| `OPENAI_API_KEY` | OpenAI API key |
| `LLM_MODEL` | Model to use (default: gpt-4o-mini) |
| `ADMIN_USER_IDS` | Comma-separated admin Telegram IDs |
