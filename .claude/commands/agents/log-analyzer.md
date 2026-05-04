# Log Analyzer Agent

Parses error logs, crash reports, and tracebacks to identify root causes.

## When to Use

- Application crashed or returned 500 errors
- `watchdog.sh` reported a service restart
- Investigating `bot.log`, `backend.log`, `uvicorn.log`

## How to Run

```
/claude/log-analyzer [log_file]
```

Defaults to scanning `*.log` in the project root.

## What to Look For

### Python Exceptions
```
Traceback (most recent call last):
  File "backend/main.py", line 45, in get_balita
    db_session.query(Balita).get(id)
AttributeError: 'Session' object has no attribute 'query'
```
→ Wrong SQLAlchemy session usage (async vs sync)

### Telegram Errors
```
 telegram.error.BadRequest: Message not found
 telegram.error.NetworkError: Connection refused
 telegram.error.RetryAfter: Flood control exceeded
```
→ Bot API misuse, network issues, rate limiting

### FastAPI Errors
```
uvicorn.error: OSError: [Errno 98] Address already in use
fastapi.exception: Request validation failed
```
→ Port conflict, Pydantic validation failure

### Database Errors
```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) database is locked
sqlalchemy.exc.IntegrityError: UNIQUE constraint failed
```
→ Concurrency issues, duplicate key violations

## Output Format

```
## Log Analysis: <logfile>

### Error Summary
Total errors: N | Errors by type:
- OperationalError: 3
- ValidationError: 1

### Root Causes Identified
1. **Database locked** — async SQLite writes from multiple workers
   - Occurred: 3 times, first at 14:32, last at 14:58
   - Files affected: backend/api/v1/imunisasi.py
   - Fix: Use `check_same_thread=False` or switch to PostgreSQL

2. **Missing field** — Pydantic validation failed on `ibu_hamil` schema
   - Request: POST /api/v1/ibu-hamil
   - Missing field: `tanggal_last_anc`
   - Fix: Make field optional or set default

### Suggested Actions
1. Update `backend/core/database.py` to use WAL mode for SQLite
2. Add default value for `tanggal_last_anc` in schema
3. Add retry logic for database locks
```
