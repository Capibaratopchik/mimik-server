from flask import Flask, request, redirect, jsonify
import yt_dlp
import os

app = Flask(__name__)

if os.path.exists('cookies.txt'):
    print("Cookies file found!")
else:
    print("WARNING: cookies.txt NOT FOUND!")

ydl_opts = {
    # === ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ ===
    # 1. Мы просим формат 140 (это всегда прямой AAC поток).
    # 2. [protocol^=http] означает "протокол должен начинаться на http". 
    #    Это ИСКЛЮЧАЕТ форматы 'm3u8' и 'm3u8_native' (плейлисты).
    'format': '140[protocol^=http]/bestaudio[protocol^=http][ext=m4a]',
    
    'noplaylist': True,
    'quiet': True,
    'default_search': 'ytsearch',
    'socket_timeout': 10,
    'cookiefile': 'cookies.txt', 
}

@app.route('/')
def home():
    return "Mimik Server (Direct Stream Mode) is Running!"

@app.route('/play')
def play_music():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Searching: {query}")
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            
            if 'entries' in info and len(info['entries']) > 0:
                video_data = info['entries'][0]
                audio_url = video_data.get('url')
                title = video_data.get('title', 'Unknown')
                
                print(f"Found: {title}")
                print(f"Format: {video_data.get('format')}") # Пишем в лог какой формат выбрался
                
                if audio_url:
                    return redirect(audio_url, code=302)
                else:
                    return jsonify({"error": "No URL found"}), 404
            else:
                return jsonify({"error": "Nothing found"}), 404
                
    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
