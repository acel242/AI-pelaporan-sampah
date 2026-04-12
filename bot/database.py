import aiosqlite
from datetime import datetime
from typing import Optional

DATABASE_PATH = "pelaporan.db"

async def init_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Users table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                role TEXT DEFAULT 'warga',
                created_at TEXT
            )
        """)
        
        # Laporan table with priority and notes
        await db.execute("""
            CREATE TABLE IF NOT EXISTS laporan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                nama TEXT,
                lokasi TEXT,
                deskripsi TEXT,
                status TEXT DEFAULT 'Menunggu',
                prioritas TEXT DEFAULT 'Sedang',
                catatan TEXT,
                tanggal TEXT,
                updated_at TEXT,
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Migration: add columns if they don't exist
        try:
            await db.execute("ALTER TABLE laporan ADD COLUMN prioritas TEXT DEFAULT 'Sedang'")
        except aiosqlite.OperationalError:
            pass  # Column already exists
        
        try:
            await db.execute("ALTER TABLE laporan ADD COLUMN catatan TEXT")
        except aiosqlite.OperationalError:
            pass  # Column already exists
        
        try:
            await db.execute("ALTER TABLE laporan ADD COLUMN updated_at TEXT")
        except aiosqlite.OperationalError:
            pass  # Column already exists
        
        await db.commit()

# ─────────────────────────────────────────────
# User Operations
# ─────────────────────────────────────────────
async def get_user(user_id: int) -> Optional[dict]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def create_user(user_id: int, username: str, role: str = "warga"):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, role, created_at) VALUES (?, ?, ?, ?)",
            (user_id, username, role, datetime.now().isoformat())
        )
        await db.commit()

async def get_all_users() -> list[dict]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users ORDER BY created_at DESC") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

# ─────────────────────────────────────────────
# Report Operations
# ─────────────────────────────────────────────
async def submit_report(user_id: int, nama: str, lokasi: str, deskripsi: str) -> dict:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        now = datetime.now()
        tanggal = now.strftime("%d/%m/%Y")
        created_at = now.isoformat()
        
        cursor = await db.execute(
            """INSERT INTO laporan (user_id, nama, lokasi, deskripsi, status, prioritas, tanggal, created_at)
               VALUES (?, ?, ?, ?, 'Menunggu', 'Sedang', ?, ?)""",
            (user_id, nama, lokasi, deskripsi, tanggal, created_at)
        )
        await db.commit()
        
        return {
            "id": cursor.lastrowid,
            "nama": nama,
            "lokasi": lokasi,
            "deskripsi": deskripsi,
            "status": "Menunggu",
            "prioritas": "Sedang",
            "tanggal": tanggal
        }

async def get_reports(user_id: int) -> list[dict]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM laporan WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def get_all_reports() -> list[dict]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM laporan ORDER BY created_at DESC") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def get_report_by_id(report_id: int) -> Optional[dict]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM laporan WHERE id = ?", (report_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

# ─────────────────────────────────────────────
# Update Operations
# ─────────────────────────────────────────────
async def update_report_status(report_id: int, status: str) -> bool:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        now = datetime.now().isoformat()
        cursor = await db.execute(
            "UPDATE laporan SET status = ?, updated_at = ? WHERE id = ?",
            (status, now, report_id)
        )
        await db.commit()
        return cursor.rowcount > 0

async def update_report_priority(report_id: int, prioritas: str) -> bool:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        now = datetime.now().isoformat()
        cursor = await db.execute(
            "UPDATE laporan SET prioritas = ?, updated_at = ? WHERE id = ?",
            (prioritas, now, report_id)
        )
        await db.commit()
        return cursor.rowcount > 0

async def update_report_note(report_id: int, catatan: str) -> bool:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        now = datetime.now().isoformat()
        cursor = await db.execute(
            "UPDATE laporan SET catatan = ?, updated_at = ? WHERE id = ?",
            (catatan, now, report_id)
        )
        await db.commit()
        return cursor.rowcount > 0

# ─────────────────────────────────────────────
# Statistics
# ─────────────────────────────────────────────
async def get_statistics() -> dict:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # Total counts
        total = await db.execute_fetchone("SELECT COUNT(*) as count FROM laporan")[0]
        
        # By status
        status_rows = await db.execute_fetchall(
            "SELECT status, COUNT(*) as count FROM laporan GROUP BY status"
        )
        by_status = {row[0]: row[1] for row in status_rows}
        
        # By priority
        priority_rows = await db.execute_fetchall(
            "SELECT prioritas, COUNT(*) as count FROM laporan GROUP BY prioritas"
        )
        by_priority = {row[0]: row[1] for row in priority_rows}
        
        return {
            "total": total,
            "by_status": by_status,
            "by_priority": by_priority
        }
