from database import (
    submit_report as db_submit_report,
    get_reports,
    get_all_reports,
    update_report_status,
    update_report_priority,
    create_user,
    get_user,
    register_petugas,
    is_petugas,
    get_petugas,
    get_pending_reports,
    add_foto_bukti,
    get_foto_bukti,
    get_statistics,
    get_report_by_id,
    update_report_note,
    update_report_foto,
)

# ─────────────────────────────────────────────
# TOOL: Submit Report (Warga)
# ─────────────────────────────────────────────
async def submit_report_tool(
    nama: str,
    lokasi: str,
    deskripsi: str,
    user_id: int,
    kategori: str = "Sampah"
) -> dict:
    """
    Submit a new environmental report.
    Use this when user wants to report any environmental issue.
    """
    result = await db_submit_report(user_id, nama, lokasi, deskripsi, kategori=kategori)
    return {
        "success": True,
        "message": (
            f"✅ Laporan berhasil dikirim!\n\n"
            f"📋 ID Laporan: #{result['id']}\n"
            f"📍 Lokasi: {lokasi}\n"
            f"📂 Kategori: {kategori}\n"
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
    """
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
    Get overall statistics about reports.
    """
    stats = await get_statistics()
    reports = await get_all_reports()
    
    if stats['total'] == 0:
        return {
            "success": True,
            "message": "📊 Belum ada data laporan.",
            "data": stats
        }
    
    total = stats['total']
    by_status = stats.get('by_status', {})
    by_priority = stats.get('by_priority', {})
    
    selesai = by_status.get('Selesai', 0)
    completion_rate = (selesai / total * 100) if total > 0 else 0
    
    lines = [
        f"📊 Statistik Laporan EcoLapor\n",
        f"━━━━━━━━━━━━━━━━━━━━\n",
        f"📁 Total Laporan: {total}\n",
        f"✅ Selesai: {selesai} ({selesai/total*100:.1f}%)\n",
        f"🔄 Diproses: {by_status.get('Diproses', 0)}\n",
        f"⏳ Menunggu: {by_status.get('Menunggu', 0)}\n",
        f"━━━━━━━━━━━━━━━━━━━━\n",
        f"🔴 Prioritas Tinggi: {by_priority.get('Tinggi', 0)}\n",
        f"🟡 Prioritas Sedang: {by_priority.get('Sedang', 0)}\n",
        f"🟢 Prioritas Rendah: {by_priority.get('Rendah', 0)}\n",
        f"━━━━━━━━━━━━━━━━━━━━\n",
        f"📈 Tingkat Penyelesaian: {completion_rate:.1f}%"
    ]
    
    return {
        "success": True,
        "message": "\n".join(lines),
        "data": stats
    }

# ─────────────────────────────────────────────
# TOOL: Search Reports
# ─────────────────────────────────────────────
async def search_reports_tool(query: str) -> dict:
    """
    Search reports by nama, lokasi, or deskripsi.
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
# TOOL: Register Petugas
# ─────────────────────────────────────────────
async def register_petugas_tool(telegram_id: int, nama: str) -> dict:
    """
    Register a new petugas (field officer).
    Use when petugas does /start for the first time.
    """
    result = await register_petugas(telegram_id, nama)
    return {
        "success": True,
        "message": (
            f"✅ Petugas berhasil terdaftar!\n\n"
            f"👤 Nama: {nama}\n"
            f"🆔 Telegram ID: {telegram_id}\n\n"
            f"Command tersedia:\n"
            f"/task - Ambil 1 tugas\n"
            f"/list - Lihat semua pending\n"
            f"/done <id> <catatan> - Tandai selesai\n"
            f"/foto <id> - Upload foto bukti\n"
            f"/stats - Statistik"
        ),
        "data": result
    }

# ─────────────────────────────────────────────
# TOOL: Get Task (Petugas)
# ─────────────────────────────────────────────
async def get_task_tool(telegram_id: int, task_id: int = None) -> dict:
    """
    Get a specific pending task by ID, or the highest priority task if no ID specified.
    Petugas only.
    """
    # Check if registered
    if not await is_petugas(telegram_id):
        return {
            "success": False,
            "message": "❌ Anda belum terdaftar sebagai petugas.\nGunakan /start untuk mendaftar."
        }

    pending = await get_pending_reports()

    if not pending:
        return {
            "success": True,
            "message": "✅ Tidak ada laporan yang menunggu.\nSemua laporan sudah ditangani!"
        }

    # If specific task_id requested, find that task
    if task_id is not None:
        task = next((t for t in pending if t['id'] == task_id), None)
        if not task:
            return {
                "success": False,
                "message": f"❌ Laporan #{task_id} tidak ditemukan atau sudah selesai."
            }
        # Auto-update status: Menunggu -> Diproses when petugas claims this specific task
        await update_report_status(task['id'], "Diproses")
    else:
        task = pending[0]  # Default: oldest highest priority

    # Auto-update status: Menunggu -> Diproses when petugas claims task
    await update_report_status(task['id'], "Diproses")

    # Format the task message
    prioritas_emoji = "🔴" if task.get('prioritas') == 'Tinggi' else "🟡" if task.get('prioritas') == 'Sedang' else "🟢"
    
    msg = (
        f"📋 TUGAS BARU #{task['id']}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{prioritas_emoji} Prioritas: {task.get('prioritas', 'Sedang')}\n"
        f"👤 Pelapor: {task.get('nama', 'Anonim')}\n"
        f"📍 Lokasi: {task.get('lokasi', '-')}\n"
        f"📝 Deskripsi: {task.get('deskripsi', '-')}\n"
        f"🕐 Dilaporkan: {task.get('tanggal', '-')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Sudah selesai? Ketik:\n"
        f"/done {task['id']} <catatan hasil kerja>\n\n"
        f"Upload foto bukti:\n"
        f"/foto {task['id']}"
    )
    
    return {
        "success": True,
        "message": msg,
        "data": task
    }

# ─────────────────────────────────────────────
# TOOL: Mark Done (Petugas)
# ─────────────────────────────────────────────
async def mark_done_tool(report_id: int, catatan: str, telegram_id: int) -> dict:
    """
    Mark a report as Selesai (completed). Petugas only.
    """
    if not await is_petugas(telegram_id):
        return {
            "success": False,
            "message": "❌ Anda belum terdaftar sebagai petugas.\nGunakan /start untuk mendaftar."
        }
    
    report = await get_report_by_id(report_id)
    if not report:
        return {
            "success": False,
            "message": f"❌ Laporan #{report_id} tidak ditemukan."
        }
    
    if report.get('status') == 'Selesai':
        return {
            "success": False,
            "message": f"⚠️ Laporan #{report_id} sudah selesai."
        }
    
    # Update status and note
    await update_report_status(report_id, 'Selesai')
    if catatan:
        await update_report_note(report_id, catatan)
    
    return {
        "success": True,
        "message": (
            f"✅ Laporan #{report_id} ditandai SELESAI!\n\n"
            f"📝 Catatan: {catatan or '-'}\n\n"
            f"Jangan lupa upload foto bukti:\n"
            f"/foto {report_id}"
        ),
        "data": {"id": report_id, "status": "Selesai", "catatan": catatan}
    }

# ─────────────────────────────────────────────
# TOOL: Upload Foto Bukti (Petugas)
# ─────────────────────────────────────────────
async def upload_foto_tool(report_id: int, foto_url: str, telegram_id: int) -> dict:
    """
    Upload photo evidence for a completed report. Petugas only.
    foto_url can be file_id from Telegram photo or a URL.
    """
    if not await is_petugas(telegram_id):
        return {
            "success": False,
            "message": "❌ Anda belum terdaftar sebagai petugas.\nGunakan /start untuk mendaftar."
        }
    
    report = await get_report_by_id(report_id)
    if not report:
        return {
            "success": False,
            "message": f"❌ Laporan #{report_id} tidak ditemukan."
        }
    
    foto = await add_foto_bukti(report_id, foto_url)

    # NOTE: laporan.foto is already updated by backend's /api/laporan/<id>/foto
    # which saves the static file and sets the proper static URL.
    # We only store file_id in foto_bukti for Telegram reference.

    return {
        "success": True,
        "message": (
            f"📸 Foto bukti berhasil diupload!\n\n"
            f"📋 Laporan: #{report_id}\n"
            f"🖼️ Foto ID: {foto['id']}\n\n"
            f"Warga bisa melihat foto ini saat cek laporan di website."
        ),
        "data": foto
    }

# ─────────────────────────────────────────────
# TOOL: List Pending (Petugas)
# ─────────────────────────────────────────────
async def list_pending_tool(telegram_id: int) -> dict:
    """
    List all pending reports for petugas. Petugas only.
    """
    if not await is_petugas(telegram_id):
        return {
            "success": False,
            "message": "❌ Anda belum terdaftar sebagai petugas.\nGunakan /start untuk mendaftar."
        }
    
    pending = await get_pending_reports()
    
    if not pending:
        return {
            "success": True,
            "message": "✅ Tidak ada laporan yang menunggu."
        }
    
    lines = [f"📋 DAFTAR MENUNGGU ({len(pending)} laporan)\n"]
    lines.append("━━━━━━━━━━━━━━━━━━━━\n")
    
    for r in pending:
        prioritas_emoji = "🔴" if r.get('prioritas') == 'Tinggi' else "🟡" if r.get('prioritas') == 'Sedang' else "🟢"
        lines.append(
            f"#{r['id']} {prioritas_emoji} | {r.get('nama', 'Anon')} | {r.get('lokasi', '-')} | {r.get('tanggal', '-')}"
        )
    
    lines.append("\nKetik /task untuk ambil tugas pertama.")
    
    return {
        "success": True,
        "message": "\n".join(lines),
        "data": pending
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