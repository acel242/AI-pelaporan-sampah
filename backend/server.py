"""
EcoLapor Backend API - Flask Server
Connects frontend to SQLite database (shared with bot)
"""
import os
import sqlite3
import httpx
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, g
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "..", "bot", "pelaporan.db")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "REDACTED")

def get_db():
    """Get database connection for current request context."""
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = sqlite3.connect(DATABASE_PATH)
        db.row_factory = sqlite3.Row
    return db


def auto_escalate_old_reports(db, days=3):
    """Auto-escalate reports > N days old to Tinggi."""
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    now = datetime.now().isoformat()
    cursor = db.execute(
        """UPDATE laporan
           SET prioritas = 'Tinggi', updated_at = ?
           WHERE status = 'Menunggu'
             AND prioritas != 'Tinggi'
             AND created_at < ?""",
        (now, cutoff)
    )
    db.commit()
    return cursor.rowcount


def assign_priority_ai(nama: str, lokasi: str, deskripsi: str) -> str:
    """Use AI to assign priority based on report content."""
    prompt = f"""Analisis laporan sampah berikut dan tentukan prioritas respons:

Nama pelapor: {nama}
Lokasi: {lokasi}
Deskripsi: {deskripsi}

Tentukan prioritas jadi SATU kata saja: Rendah, Sedang, atau Tinggi.

Aturan:
- "Rendah" = sampah sedikit, tidak blocking, tidak bau, tidak berbahaya
- "Sedang" = tumpukan sampah biasa, ada sedikit bau atau lalat
- "Tinggi" = sampah dalam jumlah besar, blocking jalan/fasilitas umum, bau menyengat, ada bahan berbahaya, atau lokasi sensitif (sekolah, rs, pasar)

Jawaban hanya 1 kata: Rendah, Sedang, atau Tinggi."""

    try:
        with httpx.Client(timeout=15) as client:
            response = client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 5,
                    "temperature": 0
                }
            )
            result = response.json()
            answer = result.get("choices", [{}])[0].get("message", {}).get("content", "Sedang").strip()

            if "Tinggi" in answer:
                return "Tinggi"
            elif "Rendah" in answer:
                return "Rendah"
            else:
                return "Sedang"
    except Exception as e:
        print(f"[AI Priority] Error: {e}")
        return "Sedang"


def close_db(e=None):
    """Close database connection."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_backend_db():
    """Initialize database if it doesn't exist."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS laporan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            nama TEXT,
            lokasi TEXT,
            deskripsi TEXT,
            foto TEXT,
            status TEXT DEFAULT 'Menunggu',
            prioritas TEXT DEFAULT 'Sedang',
            catatan TEXT,
            tanggal TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS foto_bukti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            laporan_id INTEGER,
            foto_url TEXT,
            uploaded_at TEXT
        )
    """)
    conn.commit()
    conn.close()

# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

def create_routes(app):

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

    @app.route("/api/laporan", methods=["POST"])
    def create_laporan():
        """Submit a new waste report."""
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        nama = data.get("nama")
        lokasi = data.get("lokasi")
        deskripsi = data.get("deskripsi")
        user_id = data.get("user_id", 0)
        foto = data.get("foto")

        if not all([nama, lokasi, deskripsi]):
            return jsonify({"error": "Missing required fields"}), 400

        # AI assigns priority based on content
        prioritas = assign_priority_ai(nama, lokasi, deskripsi)

        now = datetime.now()
        tanggal = now.strftime("%d/%m/%Y")
        created_at = now.isoformat()

        db = get_db()
        cursor = db.execute(
            """INSERT INTO laporan (user_id, nama, lokasi, deskripsi, foto, status, prioritas, tanggal, created_at)
               VALUES (?, ?, ?, ?, ?, 'Menunggu', ?, ?, ?)""",
            (user_id, nama, lokasi, deskripsi, foto, prioritas, tanggal, created_at)
        )
        db.commit()

        return jsonify({
            "success": True,
            "id": cursor.lastrowid,
            "status": "Menunggu",
            "prioritas": prioritas,
            "tanggal": tanggal
        }), 201

    @app.route("/api/laporan", methods=["GET"])
    def get_laporan():
        """Get reports."""
        user_id = request.args.get("user_id", type=int)
        status = request.args.get("status")
        prioritas = request.args.get("prioritas")
        search = request.args.get("search")

        db = get_db()

        # Auto-escalate old pending reports
        auto_escalate_old_reports(db)

        query = "SELECT * FROM laporan WHERE 1=1"
        params = []

        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)

        if status and status != "Semua":
            query += " AND status = ?"
            params.append(status)

        if prioritas and prioritas != "Semua":
            query += " AND prioritas = ?"
            params.append(prioritas)

        if search:
            query += " AND (nama LIKE ? OR lokasi LIKE ? OR deskripsi LIKE ?)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])

        query += " ORDER BY created_at DESC"

        rows = db.execute(query, params).fetchall()
        laporan = [dict(row) for row in rows]

        # Add first foto_url for thumbnail from foto_bukti table
        for lap in laporan:
            first_foto = db.execute(
                "SELECT foto_url FROM foto_bukti WHERE laporan_id = ? ORDER BY uploaded_at ASC LIMIT 1",
                (lap["id"],)
            ).fetchone()
            lap["foto_url"] = first_foto["foto_url"] if first_foto else None

        return jsonify({"laporan": laporan})

    @app.route("/api/laporan/<int:report_id>", methods=["GET"])
    def get_laporan_by_id(report_id):
        """Get single report by ID with foto bukti."""
        db = get_db()
        row = db.execute("SELECT * FROM laporan WHERE id = ?", (report_id,)).fetchone()

        if not row:
            return jsonify({"error": "Report not found"}), 404

        result = dict(row)

        # Add foto bukti
        foto_rows = db.execute(
            "SELECT * FROM foto_bukti WHERE laporan_id = ? ORDER BY uploaded_at ASC",
            (report_id,)
        ).fetchall()
        result["foto_bukti"] = [dict(f) for f in foto_rows]

        return jsonify(result)

    @app.route("/api/laporan/<int:report_id>/status", methods=["PATCH"])
    def update_status(report_id):
        """Update report status."""
        data = request.get_json()
        new_status = data.get("status")

        if not new_status:
            return jsonify({"error": "Status required"}), 400

        db = get_db()
        now = datetime.now().isoformat()
        db.execute(
            "UPDATE laporan SET status = ?, updated_at = ? WHERE id = ?",
            (new_status, now, report_id)
        )
        db.commit()

        return jsonify({"success": True, "status": new_status})

    @app.route("/api/laporan/<int:report_id>/prioritas", methods=["PATCH"])
    def update_prioritas(report_id):
        """Update report priority."""
        data = request.get_json()
        new_prioritas = data.get("prioritas")

        if not new_prioritas:
            return jsonify({"error": "Prioritas required"}), 400

        db = get_db()
        now = datetime.now().isoformat()
        db.execute(
            "UPDATE laporan SET prioritas = ?, updated_at = ? WHERE id = ?",
            (new_prioritas, now, report_id)
        )
        db.commit()

        return jsonify({"success": True, "prioritas": new_prioritas})

    @app.route("/api/foto", methods=["POST"])
    def add_foto_bukti():
        """Add foto bukti to a report."""
        data = request.get_json()

        laporan_id = data.get("laporan_id")
        foto_url = data.get("foto_url")

        if not laporan_id or not foto_url:
            return jsonify({"error": "laporan_id and foto_url required"}), 400

        now = datetime.now().isoformat()
        db = get_db()
        cursor = db.execute(
            "INSERT INTO foto_bukti (laporan_id, foto_url, uploaded_at) VALUES (?, ?, ?)",
            (laporan_id, foto_url, now)
        )
        db.commit()

        return jsonify({
            "success": True,
            "id": cursor.lastrowid,
            "laporan_id": laporan_id,
            "foto_url": foto_url
        }), 201

    @app.route("/api/laporan/<int:report_id>/catatan", methods=["PATCH"])
    def update_catatan(report_id):
        """Add/update note on a report."""
        data = request.get_json()
        catatan = data.get("catatan")

        if catatan is None:
            return jsonify({"error": "Catatan required"}), 400

        db = get_db()
        now = datetime.now().isoformat()
        db.execute(
            "UPDATE laporan SET catatan = ?, updated_at = ? WHERE id = ?",
            (catatan, now, report_id)
        )
        db.commit()

        return jsonify({"success": True, "catatan": catatan})

    @app.route("/api/stats", methods=["GET"])
    def get_stats():
        """Get statistics for admin dashboard."""
        db = get_db()

        # Auto-escalate old pending reports
        auto_escalate_old_reports(db)

        total = db.execute("SELECT COUNT(*) as count FROM laporan").fetchone()["count"]

        status_rows = db.execute(
            "SELECT status, COUNT(*) as count FROM laporan GROUP BY status"
        ).fetchall()
        by_status = {row["status"]: row["count"] for row in status_rows}

        priority_rows = db.execute(
            "SELECT prioritas, COUNT(*) as count FROM laporan GROUP BY prioritas"
        ).fetchall()
        by_priority = {row["prioritas"]: row["count"] for row in priority_rows}

        return jsonify({
            "total": total,
            "by_status": by_status,
            "by_priority": by_priority
        })

# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app.teardown_appcontext(close_db)

    init_backend_db()
    print("✅ Backend database initialized")

    create_routes(app)

    app.run(host="0.0.0.0", port=5000, debug=False)
