# Tmux Rules — Session & Tunnel Management

Loads when working with `start-tunnel.sh`, `deploy.sh`, or any tmux session management.

## Skill Reference

Use the `tmux` skill for:
- Sending keystrokes to tmux sessions
- Capturing pane output
- Managing multiple sessions

Location: `~/.npm-global/lib/node_modules/openclaw/skills/tmux/SKILL.md`

---

## Tmux Sessions

This project uses tmux for tunnel and dev management:

| Session | Purpose |
|---------|---------|
| `tunnel` | Cloudflare tunnel for webhook testing |
| `backend` | Local backend API (`uvicorn`) |
| `bot` | Local bot polling |

## Key Scripts

```
start-tunnel.sh    # Starts Cloudflare tunnel, outputs public URL
start-proxy.sh     # Secondary proxy server
deploy.sh          # Deploys backend to Vercel
check-url.sh       # Health check for deployed backend
```

## Starting the Tunnel (Webhook Testing)

```bash
# Start tunnel and capture the URL
bash start-tunnel.sh

# Get the public URL from tunnel output
tmux capture-pane -t tunnel -p | grep -E "trycloudflare|cloudflared"

# Set the webhook
curl -F "url=https://your-tunnel.trycloudflare.com/bot$TOKEN" \
  https://api.telegram.org/bot$TOKEN/setWebhook
```

## Tmux Workflow

```bash
# List sessions
tmux list-sessions

# Attach to tunnel session
tmux attach -t tunnel

# Send command
tmux send-keys -t tunnel "bash start-tunnel.sh" Enter

# Capture output
tmux capture-pane -t tunnel -p | tail -20

# Kill stuck session
tmux kill-session -t tunnel
```

## Backend + Bot Development

```bash
# Start backend
tmux new-session -d -s backend
tmux send-keys -t backend "cd /home/ubuntu/AI-pelaporan-sampah && python -m uvicorn backend.main:app --reload --port 8000" Enter

# Start bot polling
tmux new-session -d -s bot
tmux send-keys -t bot "cd /home/ubuntu/AI-pelaporan-sampah && python bot/main.py" Enter
```

## Production Note

In production (Vercel + Railway):
- **No tmux needed** — Vercel handles serverless, Railway handles bot process
- `start-tunnel.sh` is for **local webhook testing only**
- Use Railway's built-in restart policy instead of `watchdog.sh`
