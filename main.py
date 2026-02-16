import hashlib
import os
import asyncio
from pyrogram import Client, filters
from dotenv import load_dotenv
from database import db
from aiohttp import web

load_dotenv()

# --- KOYEB PORT FIX (8080 Standard Port) ---
async def handle(request):
    return web.Response(text="Bot is Alive and Running on Standard Port 8080!")

async def start_web_server():
    server = web.Application()
    server.router.add_get("/", handle)
    runner = web.AppRunner(server)
    await runner.setup()
    # यहाँ हमने 8080 सेट कर दिया है
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    print("🌍 Web Server started on standard port 8080")

# --- टेलीग्राम बॉट ---
app = Client(
    "ImmortalBot",
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN")
)

def generate_hash(file_name):
    return hashlib.md5(file_name.encode()).hexdigest()

@app.on_message(filters.document | filters.video)
async def process_video(client, message):
    try:
        msg = await message.reply("⚡️ प्रोसेसिंग शुरू हो रही है...")
        file = message.document or message.video
        file_name = file.file_name
        file_hash = generate_hash(file_name)
        
        storage_channel = int(os.getenv("CHANNEL_ID"))
        copied_msg = await message.copy(storage_channel)
        
        file_data = {
            "name": file_name,
            "mirrors": [{"channel_id": storage_channel, "msg_id": copied_msg.id}]
        }
        await db.save_file(file_hash, file_data)
        
        final_link = f"{os.getenv('CF_DOMAIN')}/watch/{file_hash}"
        await msg.edit(f"✅ **फाइल सुरक्षित सेव हो गई!**\n\n📂 नाम: `{file_name}`\n🔗 लिंक: {final_link}")
    except Exception as e:
        print(f"Error: {e}")

async def run_everything():
    await start_web_server()
    await app.start()
    print("🚀 इम्मोर्टल बॉट ऑनलाइन है!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_everything())
