from database import (
    submit_report as db_submit_report,
    get_reports,
    get_all_reports,
    update_report_status,
    create_user,
    get_user,
)

# ─────────────────────────────────────────────
# TOOL: Submit Report (Warga)
# ─────────────────────────────────────────────
async def submit_report_tool(
    nama: str,
    lokasi: str,
    deskripsi: str,
    user_id: int
) -> dict:
    """
    Submit a new waste report (laporan sampah).
    Use this when user wants to report garbage/waste in their area.
    """
    result = await db_submit_report(user_id, nama, lokasi, deskripsi)
    return {
        "success": True,
        "message": (
            f"✅ Laporan berhasil dikirim!\n\n"
            f"📋 ID Laporan: #{result['id']}\n"
            f"📍 Lokasi: {lokasi}\n"
            f"📝 Status: Menunggu\n\n"
            f"Tim kami akan segera menindaklanjuti."
        ),
        "data": result
    }

# ─────────────────────────────────────────────
# TOOL: Get My Reports (Warga)
# ─────────────────────────────────────────────
async def get_my_reports_tool(user_id: int) -> dict:
    """
    Get all reports submitted by the current user.
    Use this when user asks about their report status/history.
    """
    reports = await get_reports(user_id)
    if not reports:
        return {
            "success": True,
            "message": "📭 Anda belum memiliki laporan apapun.",
            "data": []
        }
    
    lines = ["📋 Daftar Laporan Anda:\n"]
    for r in reports[:10]:
        lines.append(f"#{r['id']} | {r['lokasi']} | {r['status']} | {r['tanggal']}")
    lines.append("\nBalas dengan nomor ID untuk detail.")
    
    return {
        "success": True,
        "message": "\n".join(lines),
        "data": reports
    }

# ─────────────────────────────────────────────
# TOOL: Get All Reports (Admin)
# ─────────────────────────────────────────────
async def get_all_reports_tool(
    status: str = None,
    prioritas: str = None,
    limit: int = 50
) -> dict:
    """
    Get all reports in the system with optional filters. Admin only.
    
    Args:
        status: Filter by status ('Menunggu', 'Diproses', 'Selesai')
        prioritas: Filter by priority ('Tinggi', 'Sedang', 'Rendah')
        limit: Max number of reports to return (default 50)
    """
    reports = await get_all_reports()
    
    if status:
        reports = [r for r in reports if r.get('status') == status]
    if prioritas:
        reports = [r for r in reports if r.get('prioritas') == prioritas]
    
    reports = reports[:limit]
    
    if not reports:
        return {
            "success": True,
            "message": "📭 Tidak ada laporan yang cocok dengan filter.",
            "data": []
        }
    
    menunggu = sum(1 for r in reports if r.get('status') == 'Menunggu')
    diproses = sum(1 for r in reports if r.get('status') == 'Diproses')
    selesai = sum(1 for r in reports if r.get('status') == 'Selesai')
    
    lines = [
        f"📊 Filter: {len(reports)} hasil | "
        f"{menunggu} Menunggu | {diproses} Diproses | {selesai} Selesai\n"
    ]
    lines.append("\n📋 Laporan:\n")
    for r in reports:
        prioritas_tag = "🔴" if r.get('prioritas') == 'Tinggi' else "🟡" if r.get('prioritas') == 'Sedang' else "🟢"
        lines.append(
            f"#{r['id']} {prioritas_tag} | {r.get('nama', 'Anon')} | {r.get('lokasi', '-')} | "
            f"{r.get('status', '-')} | {r.get('tanggal', '-')}"
        )
    
    return {
        "success": True,
        "message": "\n".join(lines),
        "data": reports
    }

# ─────────────────────────────────────────────
# TOOL: Update Status (Admin)
# ─────────────────────────────────────────────
async def update_status_tool(report_id: int, status: str) -> dict:
    """
    Update the status of a report. Admin only.
    Status options: 'Menunggu', 'Diproses', 'Selesai'.
    """
    valid_statuses = ['Menunggu', 'Diproses', 'Selesai']
    if status not in valid_statuses:
        return {
            "success": False,
            "message": f"❌ Status harus salah satu dari: {', '.join(valid_statuses)}"
        }
    
    updated = await update_report_status(report_id, status)
    if not updated:
        return {
            "success": False,
            "message": f"❌ Laporan #{report_id} tidak ditemukan."
        }
    
    return {
        "success": True,
        "message": f"✅ Laporan #{report_id} berhasil diupdate ke status: {status}",
        "data": {"id": report_id, "status": status}
    }

# ─────────────────────────────────────────────
# TOOL: Set Priority (Admin)
# ─────────────────────────────────────────────
async def set_priority_tool(report_id: int, prioritas: str) -> dict:
    """
    Set the priority of a report. Admin only.
    Priority options: 'Tinggi', 'Sedang', 'Rendah'.
    """
    from database import update_report_priority
    
    valid_priorities = ['Tinggi', 'Sedang', 'Rendah']
    if prioritas not in valid_priorities:
        return {
            "success": False,
            "message": f"❌ Prioritas harus salah satu dari: {', '.join(valid_priorities)}"
        }
    
    updated = await update_report_priority(report_id, prioritas)
    if not updated:
        return {
            "success": False,
            "message": f"❌ Laporan #{report_id} tidak ditemukan."
        }
    
    emoji = "🔴" if prioritas == "Tinggi" else "🟡" if prioritas == "Sedang" else "🟢"
    return {
        "success": True,
        "message": f"✅ Laporan #{report_id} prioritas diupdate: {emoji} {prioritas}",
        "data": {"id": report_id, "prioritas": prioritas}
    }

# ─────────────────────────────────────────────
# TOOL: Add Note to Report (Admin)
# ─────────────────────────────────────────────
async def add_note_tool(report_id: int, catatan: str) -> dict:
    """
    Add an internal note to a report. Admin/Agent only.
    This is for tracking agent observations and actions.
    """
    from database import update_report_note
    
    updated = await update_report_note(report_id, catatan)
    if not updated:
        return {
            "success": False,
            "message": f"❌ Laporan #{report_id} tidak ditemukan."
        }
    
    return {
        "success": True,
        "message": f"📝 Catatan ditambahkan ke laporan #{report_id}:\n\n{catatan}",
        "data": {"id": report_id, "catatan": catatan}
    }

# ─────────────────────────────────────────────
# TOOL: Bulk Update Status (Admin)
# ─────────────────────────────────────────────
async def bulk_update_status_tool(report_ids: list, status: str) -> dict:
    """
    Update status for multiple reports at once. Admin only.
    
    Args:
        report_ids: List of report IDs to update
        status: New status ('Menunggu', 'Diproses', 'Selesai')
    """
    valid_statuses = ['Menunggu', 'Diproses', 'Selesai']
    if status not in valid_statuses:
        return {
            "success": False,
            "message": f"❌ Status harus salah satu dari: {', '.join(valid_statuses)}"
        }
    
    success_count = 0
    failed_ids = []
    
    for rid in report_ids:
        updated = await update_report_status(rid, status)
        if updated:
            success_count += 1
        else:
            failed_ids.append(rid)
    
    if failed_ids:
        msg = f"⚠️ {success_count} laporan berhasil diupdate. Gagal: {failed_ids}"
    else:
        msg = f"✅ {success_count} laporan berhasil diupdate ke status: {status}"
    
    return {
        "success": success_count > 0,
        "message": msg,
        "data": {"success": success_count, "failed": failed_ids}
    }

# ─────────────────────────────────────────────
# TOOL: Get Statistics (Admin)
# ─────────────────────────────────────────────
async def get_statistics_tool() -> dict:
    """
    Get overall statistics about reports. Admin only.
    Returns counts by status, priority, and trends.
    """
    reports = await get_all_reports()
    
    if not reports:
        return {
            "success": True,
            "message": "📊 Belum ada data laporan.",
            "data": {}
        }
    
    total = len(reports)
    by_status = {
        'Menunggu': sum(1 for r in reports if r.get('status') == 'Menunggu'),
        'Diproses': sum(1 for r in reports if r.get('status') == 'Diproses'),
        'Selesai': sum(1 for r in reports if r.get('status') == 'Selesai'),
    }
    by_priority = {
        'Tinggi': sum(1 for r in reports if r.get('prioritas') == 'Tinggi'),
        'Sedang': sum(1 for r in reports if r.get('prioritas') == 'Sedang'),
        'Rendah': sum(1 for r in reports if r.get('prioritas') == 'Rendah'),
    }
    
    # Calculate completion rate
    completion_rate = (by_status['Selesai'] / total * 100) if total > 0 else 0
    
    lines = [
        f"📊 Statistik Laporan EcoLapor\n",
        f"━━━━━━━━━━━━━━━━━━━━\n",
        f"📁 Total Laporan: {total}\n",
        f"✅ Selesai: {by_status['Selesai']} ({by_status['Selesai']/total*100:.1f}%)\n",
        f"🔄 Diproses: {by_status['Diproses']}\n",
        f"⏳ Menunggu: {by_status['Menunggu']}\n",
        f"━━━━━━━━━━━━━━━━━━━━\n",
        f"🔴 Prioritas Tinggi: {by_priority['Tinggi']}\n",
        f"🟡 Prioritas Sedang: {by_priority['Sedang']}\n",
        f"🟢 Prioritas Rendah: {by_priority['Rendah']}\n",
        f"━━━━━━━━━━━━━━━━━━━━\n",
        f"📈 Tingkat Penyelesaian: {completion_rate:.1f}%"
    ]
    
    return {
        "success": True,
        "message": "\n".join(lines),
        "data": {
            "total": total,
            "by_status": by_status,
            "by_priority": by_priority,
            "completion_rate": completion_rate
        }
    }

# ─────────────────────────────────────────────
# TOOL: Search Reports (Admin)
# ─────────────────────────────────────────────
async def search_reports_tool(query: str) -> dict:
    """
    Search reports by nama, lokasi, or deskripsi. Admin only.
    
    Args:
        query: Search keyword
    """
    reports = await get_all_reports()
    
    q = query.lower()
    results = [
        r for r in reports
        if q in r.get('nama', '').lower()
        or q in r.get('lokasi', '').lower()
        or q in r.get('deskripsi', '').lower()
    ]
    
    if not results:
        return {
            "success": True,
            "message": f"🔍 Tidak ada laporan yang cocok dengan: '{query}'",
            "data": []
        }
    
    lines = [f"🔍 Ditemukan {len(results)} hasil untuk: '{query}'\n"]
    for r in results[:20]:
        lines.append(f"#{r['id']} | {r.get('nama', '-')} | {r.get('lokasi', '-')} | {r.get('status', '-')}")
    
    return {
        "success": True,
        "message": "\n".join(lines),
        "data": results
    }

# ─────────────────────────────────────────────
# TOOL: Auto-Respond (Admin)
# ─────────────────────────────────────────────
async def auto_respond_tool(report_id: int, template: str) -> dict:
    """
    Set an auto-response template for a report. Admin only.
    
    Templates:
    - 'accepted': Laporan diterima, akan ditindaklanjuti
    - 'processing': Laporan sedang diproses
    - 'completed': Laporan selesai ditangani
    - 'rejected': Laporan ditolak (tidak valid)
    """
    templates = {
        'accepted': (
            "✅ Laporan Anda telah diterima.\n"
            "Tim kami akan meninjau dan menindaklanjuti dalam 1x24 jam.\n"
            "ID Laporan: #{id}"
        ),
        'processing': (
            "🔄 Laporan Anda sedang dalam proses penanganan.\n"
            "Tim lapangan sudah dikerahkan ke lokasi.\n"
            "ID Laporan: #{id}"
        ),
        'completed': (
            "✅ Laporan Anda telah selesai ditangani.\n"
            "Terima kasih atas partisipasi Anda dalam menjaga kebersihan lingkungan.\n"
            "ID Laporan: #{id}"
        ),
        'rejected': (
            "❌ Maaf, laporan Anda tidak dapat diproses.\n"
            "Kemungkinan karena informasi yang tidak lengkap atau lokasi tidak valid.\n"
            "Silakan kirim laporan baru dengan data yang lebih lengkap.\n"
            "ID Laporan: #{id}"
        ),
    }
    
    if template not in templates:
        return {
            "success": False,
            "message": f"❌ Template tidak valid. Pilihan: {', '.join(templates.keys())}"
        }
    
    return {
        "success": True,
        "message": templates[template].format(id=report_id),
        "data": {"id": report_id, "template": template}
    }

# ─────────────────────────────────────────────
# HELPER: Ensure User
# ─────────────────────────────────────────────
async def ensure_user(user_id: int, username: str) -> dict:
    """Ensure user exists in database."""
    user = await get_user(user_id)
    if not user:
        await create_user(user_id, username)
        user = await get_user(user_id)
    return user
