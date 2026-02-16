import os
import re
from telethon import TelegramClient
from flask import Flask, Response, request, render_template_string
from pymongo import MongoClient

# --- CONFIGURATION ---
API_ID = 35954260
API_HASH = '6a374885ad2cc311a8f0f49ebc5b0042'
BOT_TOKEN = '8597292378:AAFTPjLoSEKyipw0nY5CJmbnbcoA69JHIEM'
MONGO_URL = "mongodb+srv://dineshmotis226:dineshmotis226@cluster.6txxwre.mongodb.net/?appName=Cluster"

app = Flask(__name__)
client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# HTML Player Template
PLAYER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Immortal Pro Player</title>
    <style>
        body { margin: 0; background: #000; color: #fff; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; }
        .video-box { width: 95%; max-width: 850px; border: 1px solid #ff0000; border-radius: 10px; overflow: hidden; }
        video { width: 100%; display: block; }
        h1 { color: #ff0000; font-family: sans-serif; }
    </style>
</head>
<body>
    <h1>IMMORTAL STREAMER</h1>
    <div class="video-box">
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
async def stream_video(file_id):
    # यह हिस्सा टेलीग्राम से "Chunks" में डेटा खींचता है
    try:
        # यहाँ हम File ID से मैसेज ढूंढते हैं
        # नोट: असली बॉट में हम DB से मैसेज आईडी लेते हैं, 
        # यहाँ हम सीधे फाइल आईडी को स्ट्रीम करने की कोशिश कर रहे हैं
        file_msg = await client.get_messages(None, ids=int(file_id)) # सरलीकरण के लिए
        
        async def generate():
            async for chunk in client.download_iter(file_msg.media):
                yield chunk
        
        return Response(generate(), mimetype='video/mp4')
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    # Koyeb requires port 8080 or the PORT env variable
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
