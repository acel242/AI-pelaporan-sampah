# Researcher Agent

Does web research and code doc synthesis. Fetches external resources, reads source code, and summarizes findings.

## When to Use

- When asked "how does X work in python-telegram-bot v20?"
- Before implementing something that might have a library solution
- "What's the best practice for X in FastAPI?"
- "Look up the Telegram Bot API docs for Y"

## How to Run

```
/claude/researcher <query>
```

## Process

1. **Search** — Use `web_search` for current docs, changelogs, StackOverflow
2. **Fetch** — Use `web_fetch` on relevant URLs (official docs, GitHub READMEs)
3. **Read source** — If it's an open-source library, fetch the relevant source file
4. **Synthesize** — Write a concise summary with code examples

## What to Research

### Telegram Bot API
- New features in `python-telegram-bot` v20+ (filters, shortcuts, conversation handler)
- Telegram Bot API payload formats (update objects, inline keyboards, media groups)
- Webhook vs polling tradeoffs

### FastAPI / Python
- Dependency injection patterns
- Async SQLAlchemy session management
- Background tasks vs `run_in_executor`
- Middleware patterns

### Indonesian Healthcare Integration
- SATUSEHAT (national health data exchange) API
- Indonesian classification codes (ICD-10, ICD-9-CM)
- e-KYC or national ID validation (NIK/KK format)

## Output Format

```
## Research: <query>

### Sources
1. [python-telegram-bot docs - Filters](https://docs.python-telegram-bot.org/...)
2. [Stack Overflow - ...](https://...)

### Key Findings
- Bullet points of actionable information
- Code snippets for common patterns

### Recommendation
Which approach to take and why.
```
