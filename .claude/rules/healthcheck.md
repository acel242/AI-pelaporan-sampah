# Healthcheck Rules — Production Hardening

Loads when running health audits, security checks, or production readiness reviews.

## Skill Reference

Use the `healthcheck` skill for:
- SSH, firewall, OS updates, cron hardening
- `openclaw security audit --deep`
- `openclaw update status`
- Periodic audit scheduling

Location: `~/.npm-global/lib/node_modules/openclaw/skills/healthcheck/SKILL.md`

---

## Project Production Services

This project runs on:
- **Vercel** — backend API (serverless functions)
- **Railway** — Telegram bot
- **Cloudflare Tunnel** — local webhook testing (`start-tunnel.sh`, `start-proxy.sh`)

## Deployment Scripts

```
deploy.sh          # Full deploy to Vercel + Railway
start-tunnel.sh    # Start Cloudflare tunnel for local webhook testing
start-proxy.sh     # Start proxy server for tunnel
check-url.sh       # Health check script for deployed URL
```

## Pre-Deployment Health Checklist

- [ ] All env vars set in production (no hardcoded secrets)
- [ ] `SECRET_KEY` changed from default / development value
- [ ] `DATABASE_URL` points to production database
- [ ] `ALLOWED_ORIGINS` set to production domains only
- [ ] Telegram bot webhook set to production URL (not local tunnel)
- [ ] `TELEGRAM_ADMIN_IDS` set with real admin user IDs
- [ ] `IMAGE_STORAGE_PATH` points to persistent storage (S3/R2 in prod, not local `./data/reports`)
- [ ] Port 8000 not exposed publicly (serverless = no persistent port)
- [ ] `ruff check . && black .` passes
- [ ] CI/CD pipeline green

## SSH & Server Access

If bot runs on a VPS:

```bash
# Check SSH config
cat /etc/ssh/sshd_config

# Check firewall
sudo ufw status

# Check open ports
ss -ltnup

# Check failed login attempts
journalctl --failed | grep sshd
```

**Minimum hardening (see `healthcheck` skill):**
- Key-only SSH authentication
- `ufw` deny-by-default inbound
- Automatic security updates

## Image Storage

Production stores report images in cloud storage (S3/R2), not local filesystem:

```python
# Production: use boto3 or cloudflare-r2
import boto3
s3_client.put_object(Bucket=BUCKET, Key=key, Body=image_bytes)

# Development: local filesystem
IMAGE_STORAGE_PATH=./data/reports  # from .env
```

## Log Locations

```
tunnel.log         # Cloudflare tunnel logs
bot logs           # Via Railway dashboard
backend logs       # Via Vercel dashboard
```

## Bot Production Checklist

- [ ] Bot uses webhook mode in production (not polling)
- [ ] Webhook verified at `https://api.telegram.org/bot<token>/setWebhook`
- [ ] `watchdog.sh` or Railway health checks monitor the bot
- [ ] `TELEGRAM_BOT_TOKEN` stored as Railway environment variable
- [ ] Admin IDs configured for alert routing

## Periodic Audit Command

```bash
openclaw security audit --deep
openclaw update status
```
