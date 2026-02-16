import os
import asyncio
from telethon import TelegramClient, events
from flask import Flask, Response, render_template_string
from threading import Thread

# --- CONFIGURATION ---
API_ID = 35954260
API_HASH = '6a374885ad2cc311a8f0f49ebc5b0042'
BOT_TOKEN = '8597292378:AAFTPjLoSEKyipw0nY5CJmbnbcoA69JHIEM'
# Koyeb URL (बिना https:// के)
DOMAIN = os.environ.get("CF_DOMAIN", "your-app.koyeb.app") 

app = Flask(__name__)
client = TelegramClient('bot_session', API_ID, API_HASH)

# 1. PLAYER HTML
PLAYER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Immortal Player</title>
    <style>
        body { margin: 0; background: #000; display: flex; align-items: center; justify-content: center; height: 100vh; }
        video { width: 95%; max-width: 800px; border: 2px solid red; border-radius: 10px; }
    </style>
</head>
<body>
    <video controls autoplay><source src="/stream/{{ file_id }}" type="video/mp4"></video>
</body>
</html>
"""

# 2. BOT LOGIC (मैसेज सुनने के लिए)
@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("I am Alive! Send me a video to get a streaming link.")

@client.on(events.NewMessage(func=lambda e: e.video))
async def handle_video(event):
    file_id = event.message.video.id
    streaming_link = f"https://{DOMAIN}/watch/{file_id}"
    await event.reply(f"✅ **Video Processed!**\n\n**Streaming Link:**\n{streaming_link}")

# 3. STREAMING LOGIC
@app.route('/watch/<file_id>')
def watch(file_id):
    return render_template_string(PLAYER_HTML, file_id=file_id)

@app.route('/stream/<file_id>')
async def stream_video(file_id):
    # यह हिस्सा सीधा टेलीग्राम से डेटा खींचेगा
    async def generate():
        async for chunk in client.download_iter(file_id):
            yield chunk
    return Response(generate(), mimetype='video/mp4')

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == '__main__':
    t = Thread(target=run_flask)
    t.start()
    client.start(bot_token=BOT_TOKEN)
    print("Bot is listening...")
    client.run_until_disconnected()
