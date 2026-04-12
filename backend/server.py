"""
EcoLapor Backend API - Flask Server
Connects frontend to SQLite database (shared with bot)
"""
import os
import sqlite3
import httpx
import base64
import io
import json
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


# ─────────────────────────────────────────────
# AI Agent Functions
# ─────────────────────────────────────────────

def validate_image_content(image_base64: str) -> tuple[bool, str]:
    """Use AI Vision to validate if image contains waste/trash (not selfie or other content)."""
    try:
        # Handle both base64 with and without data URI prefix
        if "," in image_base64:
            image_base64 = image_base64.split(",", 1)[1]

        prompt = """Analisis gambar ini dan tentukan apakah ini FOTO SAMPAH atau BUKAN.

Kategori SAMPAH: tumpukan sampah,垃圾, waste, trash, garbage, kotoran, limbah

Kategori BUKAN SAMPAH: selfie, foto orang, foto makanan, foto kendaraan, foto gedung, foto风景, foto документ, screenshot, atau gambar lain yang bukan sampah.

Jawaban dalam format JSON saja:
{"valid": true/false, "reason": "penjelasan singkat"}

Jika gambar jelas-jelas sampah/waste → valid: true
Jika gambar jelas BUKAN sampah (selfie, makanan, dll) → valid: false
Jika tidak yakin → valid: false"""

        with httpx.Client(timeout=20) as client:
            response = client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.2-11b-vision-preview",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_base64}"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_tokens": 100,
                    "temperature": 0
                }
            )
            result = response.json()
            answer = result.get("choices", [{}])[0].get("message", {}).get("content", "")

            try:
                parsed = json.loads(answer)
                is_valid = parsed.get("valid", False)
                reason = parsed.get("reason", "Tidak dapat menentukan")
            except:
                is_valid = "true" in answer.lower() and "false" not in answer.lower()
                reason = "Valid" if is_valid else "Tidak valid"

            return is_valid, reason

    except Exception as e:
        print(f"[AI Vision] Error: {e}")
        return True, "Validation skipped due to error"  # Fail open for availability


def validate_description_content(nama: str, lokasi: str, deskripsi: str) -> tuple[bool, str]:
    """Use AI to validate if description is meaningful and relevant to waste reporting."""
    prompt = f"""Analisis deskripsi laporan sampah berikut:

Nama pelapor: {nama}
Lokasi: {lokasi}
Deskripsi: {deskripsi}

Tentukan apakah deskripsi ini VALID untuk laporan sampah:
- VALID = deskripsi jelas menjelaskan masalah sampah (jenis, jumlah, kondisi)
- TIDAK VALID = deskripsi kosong, terlalu pendek (<5 kata), tidak relevan dengan topik sampah, atau hanya karakter acak

Contoh TIDAK VALID:
- "tes", "aaaa", "ok", "siap", "tidak tahu", "?", ""
- "saya mau laporan", "bagaimana cara"
- Deskripsi tidak mention sampah sama sekali

Contoh VALID:
- "Tumpukan sampah di depan warung, ada plastik dan sisa makanan"
- "Sampah menumpuk di pinggir jalan, berbau busuk"
- "Kantong sampah penuh, perlu segera diangkut"

Jawaban dalam format JSON:
{{"valid": true/false, "reason": "penjelasan singkat"}}"""

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
                    "max_tokens": 100,
                    "temperature": 0
                }
            )
            result = response.json()
            answer = result.get("choices", [{}])[0].get("message", {}).get("content", "")

            try:
                parsed = json.loads(answer)
                is_valid = parsed.get("valid", True)
                reason = parsed.get("reason", "Deskripsi valid")
            except:
                is_valid = len(deskripsi.strip()) >= 5
                reason = "Valid" if is_valid else "Deskripsi terlalu pendek"

            return is_valid, reason

    except Exception as e:
        print(f"[AI Description] Error: {e}")
        return True, "Validation skipped due to error"  # Fail open


def classify_waste_type(nama: str, lokasi: str, deskripsi: str) -> str:
    """Use AI to classify waste type: Anorganik, Organik, or B3."""
    prompt = f"""Klasifikasikan jenis sampah dari laporan berikut:

Nama pelapor: {nama}
Lokasi: {lokasi}
Deskripsi: {deskripsi}

Jenis sampah:
- Anorganik = plastik, logam, kaca, kertas, kardus, botol, kaleng, styrofoam
- Organik = sisa makanan, daun, kayu, sayuran, fruit waste, kotoran hewan
- B3 = baterai, oli, cat, obat kadaluwarsa, pestisida, limbah medis, neon, mercury

Jawaban hanya 1 kata: Anorganik, Organik, atau B3.

Jika tidak yakin atau campuran, pilih yang paling dominan."""

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
                    "max_tokens": 10,
                    "temperature": 0
                }
            )
            result = response.json()
            answer = result.get("choices", [{}])[0].get("message", {}).get("content", "Anorganik").strip()

            if "Organik" in answer:
                return "Organik"
            elif "B3" in answer:
                return "B3"
            else:
                return "Anorganik"

    except Exception as e:
        print(f"[AI Classify] Error: {e}")
        return "Anorganik"


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


def record_correction(report_id: int, field: str, old_value: str, new_value: str, catatan: str):
    """Record agent correction for self-learning."""
    try:
        db = get_db()
        now = datetime.now().isoformat()
        db.execute(
            """INSERT INTO agent_corrections (laporan_id, field, old_value, new_value, catatan, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (report_id, field, old_value, new_value, catatan, now)
        )
        db.commit()
    except Exception as e:
        print(f"[Agent Correction] Error: {e}")


# ─────────────────────────────────────────────
# Database Init
# ─────────────────────────────────────────────

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
            jenis_sampah TEXT DEFAULT 'Anorganik',
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
    conn.execute("""
        CREATE TABLE IF NOT EXISTS agent_corrections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            laporan_id INTEGER,
            field TEXT,
            old_value TEXT,
            new_value TEXT,
            catatan TEXT,
            created_at TEXT
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
        """Submit a new waste report with full AI validation."""
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

        # ── Step 1: Validate image (if provided) ──
        if foto:
            is_valid_image, image_reason = validate_image_content(foto)
            if not is_valid_image:
                return jsonify({
                    "error": "Foto tidak valid",
                    "reason": "Mohon upload foto sampah yang benar. " + image_reason
                }), 400

        # ── Step 2: Validate description ──
        is_valid_desc, desc_reason = validate_description_content(nama, lokasi, deskripsi)
        if not is_valid_desc:
            return jsonify({
                "error": "Deskripsi tidak valid",
                "reason": desc_reason
            }), 400

        # ── Step 3: AI classifies waste type ──
        jenis_sampah = classify_waste_type(nama, lokasi, deskripsi)

        # ── Step 4: AI assigns priority ──
        prioritas = assign_priority_ai(nama, lokasi, deskripsi)

        now = datetime.now()
        tanggal = now.strftime("%d/%m/%Y")
        created_at = now.isoformat()

        db = get_db()
        cursor = db.execute(
            """INSERT INTO laporan (user_id, nama, lokasi, deskripsi, foto, status, prioritas, jenis_sampah, tanggal, created_at)
               VALUES (?, ?, ?, ?, ?, 'Menunggu', ?, ?, ?, ?)""",
            (user_id, nama, lokasi, deskripsi, foto, prioritas, jenis_sampah, tanggal, created_at)
        )
        db.commit()

        return jsonify({
            "success": True,
            "id": cursor.lastrowid,
            "status": "Menunggu",
            "prioritas": prioritas,
            "jenis_sampah": jenis_sampah,
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
        """Update report priority (admin correction)."""
        data = request.get_json()
        new_prioritas = data.get("prioritas")

        if not new_prioritas:
            return jsonify({"error": "Prioritas required"}), 400

        db = get_db()
        old_row = db.execute("SELECT prioritas FROM laporan WHERE id = ?", (report_id,)).fetchone()
        old_value = old_row["prioritas"] if old_row else None

        now = datetime.now().isoformat()
        db.execute(
            "UPDATE laporan SET prioritas = ?, updated_at = ? WHERE id = ?",
            (new_prioritas, now, report_id)
        )
        db.commit()

        # Record correction for self-learning
        if old_value and old_value != new_prioritas:
            record_correction(report_id, "prioritas", old_value, new_prioritas, "Admin correction")

        return jsonify({"success": True, "prioritas": new_prioritas})

    @app.route("/api/laporan/<int:report_id>/jenis", methods=["PATCH"])
    def update_jenis_sampah(report_id):
        """Update waste type (admin correction)."""
        data = request.get_json()
        new_jenis = data.get("jenis_sampah")

        if not new_jenis:
            return jsonify({"error": "jenis_sampah required"}), 400

        db = get_db()
        old_row = db.execute("SELECT jenis_sampah FROM laporan WHERE id = ?", (report_id,)).fetchone()
        old_value = old_row["jenis_sampah"] if old_row else None

        now = datetime.now().isoformat()
        db.execute(
            "UPDATE laporan SET jenis_sampah = ?, updated_at = ? WHERE id = ?",
            (new_jenis, now, report_id)
        )
        db.commit()

        # Record correction for self-learning
        if old_value and old_value != new_jenis:
            record_correction(report_id, "jenis_sampah", old_value, new_jenis, "Admin correction")

        return jsonify({"success": True, "jenis_sampah": new_jenis})

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

    @app.route("/api/agent/stats", methods=["GET"])
    def agent_stats():
        """Get agent correction statistics for self-learning analysis."""
        db = get_db()

        total_corrections = db.execute(
            "SELECT COUNT(*) as count FROM agent_corrections"
        ).fetchone()["count"]

        field_corrections = db.execute(
            "SELECT field, COUNT(*) as count FROM agent_corrections GROUP BY field"
        ).fetchall()
        by_field = {row["field"]: row["count"] for row in field_corrections}

        recent = db.execute(
            "SELECT * FROM agent_corrections ORDER BY created_at DESC LIMIT 10"
        ).fetchall()

        return jsonify({
            "total_corrections": total_corrections,
            "by_field": by_field,
            "recent_corrections": [dict(r) for r in recent]
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
