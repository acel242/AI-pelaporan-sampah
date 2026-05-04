# GitHub Rules — Workflow, PR, CI

Loads automatically when working in `.github/**`, or when using `gh` CLI.

## Skill Reference

Use the `github` skill for:
- `gh pr list`, `gh pr view`, `gh pr checks`
- Creating, merging, commenting on PRs
- CI run logs, workflow debugging
- Issue triage and management

Location: `~/.npm-global/lib/node_modules/openclaw/skills/github/SKILL.md`

---

## Branch Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production, auto-deploys to Vercel/Railway |
| `feat/*` | Feature branches: `feat/report-photos`, `feat/admin-dashboard` |
| `fix/*` | Bug fixes: `fix/status-transition`, `fix/geocoding` |

- **Never commit directly to `main`**
- Delete branches after merge

## Commit Conventions

```
feat: add report photo upload endpoint
fix: correct status transition validation for DITUTUP
docs: update API docs for hotspot endpoint
chore: upgrade fastapi to 0.115
```

## PR Checklist Before Opening

- [ ] `ruff check . && black .` passes
- [ ] Tests added/updated for new endpoints
- [ ] API docs updated if endpoint shape changed
- [ ] `CLAUDE.md` updated if behavior changed
- [ ] No secrets or credentials in diff
- [ ] Image storage path validated for new file endpoints

## CI Pipeline

On every PR:
1. `ruff check .` — lint
2. `black --check .` — format check
3. `pytest tests/` — unit tests (if tests exist)

On merge to `main`:
1. CI must pass
2. Backend auto-deploys to Vercel
3. Bot deploys to Railway

## Deployment

```bash
# Full deploy (backend + bot)
bash deploy.sh

# Step by step:
cd backend && vercel --prod    # Deploy API as serverless
python bot/main.py             # Run bot on Railway

# Test webhooks locally
bash start-tunnel.sh
```

## Using `gh` CLI

```bash
# Check CI status for current PR
gh pr checks

# View PR details
gh pr view 55 --repo owner/repo --json title,state,additions,deletions

# Create PR
gh pr create --title "feat: add report photos" --body "Description"

# Merge PR (squash)
gh pr merge 55 --squash --repo owner/repo

# View failed workflow logs
gh run view <run-id> --log-failed
```
