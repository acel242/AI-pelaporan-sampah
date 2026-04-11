import aiosqlite
from datetime import datetime
from typing import Optional

DATABASE_PATH = "pelaporan.db"

async def init_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                role TEXT DEFAULT 'warga',
                created_at TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS laporan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                nama TEXT,
                lokasi TEXT,
                deskripsi TEXT,
                status TEXT DEFAULT 'Menunggu',
                tanggal TEXT,
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        await db.commit()

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

async def submit_report(user_id: int, nama: str, lokasi: str, deskripsi: str) -> dict:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        tanggal = datetime.now().strftime("%d/%m/%Y")
        created_at = datetime.now().isoformat()
        cursor = await db.execute(
            """INSERT INTO laporan (user_id, nama, lokasi, deskripsi, status, tanggal, created_at)
               VALUES (?, ?, ?, ?, 'Menunggu', ?, ?)""",
            (user_id, nama, lokasi, deskripsi, tanggal, created_at)
        )
        await db.commit()
        return {
            "id": cursor.lastrowid,
            "nama": nama,
            "lokasi": lokasi,
            "deskripsi": deskripsi,
            "status": "Menunggu",
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

async def update_report_status(report_id: int, status: str) -> bool:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "UPDATE laporan SET status = ? WHERE id = ?",
            (status, report_id)
        )
        await db.commit()
        return cursor.rowcount > 0
