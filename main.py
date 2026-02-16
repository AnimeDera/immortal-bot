import os
from telethon import TelegramClient, events
from flask import Flask, Response, render_template_string
from threading import Thread

# --- CONFIG ---
API_ID = 35954260
API_HASH = '6a374885ad2cc311a8f0f49ebc5b0042'
BOT_TOKEN = '8597292378:AAFTPjLoSEKyipw0nY5CJmbnbcoA69JHIEM'
DOMAIN = os.environ.get("CF_DOMAIN")

app = Flask(__name__)
client = TelegramClient('bot_session', API_ID, API_HASH)

@client.on(events.NewMessage(func=lambda e: e.video or e.document))
async def handle_media(event):
    # यहाँ हम Message ID का उपयोग कर रहे हैं जो कभी फेल नहीं होती
    msg_id = event.message.id
    chat_id = event.chat_id
    stream_url = f"https://{DOMAIN}/watch/{chat_id}/{msg_id}"
    await event.reply(f"🎬 **Video is Ready to Stream!**\n\n**Link:** {stream_url}")

@app.route('/watch/<chat_id>/<msg_id>')
def watch(chat_id, msg_id):
    return render_template_string("""
        <html><head><title>Immortal Player</title></head>
        <body style="margin:0;background:#000;display:flex;justify-content:center;align-items:center;height:100vh;">
        <video controls autoplay style="width:95%;max-width:850px;border:2px solid red;">
        <source src="/stream/{{c}}/{{m}}" type="video/mp4"></video></body></html>
    """, c=chat_id, m=msg_id)

@app.route('/stream/<chat_id>/<msg_id>')
async def stream(chat_id, msg_id):
    async def generate():
        async with client:
            # यह हिस्सा टेलीग्राम से सीधा 'Live' डेटा खींचेगा
            message = await client.get_messages(int(chat_id), ids=int(msg_id))
            async for chunk in client.download_iter(message.media):
                yield chunk
    return Response(generate(), mimetype='video/mp4')

if __name__ == '__main__':
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
    client.start(bot_token=BOT_TOKEN)
    client.run_until_disconnected()
