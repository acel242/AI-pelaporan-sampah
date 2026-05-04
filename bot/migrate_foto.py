import asyncio
import aiosqlite
import os
from telegram import Bot
from io import BytesIO
from datetime import datetime

# Load token from .env
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "pelaporan.db")
FOTO_DIR = os.path.join(os.path.dirname(__file__), '..', 'backend', 'static', 'foto')

async def migrate():
    bot = Bot(TOKEN)
    os.makedirs(FOTO_DIR, exist_ok=True)
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM foto_bukti WHERE foto_url LIKE 'AgAC%'") as cursor:
            rows = await cursor.fetchall()
        
        print(f"Found {len(rows)} file_id entries to migrate")
        
        for row in rows:
            file_id = row['foto_url']
            laporan_id = row['laporan_id']
            old_id = row['id']
            
            print(f"Processing ID {old_id} (Laporan #{laporan_id})...")
            
            try:
                # Download from Telegram
                tg_file = await bot.get_file(file_id)
                buffer = BytesIO()
                await tg_file.download_to_memory(out=buffer)
                buffer.seek(0)
                image_data = buffer.read()
                
                # Save locally
                filename = f"bukti_{laporan_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                filepath = os.path.join(FOTO_DIR, filename)
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                
                file_url = f"/static/foto/{filename}"
                
                # Update database
                await db.execute(
                    "UPDATE foto_bukti SET foto_url = ? WHERE id = ?",
                    (file_url, old_id)
                )
                await db.commit()
                
                print(f"✅ Migrated to: {file_url}")
                
            except Exception as e:
                print(f"❌ Failed to migrate ID {old_id}: {e}")
    
    print("Migration complete!")

if __name__ == "__main__":
    asyncio.run(migrate())
