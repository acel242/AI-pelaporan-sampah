import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
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

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await ensure_user(user.id, user.username or user.first_name or "unknown")
    
    await update.message.reply_text(
        "👋 Halo! Saya GoBcaEnv, asisten pelaporan sampah EcoLapor.\n\n"
        "Saya bisa membantu Anda:\n"
        "• 📝 Melaporkan tumpukan sampah liar\n"
        "• 📋 Mengecek status laporan Anda\n\n"
        "Cukup ceritakan lokasi dan deskripsi sampah yang ingin dilaporkan!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Cara Penggunaan:\n\n"
        "1. **Laporkan Sampah**\n"
        "   Ceritakan: lokasi dan deskripsi sampah\n"
        "   Contoh: 'Ada tumpukan sampah di Jl. Sam Ratulangi no 45, bau banget'\n\n"
        "2. **Cek Laporan**\n"
        "   Ketik: 'cek laporan saya'\n\n"
        "3. **Admin Only**\n"
        "   /all_reports - Lihat semua laporan\n"
        "   /update_status <id> <status> - Update status laporan"
    )

async def all_reports_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    from tools import get_all_reports_tool
    result = await get_all_reports_tool()
    await update.message.reply_text(result["message"])

async def update_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) < 2:
            await update.message.reply_text(
                "❌ Format: /update_status <id> <status>\n"
                "Contoh: /update_status 5 Selesai"
            )
            return
        
        report_id = int(args[0])
        status = args[1]
        
        from tools import update_status_tool
        result = await update_status_tool(report_id, status)
        await update.message.reply_text(result["message"])
    except ValueError:
        await update.message.reply_text("❌ ID harus angka. Contoh: /update_status 5 Selesai")

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
        await update.message.reply_text(
            "❌ Maaf, terjadi kesalahan. Silakan coba lagi."
        )

async def post_init(application: Application):
    await init_db()
    logger.info("Database initialized")

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
    application.add_handler(CommandHandler("all_reports", all_reports_command))
    application.add_handler(CommandHandler("update_status", update_status_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("GoBcaEnv bot starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
