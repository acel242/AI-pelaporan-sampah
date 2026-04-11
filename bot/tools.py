from database import (
    submit_report as db_submit_report,
    get_reports,
    get_all_reports,
    update_report_status,
    create_user,
    get_user,
)

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
        "message": f"✅ Laporan berhasil dikirim!\n\n📋 ID Laporan: #{result['id']}\n📍 Lokasi: {lokasi}\n📝 Status: Menunggu\n\nTim kami akan segera menindaklanjuti.",
        "data": result
    }

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

async def get_all_reports_tool() -> dict:
    """
    Get all reports in the system. Admin only.
    Use this when admin wants to see all reports.
    """
    reports = await get_all_reports()
    if not reports:
        return {
            "success": True,
            "message": "📭 Belum ada laporan masuk.",
            "data": []
        }
    
    menunggu = sum(1 for r in reports if r['status'] == 'Menunggu')
    selesai = sum(1 for r in reports if r['status'] == 'Selesai')
    
    lines = [f"📊 Statistik: {len(reports)} Total | {menunggu} Menunggu | {selesai} Selesai\n"]
    lines.append("\n📋 Laporan:\n")
    for r in reports[:20]:
        lines.append(f"#{r['id']} | {r['nama']} | {r['lokasi']} | {r['status']} | {r['tanggal']}")
    
    return {
        "success": True,
        "message": "\n".join(lines),
        "data": reports
    }

async def update_status_tool(report_id: int, status: str) -> dict:
    """
    Update the status of a report. Admin only.
    Status options: 'Menunggu' or 'Selesai'.
    """
    valid_statuses = ['Menunggu', 'Selesai']
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

async def ensure_user(user_id: int, username: str) -> dict:
    """Ensure user exists in database."""
    user = await get_user(user_id)
    if not user:
        await create_user(user_id, username)
        user = await get_user(user_id)
    return user
