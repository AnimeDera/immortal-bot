import hashlib
import os
from pyrogram import Client, filters
from dotenv import load_dotenv
from database import db

load_dotenv()

# बॉट को चालू करना
app = Client(
    "ImmortalBot",
    api_id=int(os.getenv("API_ID")),
    api_hash=os.getenv("API_HASH"),
    bot_token=os.getenv("BOT_TOKEN")
)

def generate_hash(file_name):
    """फाइल के लिए एक यूनिक आईडी (Hash) बनाना"""
    return hashlib.md5(file_name.encode()).hexdigest()

@app.on_message(filters.document | filters.video)
async def process_video(client, message):
    msg = await message.reply("⏳ प्रोसेसिंग हो रही है, कृपया रुकें...")
    
    file = message.document or message.video
    file_name = file.file_name
    
    # 1. यूनिक आईडी (Hash) बनाना
    file_hash = generate_hash(file_name)
    
    # 2. स्टोरेज चैनल में फाइल की कॉपी भेजना
    storage_channel = int(os.getenv("CHANNEL_ID"))
    copied_msg = await message.copy(storage_channel)
    
    # 3. डेटाबेस (MongoDB) में सब कुछ याद रखना
    file_data = {
        "name": file_name,
        "mirrors": [
            {"channel_id": storage_channel, "msg_id": copied_msg.id}
        ]
    }
    await db.save_file(file_hash, file_data)
    
    # 4. यूजर को लिंक देना
    final_link = f"{os.getenv('CF_DOMAIN')}/watch/{file_hash}"
    await msg.edit(f"✅ **फाइल सेव हो गई!**\n\n📂 नाम: `{file_name}`\n🔗 लिंक: {final_link}")

print("🚀 बॉट अब ऑनलाइन है!")
app.run()