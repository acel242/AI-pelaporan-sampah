# Code Reviewer Agent

Reviews code changes — diffs, file edits, or full files — and returns a structured summary.

## When to Use

- After `git diff` or file edits
- Before merging a PR or completing a feature
- When asked to "review this code"

## How to Run

This is a CLAUDE.md-native agent command. When you invoke it:

```
/claude/code-reviewer [files...]
```

## Review Checklist

### Correctness
- [ ] Logic errors, off-by-one bugs
- [ ] Missing null/None checks
- [ ] Incorrect async/await usage
- [ ] Resource leaks (unclosed files, DB sessions)
- [ ] Race conditions in concurrent code

### Security
- [ ] SQL injection vectors (use parameterized queries)
- [ ] Missing input validation on public endpoints
- [ ] Secrets hardcoded or logged
- [ ] Missing auth/permission checks on sensitive endpoints

### API Design (FastAPI)
- [ ] Proper HTTP status codes (201 created, 204 no content, 400 bad request, 404, 500)
- [ ] Request validation with Pydantic (no `Any` types in schemas)
- [ ] Response model declared on endpoints
- [ ] Idempotent operations for POST/PUT
- [ ] Pagination on list endpoints

### Python Style
- [ ] `ruff check .` passes
- [ ] `black .` formatting applied
- [ ] No wildcard imports (`from x import *`)
- [ ] Type hints on function signatures
- [ ] Docstrings on public functions

### Error Handling
- [ ] Exceptions caught and logged, not silently swallowed
- [ ] Proper HTTP exception raising (FastAPI `HTTPException`)
- [ ] Background tasks handle their own errors
- [ ] Telegram bot: all handlers wrapped in try/except

## Output Format

```
## Code Review: <feature-name>

### Summary
Brief description of what was changed.

### Issues Found
1. **[HIGH]** `file:line` — Description
2. **[MED]** `file:line` — Description
3. **[LOW]** `file:line` — Description

### Recommendations
- List of suggestions that aren't bugs but improve quality

### Files Reviewed
- `backend/api/v1/balita.py`
- `bot/handlers/registry.py`
...

### Verdict
✅ LGTM / ⚠️ Needs Changes / ❌ Blocked
```

## Tips

- Always read the full file context, not just the diff — a diff can look fine in isolation but conflict with surrounding code
- For Telegram bot handlers, pay special attention to state management and callback query handling
- For FastAPI endpoints, verify the database session lifecycle (request → session → response, no session leaks)
