import os
import asyncio
import logging
import base64
from dotenv import load_dotenv

load_dotenv()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from agent import SmartAgent
from database import init_db, create_user as ensure_user, get_conv_state, set_conv_state, clear_conv_state, is_petugas

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

agent = SmartAgent()

ADMIN_PASSWORD = os.getenv("ADMIN_REGISTRATION_PASSWORD", "ecolapor2026")
STATE_AWAITING_PASSWORD = "awaiting_password"

# In-memory pending foto uploads: user_id -> report_id
_pending_foto_uploads: dict[int, int] = {}

# ─────────────────────────────────────────────
# Command Handlers
# ─────────────────────────────────────────────
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start - password gate before registration."""
    user = update.effective_user
    await ensure_user(user.id, user.username or user.first_name or "unknown")

    if await is_petugas(user.id):
        await update.message.reply_text(
            "👋 Halo petugas! Anda sudah terdaftar.\n\n"
            "Command tersedia:\n"
            "/task - Ambil 1 tugas\n"
            "/list - Lihat semua pending\n"
            "/done <id> <catatan> - Tandai selesai\n"
            "/foto <id> - Upload foto bukti\n"
            "/stats - Statistik\n\n"
            "Ketik /help untuk bantuan."
        )
        return

    state = await get_conv_state(user.id)
    if state == STATE_AWAITING_PASSWORD:
        await update.message.reply_text(
            "🔐 Masih menunggu password. Silakan masukkan password admin:\n"
            "Contoh: ecolapor2026"
        )
        return

    await set_conv_state(user.id, STATE_AWAITING_PASSWORD)
    await update.message.reply_text(
        "🔐 EcoLapor Petugas Registration\n\n"
        "Masukkan password admin untuk mendaftar sebagai petugas:\n"
        "Minimal 6 karakter"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    from tools import is_petugas

    is_petugas_user = await is_petugas(user_id)
    is_admin_user = agent.is_admin(user_id)

    if is_petugas_user or is_admin_user:
        await update.message.reply_text(
            "📖 Panduan EcoLapor AI - PETUGAS\n\n"
            "━━━━━━━━ PETUGAS ━━━━━━━━\n"
            "/task - Ambil 1 tugas\n"
            "/list - Lihat semua laporan pending\n"
            "/done <id> <catatan> - Tandai selesai\n"
            "/foto <id> - Upload foto bukti\n"
            "/stats - Statistik harian\n\n"
            "━━━━━━━━ ADMIN ━━━━━━━━\n"
            "/all - Semua laporan\n"
            "/search <kata> - Cari laporan\n"
            "/priority <id> <tinggi/sedang/rendah> - Set prioritas\n"
            "/note <id> <catatan> - Tambah catatan\n"
            "/bulk <ids> <status> - Update banyak"
        )
    else:
        await update.message.reply_text(
            "👋 Halo! Saya EcoLapor AI.\n\n"
            "Saya adalah asisten pelaporan lingkungan untuk warga Manado.\n\n"
            "Cara pakai: Cukup ceritakan lokasi dan kondisi lingkungan yang ingin Anda laporkan.\n\n"
            "Contoh: 'Ada tumpukan sampah di Jl. Sam Ratulangi dekat lampu merah'\n"
            "Contoh: 'Drainase tersumbat di Jl. Katamso, banjir lagi'"
        )

async def task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /task - get one task for petugas. Optional: /task <id> for specific task."""
    from tools import get_task_tool
    user_id = update.effective_user.id

    # If a specific task ID is provided
    if context.args and context.args[0]:
        try:
            task_id = int(context.args[0])
            result = await get_task_tool(user_id, task_id=task_id)
        except ValueError:
            await update.message.reply_text("❌ ID harus angka. Contoh: /task 29")
            return
    else:
        result = await get_task_tool(user_id)

    await update.message.reply_text(result["message"])

async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /list - list all pending for petugas."""
    from tools import list_pending_tool
    user_id = update.effective_user.id
    result = await list_pending_tool(user_id)
    await update.message.reply_text(result["message"])

async def done_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /done <id> <catatan> - mark as completed."""
    from tools import mark_done_tool
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text(
            "❌ Format: /done <id> <catatan>\n"
            "Contoh: /done 5 Sudah dibersihkan pagi ini"
        )
        return

    try:
        report_id = int(context.args[0])
        catatan = " ".join(context.args[1:]) if len(context.args) > 1 else ""
        result = await mark_done_tool(report_id, catatan, user_id)
        await update.message.reply_text(result["message"])
    except ValueError:
        await update.message.reply_text("❌ ID harus angka. Contoh: /done 5 catatan aqui")

async def foto_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /foto <id> - enter photo upload mode."""
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text(
            "📸 Format: /foto <id>\n"
            "Contoh: /foto 5\n\n"
            "Setelah itu, KIRIM FOTO sebagai pesan baru (tanpa command)."
        )
        return

    try:
        report_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ ID harus angka. Contoh: /foto 5")
        return

    _pending_foto_uploads[user_id] = report_id
    await update.message.reply_text(
        f"📸 Mode upload aktif untuk laporan #{report_id}.\n"
        "Kirim foto sekarang (tanpa command)."
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats - show statistics."""
    from tools import get_statistics_tool
    result = await get_statistics_tool()
    await update.message.reply_text(result["message"])

async def all_reports_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /all - show all reports. Admin only."""
    from tools import get_all_reports_tool
    user_id = update.effective_user.id

    if not agent.is_admin(user_id):
        await update.message.reply_text("❌ Hanya admin.")
        return

    status = None
    prioritas = None

    args = context.args
    if args:
        if args[0].lower() in ['menunggu', 'diproses', 'selesai']:
            status = args[0].capitalize()
        if len(args) > 1 and args[1].lower() in ['tinggi', 'sedang', 'rendah']:
            prioritas = args[1].capitalize()

    result = await get_all_reports_tool(status=status, prioritas=prioritas)
    await update.message.reply_text(result["message"])

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /search - search reports. Admin only."""
    from tools import search_reports_tool
    user_id = update.effective_user.id

    if not agent.is_admin(user_id):
        await update.message.reply_text("❌ Hanya admin.")
        return

    if not context.args:
        await update.message.reply_text("❌ Format: /search <kata kunci>\nContoh: /search Gatot Subroto")
        return

    query = " ".join(context.args)
    result = await search_reports_tool(query)
    await update.message.reply_text(result["message"])

async def priority_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /priority - set priority. Admin only."""
    from tools import set_priority_tool
    user_id = update.effective_user.id

    if not agent.is_admin(user_id):
        await update.message.reply_text("❌ Hanya admin.")
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ Format: /priority <id> <tinggi|sedang|rendah>\n"
            "Contoh: /priority 5 tinggi"
        )
        return

    try:
        report_id = int(context.args[0])
        prioritas = context.args[1].lower()

        priority_map = {"tinggi": "Tinggi", "sedang": "Sedang", "rendah": "Rendah",
                        "high": "Tinggi", "medium": "Sedang", "low": "Rendah"}
        prioritas = priority_map.get(prioritas.lower(), prioritas.capitalize())

        if prioritas not in ["Tinggi", "Sedang", "Rendah"]:
            await update.message.reply_text("❌ Prioritas harus: tinggi, sedang, rendah")
            return

        result = await set_priority_tool(report_id, prioritas)
        await update.message.reply_text(result["message"])
    except ValueError:
        await update.message.reply_text("❌ ID harus angka. Contoh: /priority 5 tinggi")

async def note_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /note - add note. Admin only."""
    from tools import add_note_tool
    user_id = update.effective_user.id

    if not agent.is_admin(user_id):
        await update.message.reply_text("❌ Hanya admin.")
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ Format: /note <id> <catatan>\n"
            "Contoh: /note 5 Sudah dikoordinasikan dengan Dinas LH"
        )
        return

    try:
        report_id = int(context.args[0])
        catatan = " ".join(context.args[1:])
        result = await add_note_tool(report_id, catatan)
        await update.message.reply_text(result["message"])
    except ValueError:
        await update.message.reply_text("❌ ID harus angka. Contoh: /note 5 catatan aqui")

async def bulk_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /bulk - bulk update. Admin only."""
    from tools import bulk_update_status_tool
    user_id = update.effective_user.id

    if not agent.is_admin(user_id):
        await update.message.reply_text("❌ Hanya admin.")
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ Format: /bulk <id1,id2,id3> <status>\n"
            "Contoh: /bulk 1,2,3 Selesai"
        )
        return

    ids_str = context.args[0].split(",")
    try:
        report_ids = [int(x.strip()) for x in ids_str]
        status = context.args[1].capitalize()

        if status not in ["Menunggu", "Diproses", "Selesai"]:
            await update.message.reply_text("❌ Status: Menunggu, Diproses, Selesai")
            return

        result = await bulk_update_status_tool(report_ids, status)
        await update.message.reply_text(result["message"])
    except ValueError:
        await update.message.reply_text("❌ Format ID salah. Contoh: /bulk 1,2,3 Selesai")

async def auto_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /auto - auto respond template. Admin only."""
    from tools import auto_respond_tool
    user_id = update.effective_user.id

    if not agent.is_admin(user_id):
        await update.message.reply_text("❌ Hanya admin.")
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ Format: /auto <id> <template>\n"
            "Template: accepted, processing, completed, rejected\n"
            "Contoh: /auto 5 completed"
        )
        return

    try:
        report_id = int(context.args[0])
        template = context.args[1].lower()
        result = await auto_respond_tool(report_id, template)
        await update.message.reply_text(result["message"])
    except ValueError:
        await update.message.reply_text("❌ ID harus angka. Contoh: /auto 5 completed")

async def handle_photo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo messages - check if waiting for foto upload."""
    user = update.effective_user

    report_id = _pending_foto_uploads.get(user.id)
    if not report_id:
        await update.message.reply_text(
            "📸 Foto diterima! Untuk laporan warga, silakan gunakan website:\n"
            "https://eco-lapor.43.157.235.76.nip.io\n\n"
            "Untuk petugas: Gunakan /foto <id> dulu, baru kirim foto."
        )
        return

    photo = update.message.photo[-1]
    file_id = photo.file_id

    # Download photo from Telegram and convert to base64
    try:
        from io import BytesIO
        tg_file = await context.bot.get_file(file_id)
        buffer = BytesIO()
        await tg_file.download_to_memory(out=buffer)
        buffer.seek(0)
        foto_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        foto_data_uri = f"data:image/jpeg;base64,{foto_base64}"
    except Exception as e:
        logger.error(f"Failed to download Telegram photo: {e}")
        await update.message.reply_text("❌ Gagal download foto. Coba lagi.")
        return

    # Store in foto_bukti table ONLY - do NOT overwrite warga's original photo
    # The bukti photo is separate from the warga's submission photo
    from tools import upload_foto_tool
    result = await upload_foto_tool(report_id, file_id, user.id)

    del _pending_foto_uploads[user.id]
    await update.message.reply_text(result["message"])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message.text

    logger.info(f"Message from {user.username} (ID:{user.id}): {message}")

    await ensure_user(user.id, user.username or user.first_name or "unknown")

    state = await get_conv_state(user.id)
    if state == STATE_AWAITING_PASSWORD:
        if message == ADMIN_PASSWORD:
            await clear_conv_state(user.id)
            from tools import register_petugas_tool
            await register_petugas_tool(user.id, user.first_name or "Petugas")
            await update.message.reply_text(
                f"✅ Password benar! Selamat datang, {user.first_name or 'Petugas'}!\n\n"
                f"Anda terdaftar sebagai petugas DLH.\n\n"
                f"Command:\n"
                f"/task - Ambil 1 tugas\n"
                f"/list - Lihat semua pending\n"
                f"/done <id> <catatan> - Tandai selesai\n"
                f"/foto <id> - Upload foto bukti\n"
                f"/stats - Statistik\n\n"
                f"Ketik /help untuk bantuan."
            )
        else:
            await update.message.reply_text(
                "❌ Password salah. Silakan coba lagi:\n"
                "Ketik /start untuk mulai ulang."
            )
        return

    try:
        response = await agent.process(message, user.id, user.username or user.first_name or "unknown")
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        await update.message.reply_text("❌ Maaf, terjadi kesalahan. Silakan coba lagi.")

async def post_init(application: Application):
    await init_db()
    logger.info("Database initialized")
    admin_ids = os.getenv("ADMIN_USER_IDS", "1254636239")
    logger.info(f"Admin IDs: {admin_ids}")

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return

    application = (
        Application.builder()
        .token(token)
        .post_init(post_init)
        .build()
    )

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("task", task_command))
    application.add_handler(CommandHandler("list", list_command))
    application.add_handler(CommandHandler("done", done_command))
    application.add_handler(CommandHandler("foto", foto_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("all", all_reports_command))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("priority", priority_command))
    application.add_handler(CommandHandler("note", note_command))
    application.add_handler(CommandHandler("bulk", bulk_command))
    application.add_handler(CommandHandler("auto", auto_command))

    application.add_handler(MessageHandler(
        filters.PHOTO & ~filters.COMMAND,
        handle_photo_message
    ))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("EcoLapor AI bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
