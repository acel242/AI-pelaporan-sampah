import aiosqlite
import os
from datetime import datetime
from typing import Optional

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "pelaporan.db")

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
        
        # Petugas table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS petugas (
                telegram_id INTEGER PRIMARY KEY,
                nama TEXT,
                registered_at TEXT
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
        
        # Foto bukti table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS foto_bukti (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                laporan_id INTEGER,
                foto_url TEXT,
                uploaded_at TEXT,
                FOREIGN KEY (laporan_id) REFERENCES laporan(id)
            )
        """)
        
        # Migration: add columns if they don't exist (newer columns not in CREATE TABLE)
        for col in ["foto", "jenis_sampah", "kategori", "sub_kategori", "latitude", "longitude"]:
            try:
                await db.execute(f"ALTER TABLE laporan ADD COLUMN {col} TEXT")
            except aiosqlite.OperationalError:
                pass  # Column already exists
        
        # Migration: set kategori='Sampah' for existing rows
        try:
            await db.execute("UPDATE laporan SET kategori = 'Sampah' WHERE kategori IS NULL")
            await db.commit()
        except Exception:
            pass
        
        # Conversation state for password gate
        await db.execute("""
            CREATE TABLE IF NOT EXISTS conv_state (
                user_id INTEGER PRIMARY KEY,
                state TEXT,
                updated_at TEXT
            )
        """)
        
        await db.commit()

# ─────────────────────────────────────────────
# Petugas Operations
# ─────────────────────────────────────────────
async def register_petugas(telegram_id: int, nama: str) -> dict:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        now = datetime.now().isoformat()
        await db.execute(
            """INSERT OR REPLACE INTO petugas (telegram_id, nama, registered_at)
               VALUES (?, ?, ?)""",
            (telegram_id, nama, now)
        )
        await db.commit()
        return {"telegram_id": telegram_id, "nama": nama, "registered_at": now}

async def get_petugas(telegram_id: int) -> Optional[dict]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM petugas WHERE telegram_id = ?", (telegram_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def is_petugas(telegram_id: int) -> bool:
    petugas = await get_petugas(telegram_id)
    return petugas is not None

# ─────────────────────────────────────────────
# Conversation State (for password gate)
# ─────────────────────────────────────────────
async def get_conv_state(user_id: int) -> Optional[str]:
    """Get current conversation state for user."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT state FROM conv_state WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def set_conv_state(user_id: int, state: str) -> None:
    """Set conversation state for user."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        now = datetime.now().isoformat()
        await db.execute(
            "INSERT OR REPLACE INTO conv_state (user_id, state, updated_at) VALUES (?, ?, ?)",
            (user_id, state, now)
        )
        await db.commit()

async def clear_conv_state(user_id: int) -> None:
    """Clear conversation state."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("DELETE FROM conv_state WHERE user_id = ?", (user_id,))
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

async def check_duplicate_report(user_id: int, lokasi: str, jam_window: int = 24) -> Optional[dict]:
    """Check if user has submitted a similar report at the same location in the last N hours.
    Returns the existing report if found, None otherwise."""
    from datetime import timedelta
    cutoff = (datetime.now() - timedelta(hours=jam_window)).isoformat()

    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT * FROM laporan
               WHERE user_id = ?
                 AND LOWER(lokasi) = LOWER(?)
                 AND created_at > ?
               ORDER BY created_at DESC
               LIMIT 1""",
            (user_id, lokasi, cutoff)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def submit_report_with_photos(
    user_id: int, nama: str, lokasi: str, deskripsi: str,
    foto_urls: list[str] = None,
    kategori: str = "Sampah", sub_kategori: str = None,
    latitude: str = None, longitude: str = None,
    jenis_sampah: str = "Anorganik"
) -> dict:
    """Submit a report and optionally attach photos, all in one transaction."""
    from datetime import datetime

    async with aiosqlite.connect(DATABASE_PATH) as db:
        now = datetime.now()
        tanggal = now.strftime("%d/%m/%Y")
        created_at = now.isoformat()

        cursor = await db.execute(
            """INSERT INTO laporan (
                   user_id, nama, lokasi, deskripsi, status, prioritas,
                   tanggal, created_at, kategori, sub_kategori,
                   latitude, longitude, jenis_sampah
               ) VALUES (?, ?, ?, ?, 'Menunggu', 'Sedang', ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, nama, lokasi, deskripsi, tanggal, created_at,
             kategori, sub_kategori, latitude, longitude, jenis_sampah)
        )
        laporan_id = cursor.lastrowid

        if foto_urls:
            for foto_url in foto_urls:
                await db.execute(
                    """INSERT INTO foto_bukti (laporan_id, foto_url, uploaded_at)
                       VALUES (?, ?, ?)""",
                    (laporan_id, foto_url, now.isoformat())
                )

        await db.commit()

        return {
            "id": laporan_id,
            "nama": nama,
            "lokasi": lokasi,
            "deskripsi": deskripsi,
            "status": "Menunggu",
            "prioritas": "Sedang",
            "tanggal": tanggal,
            "kategori": kategori,
            "sub_kategori": sub_kategori,
            "latitude": latitude,
            "longitude": longitude,
            "jenis_sampah": jenis_sampah,
            "foto_count": len(foto_urls) if foto_urls else 0,
        }


async def get_all_users() -> list[dict]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users ORDER BY created_at DESC") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

# ─────────────────────────────────────────────
# Report Operations
# ─────────────────────────────────────────────
async def submit_report(user_id: int, nama: str, lokasi: str, deskripsi: str, kategori: str = "Sampah", sub_kategori: str = None, latitude: str = None, longitude: str = None, jenis_sampah: str = "Anorganik") -> dict:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        now = datetime.now()
        tanggal = now.strftime("%d/%m/%Y")
        created_at = now.isoformat()
        
        cursor = await db.execute(
            """INSERT INTO laporan (user_id, nama, lokasi, deskripsi, status, prioritas, tanggal, created_at, kategori, sub_kategori, latitude, longitude, jenis_sampah)
               VALUES (?, ?, ?, ?, 'Menunggu', 'Sedang', ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, nama, lokasi, deskripsi, tanggal, created_at, kategori, sub_kategori, latitude, longitude, jenis_sampah)
        )
        await db.commit()
        
        return {
            "id": cursor.lastrowid,
            "nama": nama,
            "lokasi": lokasi,
            "deskripsi": deskripsi,
            "status": "Menunggu",
            "prioritas": "Sedang",
            "tanggal": tanggal,
            "kategori": kategori,
            "sub_kategori": sub_kategori,
            "latitude": latitude,
            "longitude": longitude,
            "jenis_sampah": jenis_sampah,
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

async def get_pending_reports() -> list[dict]:
    """Get all pending reports sorted by priority (Tinggi first) then by oldest created_at.
    Auto-escalates reports > 3 days old to Tinggi priority."""
    
    # Auto-escalate old reports
    await escalate_old_reports()
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        async with db.execute(
            """SELECT * FROM laporan WHERE status = 'Menunggu' 
               ORDER BY 
                   CASE prioritas 
                       WHEN 'Tinggi' THEN 1 
                       WHEN 'Sedang' THEN 2 
                       WHEN 'Rendah' THEN 3 
                   END,
                   created_at ASC"""
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def escalate_old_reports(days: int = 3) -> int:
    """Auto-escalate reports that have been 'Menunggu' for more than X days to Tinggi priority.
    Returns number of reports escalated."""
    from datetime import timedelta
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            """UPDATE laporan 
               SET prioritas = 'Tinggi', updated_at = ?
               WHERE status = 'Menunggu' 
                 AND prioritas != 'Tinggi'
                 AND created_at < ?""",
            (datetime.now().isoformat(), cutoff)
        )
        await db.commit()
        return cursor.rowcount

# ─────────────────────────────────────────────
# Foto Bukti Operations
# ─────────────────────────────────────────────
async def add_foto_bukti(laporan_id: int, foto_url: str) -> dict:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        now = datetime.now().isoformat()
        cursor = await db.execute(
            """INSERT INTO foto_bukti (laporan_id, foto_url, uploaded_at)
               VALUES (?, ?, ?)""",
            (laporan_id, foto_url, now)
        )
        await db.commit()
        return {"id": cursor.lastrowid, "laporan_id": laporan_id, "foto_url": foto_url, "uploaded_at": now}

async def get_foto_bukti(laporan_id: int) -> list[dict]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM foto_bukti WHERE laporan_id = ? ORDER BY uploaded_at ASC",
            (laporan_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

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

async def update_report_foto(report_id: int, foto_url: str) -> bool:
    """Update the main foto field of a laporan with the bukti photo."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        now = datetime.now().isoformat()
        cursor = await db.execute(
            "UPDATE laporan SET foto = ?, updated_at = ? WHERE id = ?",
            (foto_url, now, report_id)
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
        
        cursor = await db.execute("SELECT COUNT(*) FROM laporan")
        total = (await cursor.fetchone())[0]

        cursor = await db.execute("SELECT status, COUNT(*) FROM laporan GROUP BY status")
        status_rows = await cursor.fetchall()
        by_status = {row[0]: row[1] for row in status_rows}

        cursor = await db.execute("SELECT prioritas, COUNT(*) FROM laporan GROUP BY prioritas")
        priority_rows = await cursor.fetchall()
        by_priority = {row[0]: row[1] for row in priority_rows}
        
        return {
            "total": total,
            "by_status": by_status,
            "by_priority": by_priority
        }

# ─── Conversation Memory Table ────────────────────────────────────────────────

async def init_memory_db():
    """Create memory table for learned facts."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS conv_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                keyword TEXT,
                fact TEXT,
                created_at TEXT
            )
        """)
        await db.commit()

async def add_conv_memory(user_id: int, keyword: str, fact: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT INTO conv_memory (user_id, keyword, fact, created_at) VALUES (?, ?, ?, ?)",
            (user_id, keyword, fact, datetime.now().isoformat())
        )
        await db.commit()

async def search_conv_memory(user_id: int, query: str) -> list:
    """Search memory for relevant facts."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        rows = await db.execute(
            """SELECT keyword, fact FROM conv_memory
               WHERE user_id = ? AND (keyword LIKE ? OR fact LIKE ?)""",
            (user_id, f"%{query}%", f"%{query}%")
        )
        return await rows.fetchall()

async def search_all_memory(query: str) -> list:
    """Search all memory (admin)."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        rows = await db.execute(
            """SELECT user_id, keyword, fact FROM conv_memory
               WHERE keyword LIKE ? OR fact LIKE ?""",
            (f"%{query}%", f"%{query}%")
        )
        return await rows.fetchall()

# Initialize on import
import asyncio
try:
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.create_task(init_memory_db())
    else:
        loop.run_until_complete(init_memory_db())
except Exception:
    pass
