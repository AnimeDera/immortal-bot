import os
import asyncio
from telethon import TelegramClient, utils
from flask import Flask, Response, request, render_template_string
from threading import Thread

# --- CONFIGURATION (Environment Variables) ---
API_ID = int(os.environ.get("API_ID", 35954260))
API_HASH = os.environ.get("API_HASH", "6a374885ad2cc311a8f0f49ebc5b0042")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8597292378:AAFTPjLoSEKyipw0nY5CJmbnbcoA69JHIEM")

app = Flask(__name__)
client = TelegramClient('bot_session', API_ID, API_HASH)

# HTML Player Interface
PLAYER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Immortal HD Player</title>
    <style>
        body { margin: 0; background: #000; color: #fff; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; font-family: sans-serif; }
        .player-container { width: 100%; max-width: 800px; background: #111; border-radius: 10px; overflow: hidden; border: 2px solid #ff0000; }
        video { width: 100%; display: block; }
        h1 { color: #ff0000; text-transform: uppercase; letter-spacing: 2px; }
    </style>
</head>
<body>
    <h1>IMMORTAL PLAYER</h1>
    <div class="player-container">
        <video controls autoplay preload="auto">
            <source src="/stream/{{ file_id }}" type="video/mp4">
        </video>
    </div>
</body>
</html>
"""

@app.route('/watch/<file_id>')
def watch(file_id):
    return render_template_string(PLAYER_HTML, file_id=file_id)

@app.route('/stream/<file_id>')
def stream_video(file_id):
    async def generate():
        # टेलीग्राम से फाइल के चंक्स (टुकड़े) प्राप्त करना
        async with client:
            # हम सीधे टेलीग्राम के गेट-फाइल सिस्टम का उपयोग करते हैं
            # नोट: यह हिस्सा आपके डेटाबेस की फाइल आईडी से जुड़ा होना चाहिए
            # अभी के लिए यह एक बेसिक स्ट्रक्चर है
            try:
                # यहाँ फाइल को छोटे टुकड़ों (1MB) में स्ट्रीम किया जाता है
                async for chunk in client.download_iter(file_id, chunk_size=1024*1024):
                    yield chunk
            except Exception as e:
                print(f"Error: {e}")

    return Response(generate(), mimetype='video/mp4')

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    # Flask को अलग थ्रेड में चलाना ताकि Telethon और Flask दोनों चलें
    t = Thread(target=run_flask)
    t.start()
    client.start(bot_token=BOT_TOKEN)
    client.run_until_disconnected()
