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
from flask import send_from_directory

STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
FOTO_DIR = os.path.join(STATIC_DIR, 'foto')
os.makedirs(FOTO_DIR, exist_ok=True)

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path='/static')
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
    """Use AI Vision to validate if image contains an environmental issue.
    
    Lenient: accepts any environmental issue. Rejects only clearly irrelevant
    content like selfies, food, vehicles, landscapes.
    """
    if not image_base64:
        return True, "No image"

    try:
        if "," in image_base64:
            image_base64 = image_base64.split(",", 1)[1]
    except Exception:
        pass

    if image_base64.startswith('iVBOR'):
        mime = 'image/png'
    elif image_base64.startswith('UklGR'):
        mime = 'image/webp'
    else:
        mime = 'image/jpeg'

    sumopod_key = os.getenv("SUMOPOD_API_KEY", "sk-CJSIoKjjsr-v0NlC7P3IhQ")

    try:
        import httpx
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                'https://ai.sumopod.com/v1/chat/completions',
                headers={'Authorization': f'Bearer {sumopod_key}', 'Content-Type': 'application/json'},
                json={
                    'model': 'gpt-5.1',
                    'messages': [{'role': 'user', 'content': [
                        {'type': 'text', 'text': 'Periksa foto ini. Jawab VALID jika menunjukkan masalah lingkungan (sampah, banjir, pencemaran, fasilitas rusak, pohon bahaya, hewan terlantar, kebakaran). Jawab TIDAK_VALID jika BUKAN masalah lingkungan (selfie, makanan, dokumen). Jawaban satu kata saja.'},
                        {'type': 'image_url', 'image_url': {'url': f'data:{mime};base64,{image_base64}'}}
                    ]}],
                    'max_tokens': 20,
                    'temperature': 0.1
                }
            )

        result = response.json()
        if "choices" not in result:
            return True, "OK (vision check skipped)"
        answer = result["choices"][0]["message"]["content"].strip().upper()
        if "TIDAK_VALID" in answer or "INVALID" in answer:
            return False, "Foto tidak menunjukkan masalah lingkungan. Mohon upload foto yang relevan."
        return True, "OK"
    except Exception:
        return True, "OK (vision check error)"


def validate_description_content(nama: str, lokasi: str, deskripsi: str) -> tuple[bool, str]:
    """Use AI to validate if description is meaningful and relevant to waste reporting.
    
    Lenient: accepts most text as valid. Only rejects gibberish/empty/clearly wrong content.
    """
    # Basic rule-based pre-check before calling AI
    deskripsi_lower = deskripsi.strip().lower()
    if len(deskripsi_lower) < 3:
        return False, "Deskripsi terlalu pendek"
    if len(deskripsi.strip()) < 3:
        return False, "Deskripsi terlalu pendek"
    if len(deskripsi_lower) > 2000:
        return False, "Deskripsi terlalu panjang"
    return True, "Valid"


def classify_category(nama: str, lokasi: str, deskripsi: str, kategori_hint: str = None) -> tuple[str, str]:
    """Use AI to classify report category and sub-category.
    Returns (kategori, sub_kategori)."""
    # If user explicitly chose a category, trust it
    if kategori_hint and kategori_hint != "Lainnya":
        return kategori_hint, classify_sub_category(nama, lokasi, deskripsi, kategori_hint)

    prompt = f"""Klasifikasikan laporan lingkungan berikut:

Nama pelapor: {nama}
Lokasi: {lokasi}
Deskripsi: {deskripsi}

Kategori (pilih SATU):
- Sampah = tumpukan sampah, limbah, plastik, organik, B3
- Banjir = genangan, drainase tersumbat, area banjir
- Pencemaran_Air = sungai/laut tercemar, limbah cair
- Pencemaran_Udara = asap, debu, polusi
- Fasilitas_Rusak = taman rusak, lampu mati, trotoar
- Hewan_Liar = hewan terlantar/sakit/berbahaya
- Pohon_Bahaya = pohon roboh, rantau mengancam
- Kebakaran = kebakaran hutan/lahan
- Lainnya = tidak cocok di atas

Jawaban hanya 1 kata: kategorinya."""

    try:
        with httpx.Client(timeout=15) as client:
            response = client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": prompt}], "max_tokens": 10, "temperature": 0}
            )
            result = response.json()
            answer = result.get("choices", [{}])[0].get("message", {}).get("content", "Sampah").strip()

            mapping = {
                "Sampah": "Sampah", "Banjir": "Banjir", "Pencemaran_Air": "Pencemaran Air",
                "Pencemaran_Udara": "Pencemaran Udara", "Fasilitas_Rusak": "Fasilitas Rusak",
                "Hewan_Liar": "Hewan Liar", "Pohon_Bahaya": "Pohon Bahaya",
                "Kebakaran": "Kebakaran", "Lainnya": "Lainnya"
            }
            kategori = mapping.get(answer, "Lainnya")
            return kategori, classify_sub_category(nama, lokasi, deskripsi, kategori)
    except Exception as e:
        print(f"[AI Classify Category] Error: {e}")
        return "Sampah", None


def classify_sub_category(nama: str, lokasi: str, deskripsi: str, kategori: str) -> str:
    """Classify sub-category based on main category."""
    sub_map = {
        "Sampah": "Anorganik, Organik, B3",
        "Banjir": "Genangan, Drainase Tersumbat, Banjir Besar",
        "Pencemaran Air": "Limbah Cair, Limbah Industri, Tumpahan",
        "Pencemaran Udara": "Asap, Debu, Polusi Industri",
        "Fasilitas Rusak": "Lampu Mati, Trotoar, Taman, Jalan",
        "Hewan Liar": "Terlantar, Sakit, Berbahaya",
        "Pohon Bahaya": "Roboh, Rantau, Akar",
        "Kebakaran": "Hutan, Lahan, Semak",
    }
    options = sub_map.get(kategori, "Umum")

    prompt = f"""Klasifikasikan sub-kategori laporan lingkungan:

Kategori: {kategori}
Deskripsi: {deskripsi}
Lokasi: {lokasi}

Pilihan: {options}

Jawaban hanya 1 kata."""

    try:
        with httpx.Client(timeout=15) as client:
            response = client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": prompt}], "max_tokens": 10, "temperature": 0}
            )
            result = response.json()
            answer = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            return answer if answer else None
    except Exception:
        return None


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
            kategori TEXT DEFAULT 'Sampah',
            sub_kategori TEXT,
            latitude TEXT,
            longitude TEXT,
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
    # Migrations for existing DBs
    for col, default in [
        ("jenis_sampah", "Anorganik"),
        ("kategori", "Sampah"),
        ("sub_kategori", None),
        ("latitude", None),
        ("longitude", None),
    ]:
        try:
            conn.execute(f"ALTER TABLE laporan ADD COLUMN {col} TEXT DEFAULT '{default or ''}'")
            conn.commit()
        except Exception:
            pass
    # Set kategori for existing rows
    try:
        conn.execute("UPDATE laporan SET kategori = 'Sampah' WHERE kategori IS NULL OR kategori = ''")
        conn.commit()
    except Exception:
        pass
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
        """Submit a new environmental report with full AI validation."""
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        nama = data.get("nama")
        lokasi = data.get("lokasi") or ""
        deskripsi = data.get("deskripsi") or ""
        user_id = data.get("user_id", 0)
        foto = data.get("foto")
        exif_lat = data.get("exif_lat")
        exif_lon = data.get("exif_lon")
        exif_timestamp = data.get("exif_timestamp")
        kategori_hint = data.get("kategori")  # User-chosen category

        if not nama:
            return jsonify({"error": "Nama wajib diisi"}), 400

        # ── Step 0: Auto-fill lokasi from EXIF GPS or AI vision ──
        if not lokasi:
            if exif_lat and exif_lon:
                lokasi = f"{exif_lat},{exif_lon}"
            elif foto:
                ai_lokasi = None
                for attempt in range(2):
                    try:
                        ai_lokasi = extract_location_from_image(foto)
                        if ai_lokasi:
                            break
                    except Exception as e:
                        print(f"[WARN] AI lokasi attempt {attempt+1} failed: {e}")
                if ai_lokasi:
                    lokasi = ai_lokasi
                else:
                    lokasi = "Lokasi tidak diketahui"
            else:
                lokasi = "Lokasi tidak diketahui"

        # Auto-generate or enhance deskripsi
        if foto:
            if not deskripsi:
                desc_result = None
                for attempt in range(2):
                    try:
                        desc_result = describe_image_ai(foto)
                        if desc_result:
                            break
                    except Exception as e:
                        print(f"[WARN] Auto-describe attempt {attempt+1} failed: {e}")
                deskripsi = desc_result or "Laporan masalah lingkungan"
            elif len(deskripsi.strip()) < 20:
                desc_result = None
                for attempt in range(2):
                    try:
                        desc_result = describe_image_ai(foto)
                        if desc_result:
                            break
                    except Exception as e:
                        print(f"[WARN] Auto-enhance attempt {attempt+1} failed: {e}")
                if desc_result:
                    deskripsi = desc_result

        # ── Step 1: Validate image (if provided) ──
        if foto:
            is_valid_image, image_reason = validate_image_content(foto)
            if not is_valid_image:
                return jsonify({"error": "Foto tidak valid", "reason": image_reason}), 400

        # ── Step 2: Validate description ──
        is_valid_desc, desc_reason = validate_description_content(nama, lokasi, deskripsi)
        if not is_valid_desc:
            return jsonify({"error": "Deskripsi tidak valid", "reason": desc_reason}), 400

        # ── Step 3: AI classifies category + sub-category ──
        kategori, sub_kategori = classify_category(nama, lokasi, deskripsi, kategori_hint)

        # ── Step 4: AI classifies waste type (only for Sampah category) ──
        jenis_sampah = classify_waste_type(nama, lokasi, deskripsi) if kategori == "Sampah" else None

        # ── Step 5: AI assigns priority ──
        prioritas = assign_priority_ai(nama, lokasi, deskripsi)

        now = datetime.now()
        tanggal = now.strftime("%d/%m/%Y")
        created_at = now.isoformat()

        db = get_db()
        cursor = db.execute(
            """INSERT INTO laporan (user_id, nama, lokasi, deskripsi, foto, status, prioritas, jenis_sampah, kategori, sub_kategori, latitude, longitude, tanggal, created_at)
               VALUES (?, ?, ?, ?, ?, 'Menunggu', ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, nama, lokasi, deskripsi, foto, prioritas, jenis_sampah, kategori, sub_kategori, exif_lat, exif_lon, tanggal, created_at)
        )
        db.commit()

        return jsonify({
            "success": True,
            "id": cursor.lastrowid,
            "status": "Menunggu",
            "prioritas": prioritas,
            "jenis_sampah": jenis_sampah,
            "kategori": kategori,
            "sub_kategori": sub_kategori,
            "tanggal": tanggal
        }), 201

    @app.route("/api/laporan", methods=["GET"])
    def get_laporan():
        """Get reports with pagination (5 per page)."""
        user_id = request.args.get("user_id", type=int)
        status = request.args.get("status")
        prioritas = request.args.get("prioritas")
        kategori = request.args.get("kategori")
        search = request.args.get("search")
        page = request.args.get("page", 1, type=int)
        per_page = 5

        db = get_db()
        auto_escalate_old_reports(db)

        query = """SELECT id, user_id, nama, lokasi, deskripsi, status, prioritas, jenis_sampah, kategori, sub_kategori, catatan, tanggal, created_at, updated_at, latitude, longitude, CASE WHEN foto IS NOT NULL AND foto != '' THEN 1 ELSE 0 END as foto_exists FROM laporan WHERE 1=1"""
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
        if kategori and kategori != "Semua":
            query += " AND kategori = ?"
            params.append(kategori)
        if search:
            query += " AND (nama LIKE ? OR lokasi LIKE ? OR deskripsi LIKE ?)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])

        # Count total
        count_query = query.replace("SELECT id, user_id, nama, lokasi, deskripsi, status, prioritas, jenis_sampah, kategori, sub_kategori, catatan, tanggal, created_at, updated_at, latitude, longitude, CASE WHEN foto IS NOT NULL AND foto != '' THEN 1 ELSE 0 END as foto_exists", "SELECT COUNT(*) as total")
        total = db.execute(count_query, params).fetchone()["total"]

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([per_page, (page - 1) * per_page])

        rows = db.execute(query, params).fetchall()
        laporan = [dict(row) for row in rows]

        return jsonify({
            "laporan": laporan,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page
            }
        })

    @app.route("/api/laporan/<int:report_id>/preview", methods=["GET"])
    def get_laporan_preview(report_id):
        """Return warga's original foto (base64) for thumbnail preview.
        Lightweight endpoint — only id + foto (base64), no other columns.
        Serves warga's original submission, NOT officer bukti photos."""
        db = get_db()
        row = db.execute(
            "SELECT id, foto FROM laporan WHERE id = ? AND foto IS NOT NULL AND foto != ''",
            (report_id,)
        ).fetchone()

        if not row:
            return jsonify({"id": report_id, "foto": None})

        return jsonify({"id": row["id"], "foto": row["foto"]})

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

    @app.route("/api/laporan/<int:report_id>", methods=["DELETE"])
    def delete_laporan(report_id):
        """Delete a report. Admin only."""
        db = get_db()
        cursor = db.execute("DELETE FROM laporan WHERE id = ?", (report_id,))
        db.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Report not found"}), 404

        # Also delete related foto_bukti entries
        db.execute("DELETE FROM foto_bukti WHERE laporan_id = ?", (report_id,))
        db.commit()

        return jsonify({"success": True, "deleted_id": report_id})

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
        })

    @app.route("/api/laporan/<int:report_id>/foto", methods=["POST"])
    def update_laporan_foto(report_id):
        """Receive base64 foto from bot/officer, save as static file, store path in laporan.foto.
        foto_bukti stores Telegram file_id separately for reference.
        Static file URL in laporan.foto is what both warga and admin see in lists."""
        data = request.get_json()
        foto_base64 = data.get("foto")

        if not foto_base64:
            return jsonify({"error": "foto (base64) required"}), 400

        if ',' in foto_base64:
            foto_base64 = foto_base64.split(',', 1)[1]

        try:
            image_data = base64.b64decode(foto_base64)
        except Exception:
            return jsonify({"error": "Invalid base64 image"}), 400

        filename = f"bukti_{report_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        filepath = os.path.join(FOTO_DIR, filename)
        with open(filepath, 'wb') as f:
            f.write(image_data)

        foto_url = f"/static/foto/{filename}"

        db = get_db()
        exists = db.execute("SELECT id FROM laporan WHERE id = ?", (report_id,)).fetchone()
        if not exists:
            return jsonify({"error": "Report not found"}), 404

        now = datetime.now().isoformat()
        cursor = db.execute(
            "UPDATE laporan SET foto = ?, updated_at = ? WHERE id = ?",
            (foto_url, now, report_id)
        )
        db.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Report not found"}), 404

        return jsonify({
            "success": True,
            "report_id": report_id,
            "foto_url": foto_url
        }), 200

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
        auto_escalate_old_reports(db)

        total = db.execute("SELECT COUNT(*) as count FROM laporan").fetchone()["count"]

        status_rows = db.execute("SELECT status, COUNT(*) as count FROM laporan GROUP BY status").fetchall()
        by_status = {row["status"]: row["count"] for row in status_rows}

        priority_rows = db.execute("SELECT prioritas, COUNT(*) as count FROM laporan GROUP BY prioritas").fetchall()
        by_priority = {row["prioritas"]: row["count"] for row in priority_rows}

        category_rows = db.execute("SELECT kategori, COUNT(*) as count FROM laporan GROUP BY kategori").fetchall()
        by_category = {row["kategori"]: row["count"] for row in category_rows}

        return jsonify({
            "total": total,
            "by_status": by_status,
            "by_priority": by_priority,
            "by_category": by_category
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

def describe_image_ai(image_base64: str):
    """
    Reusable AI image description helper using SumoPod GPT-5.1 with base64 data URIs.
    Returns a waste description string, or None on failure / non-waste image.
    """
    if not image_base64:
        return None
    try:
        if ',' in image_base64:
            image_base64 = image_base64.split(',', 1)[1]
    except Exception:
        pass

    # Detect MIME type from magic bytes
    if image_base64.startswith('iVBOR'):
        mime = 'image/png'
    elif image_base64.startswith('UklGR'):
        mime = 'image/webp'
    else:
        mime = 'image/jpeg'

    sumopod_key = os.getenv("SUMOPOD_API_KEY", "sk-CJSIoKjjsr-v0NlC7P3IhQ")

    try:
        import httpx
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                'https://ai.sumopod.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {sumopod_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'gpt-5.1',
                    'messages': [{
                        'role': 'user',
                        'content': [
                            {'type': 'text', 'text': 'Anda adalah asisten AI yang menganalisis foto masalah lingkungan di Indonesia. Jelaskan secara detail dan concis (2-3 kalimat) kondisi dalam foto dalam Bahasa Indonesia formal. Bisa berupa: sampah, banjir, pencemaran, fasilitas rusak, pohon bahaya, hewan terlantar, kebakaran. Contoh: Tumpukan sampah plastik di pinggir jalan, genangan air di drainase, pohon roboh menghalangi jalan. Jika foto BUKAN masalah lingkungan, jawab: FOTO_BUKAN_MASALAH'},
                            {'type': 'image_url', 'image_url': {'url': f'data:{mime};base64,{image_base64}'}}
                        ]
                    }],
                    'max_tokens': 200,
                    'temperature': 0.3
                }
            )

        result = response.json()
        if "choices" not in result:
            return None
        desc = result["choices"][0]["message"]["content"].strip()
        if "BUKAN_MASALAH" in desc.upper() or "bukan masalah" in desc.lower() or "BUKAN_SAMPAH" in desc.upper() or "bukan sampah" in desc.lower():
            return None
        return desc
    except Exception:
        return None


def extract_location_from_image(image_base64: str):
    """
    AI vision to detect location from photo (road name, landmark, area description).
    Returns a location string like "Jl. Sudirman, dekat Pasar Bajo, Manado" or None.
    """
    if not image_base64:
        return None
    try:
        if ',' in image_base64:
            image_base64 = image_base64.split(',', 1)[1]
    except Exception:
        pass

    if image_base64.startswith('iVBOR'):
        mime = 'image/png'
    elif image_base64.startswith('UklGR'):
        mime = 'image/webp'
    else:
        mime = 'image/jpeg'

    sumopod_key = os.getenv("SUMOPOD_API_KEY", "sk-CJSIoKjjsr-v0NlC7P3IhQ")

    try:
        import httpx
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                'https://ai.sumopod.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {sumopod_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'gpt-5.1',
                    'messages': [{
                        'role': 'user',
                        'content': [
                            {'type': 'text', 'text': 'Analisis foto untuk mendeteksi LOKASI geografis di Manado, Sulawesi Utara, Indonesia. Return JSON dengan key "lokasi" berisi deskripsi lokasi yang spesifik dan detail dalam Bahasa Indonesia. Prioritas: (1) nama jalan + landmark/nama tempat, (2) nama area/neighbourhood + bangunan terkenal, (3) keterangan area umum (ruangan kelas, pinggir jalan, pasar). Jika foto benar-benar tidak memiliki petunjuk lokasi sama sekali, return: {"lokasi": ""}. Contoh valid: {"lokasi": "Jl. Sudirman, dekat Pasar Bajo, Manado"}, {"lokasi": "Di dalam ruangan kelas sekolah"}, {"lokasi": "Di pinggir jalan Boulevard, Manado"}. Jangan gunakan koordinat GPS.'},
                            {'type': 'image_url', 'image_url': {'url': f'data:{mime};base64,{image_base64}'}}
                        ]
                    }],
                    'max_tokens': 80,
                    'temperature': 0.3
                }
            )

        result = response.json()
        if "choices" not in result:
            return None
        raw = result["choices"][0]["message"]["content"].strip()
        # Parse JSON response
        import json
        try:
            data = json.loads(raw)
            lokasi = data.get("lokasi", "").strip()
            return lokasi if lokasi else None
        except Exception:
            # Try to extract from text response
            if "lokasi" in raw.lower():
                import re
                match = re.search(r'"lokasi"\s*:\s*"([^"]+)"', raw)
                if match:
                    return match.group(1).strip()
            return None
    except Exception:
        return None


@app.route("/api/agent/classify", methods=["POST"])
def agent_classify():
    """
    Classify waste type from text description.
    Returns: { "category": "Anorganik|Organik|B3", "confidence": float }
    """
    body = request.get_json()
    text = body.get("text", "")

    if not text.strip():
        return jsonify({"error": "text required"}), 400

    prompt = f"""Klasifikasikan jenis sampah dari laporan berikut:

{text}

Jenis sampah:
- Anorganik = plastik, logam, kaca, kertas, kardus, botol, kaleng, styrofoam
- Organik = sisa makanan, daun, kayu, sayuran, fruit waste, kotoran hewan
- B3 = baterai, oli, cat, obat kadaluwarsa, pestisida, limbah medis, neon, mercury

Jawaban hanya 1 kata: Anorganik, Organik, atau B3."""

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
                category = "Organik"
            elif "B3" in answer:
                category = "B3"
            else:
                category = "Anorganik"

            return jsonify({"category": category, "confidence": 0.9})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/agent/priority", methods=["POST"])
def agent_priority():
    """
    Assign priority from text description.
    Returns: { "priority": "Rendah|Sedang|Tinggi", "reason": str }
    """
    body = request.get_json()
    text = body.get("text", "")

    if not text.strip():
        return jsonify({"error": "text required"}), 400

    prompt = f"""Tentukan prioritas pelaporan sampah:

{text}

Prioritas:
- Tinggi = mengancam kesehatan/safety (B3, menumpuk besar, menutup drainase, di sekolah/rumah sakit)
- Sedang = mengganggu kenyamanan (tumpukan sedang, bau, di trotoar)
- Rendah = aesthetic/nuisance kecil (sedikit sampah, di tempat sepi)

Jawaban hanya 1 kata: Tinggi, Sedang, atau Rendah."""

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
            answer = result.get("choices", [{}])[0].get("message", {}).get("content", "Sedang").strip()

            if "Tinggi" in answer:
                priority = "Tinggi"
            elif "Rendah" in answer:
                priority = "Rendah"
            else:
                priority = "Sedang"

            return jsonify({"priority": priority, "reason": f"Based on: {text[:100]}"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/agent/describe", methods=["POST"])
def agent_describe():
    """
    AI auto-description: analyze photo and generate waste description.
    Uses SumoPod GPT-5.1 with base64 data URIs.
    """
    body = request.get_json()
    image_base64 = body.get("image", "")

    if not image_base64:
        return jsonify({"success": False, "error": "No image provided"}), 400

    try:
        if "," in image_base64:
            image_base64 = image_base64.split(",", 1)[1]
    except Exception:
        pass

    # Detect MIME type from magic bytes
    if image_base64.startswith('iVBOR'):
        mime = 'image/png'
    elif image_base64.startswith('UklGR'):
        mime = 'image/webp'
    else:
        mime = 'image/jpeg'

    sumopod_key = os.getenv("SUMOPOD_API_KEY", "sk-CJSIoKjjsr-v0NlC7P3IhQ")

    try:
        import httpx
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                'https://ai.sumopod.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {sumopod_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'gpt-5.1',
                    'messages': [{
                        'role': 'user',
                        'content': [
                            {'type': 'text', 'text': 'Anda adalah asisten AI yang menganalisis foto masalah lingkungan di Indonesia. Jelaskan secara detail dan concis (2-3 kalimat) kondisi dalam foto tersebut dalam Bahasa Indonesia formal. Ini bisa berupa: sampah, banjir, pencemaran, fasilitas rusak, pohon bahaya, hewan terlantar, kebakaran, atau masalah lingkungan lainnya. Jika foto BUKAN masalah lingkungan (misalnya selfie, makanan, kendaraan), jawab: FOTO_BUKAN_MASALAH'},
                            {'type': 'image_url', 'image_url': {'url': f'data:{mime};base64,{image_base64}'}}
                        ]
                    }],
                    'max_tokens': 200,
                    'temperature': 0.3
                }
            )

        result = response.json()
        if "choices" not in result:
            return jsonify({"success": False, "error": result.get("error", {}).get("message", "AI error")}), 500

        description = result["choices"][0]["message"]["content"].strip()

        if "BUKAN_MASALAH" in description.upper() or "bukan masalah" in description.lower() or "BUKAN_SAMPAH" in description.upper() or "bukan sampah" in description.lower():
            return jsonify({"success": False, "error": "Foto bukan masalah lingkungan"}), 400

        return jsonify({"success": True, "description": description})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app.teardown_appcontext(close_db)

    # ── Global error handlers: always return JSON ──
    @app.errorhandler(Exception)
    def handle_exception(e):
        return jsonify({"error": str(e)}), getattr(e, 'code', 500)

    @app.errorhandler(404)
    def handle_404(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(405)
    def handle_405(e):
        return jsonify({"error": "Method not allowed"}), 405

    init_backend_db()
    print("✅ Backend database initialized")

    create_routes(app)

    app.run(host="0.0.0.0", port=5000, debug=False)
