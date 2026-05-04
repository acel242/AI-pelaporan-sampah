# Find Skills Rules — Skill Discovery & Installation

Loads when user asks about missing capabilities or extending the agent.

## Skill Reference

Location: `~/.agents/skills/find-skills/SKILL.md`

---

## How to Discover Skills

```bash
# Search the skills registry
npx skills find react
npx skills find testing
npx skills find deployment

# Browse available skills
npx skills list
```

Browse skills at: https://skills.sh/

## When to Search

- User says "how do I do X" where X might have a skill
- User asks "find a skill for X" or "is there a skill for X?"
- User wants a specialized capability (design, testing, deployment)
- User says they wish they had help with a specific domain

## Quality Checklist Before Recommending

1. **Install count** — Prefer 1K+ installs; be cautious under 100
2. **Source reputation** — Official sources (`vercel-labs`, `anthropic`) more trustworthy
3. **GitHub stars** — Check the source repo; <100 stars is risky

## Installing a Skill

```bash
# Install globally
npx skills add owner/repo@skill-name -g -y

# Update all skills
npx skills update
```

## Skills Currently Installed for This Project

| Skill | Used For |
|-------|---------|
| `python-backend` | FastAPI, SQLAlchemy, auth, caching |
| `github` | PR management, CI, releases |
| `healthcheck` | Host hardening, SSH, firewall |
| `tmux` | Tunnel session management |
| `docx` | Word document generation |
| `find-skills` | Skill discovery |
| `ui-ux-pro-max` | React frontend design |
| `writing-plans` | Proposal/project planning |
