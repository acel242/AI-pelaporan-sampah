import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from agent import GoBcaEnvAgent
from database import init_db, ensure_user

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

agent = GoBcaEnvAgent()

# ─────────────────────────────────────────────
# Command Handlers
# ─────────────────────────────────────────────
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await ensure_user(user.id, user.username or user.first_name or "unknown")
    
    await update.message.reply_text(
        "👋 Halo! Saya GoBcaEnv, asisten pelaporan sampah EcoLapor.\n\n"
        "📝 Fitur:\n"
        "• Laporkan sampah liar di sekitarmu\n"
        "• Cek status laporanmu\n"
        "• Admin: Kelola semua laporan\n\n"
        "Ketik /help untuk panduan lengkap."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Panduan GoBcaEnv\n\n"
        "━━━━━━━━ WARGA ━━━━━━━━\n"
        "1. **Laporkan Sampah**\n"
        "   Ceritakan lokasi & deskripsi\n"
        "   Contoh: 'Ada tumpukan sampah di Jl. Sam Ratulangi no 45'\n\n"
        "2. **Cek Laporan Saya**\n"
        "   Ketik: 'cek laporan saya'\n\n"
        "━━━━━━━━ ADMIN ━━━━━━━━\n"
        "• /stats - Statistik laporan\n"
        "• /all - Semua laporan\n"
        "• /search <kata> - Cari laporan\n"
        "• /priority <id> <tinggi/sedang/rendah> - Set prioritas\n"
        "• /note <id> <catatan> - Tambah catatan\n"
        "• /bulk <ids> <status> - Update banyak\n"
        "• /auto <id> <template> - Auto respond"
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from tools import get_statistics_tool
    user_id = update.effective_user.id
    
    if not agent.is_admin(user_id):
        await update.message.reply_text("❌ Hanya admin yang bisa melihat statistik.")
        return
    
    result = await get_statistics_tool()
    await update.message.reply_text(result["message"])

async def all_reports_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from tools import get_all_reports_tool
    user_id = update.effective_user.id
    
    if not agent.is_admin(user_id):
        await update.message.reply_text("❌ Hanya admin.")
        return
    
    status = None
    prioritas = None
    
    # Parse optional filters from args
    args = context.args
    if args:
        if args[0].lower() in ['menunggu', 'diproses', 'selesai']:
            status = args[0].capitalize()
        if len(args) > 1 and args[1].lower() in ['tinggi', 'sedang', 'rendah']:
            prioritas = args[1].capitalize()
    
    result = await get_all_reports_tool(status=status, prioritas=prioritas)
    await update.message.reply_text(result["message"])

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        
        # Normalize
        priority_map = {"tinggi": "Tinggi", "sedang": "Sedang", "rendah": "Rendah", "high": "Tinggi", "medium": "Sedang", "low": "Rendah"}
        prioritas = priority_map.get(prioritas.lower(), prioritas.capitalize())
        
        if prioritas not in ["Tinggi", "Sedang", "Rendah"]:
            await update.message.reply_text("❌ Prioritas harus: tinggi, sedang, rendah")
            return
        
        result = await set_priority_tool(report_id, prioritas)
        await update.message.reply_text(result["message"])
    except ValueError:
        await update.message.reply_text("❌ ID harus angka. Contoh: /priority 5 tinggi")

async def note_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

# ─────────────────────────────────────────────
# Message Handler
# ─────────────────────────────────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.message.text
    
    logger.info(f"Message from {user.username} (ID:{user.id}): {message}")
    
    await ensure_user(user.id, user.username or user.first_name or "unknown")
    
    try:
        response = await agent.process(message, user.id, user.username or user.first_name or "unknown")
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await update.message.reply_text("❌ Maaf, terjadi kesalahan. Silakan coba lagi.")

# ─────────────────────────────────────────────
# Post Init
# ─────────────────────────────────────────────
async def post_init(application: Application):
    await init_db()
    logger.info("Database initialized")
    logger.info(f"Admin IDs: {agent.admin_user_ids}")

# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
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
    
    # Commands
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("all", all_reports_command))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("priority", priority_command))
    application.add_handler(CommandHandler("note", note_command))
    application.add_handler(CommandHandler("bulk", bulk_command))
    application.add_handler(CommandHandler("auto", auto_command))
    
    # Messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("GoBcaEnv bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
