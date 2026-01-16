from flask import Flask, request, redirect, jsonify
import yt_dlp
import os

app = Flask(__name__)

if os.path.exists('cookies.txt'):
    print("Cookies file found!")
else:
    print("WARNING: cookies.txt NOT FOUND!")

ydl_opts = {
    # Просим 'm4a' (это AAC). Если нет - любой лучший аудиоформат.
    'format': 'bestaudio[ext=m4a]/best[ext=mp4]/best',
    
    'noplaylist': True,
    'quiet': True,
    'default_search': 'ytsearch',
    'socket_timeout': 10,
    
    # Используем куки
    'cookiefile': 'cookies.txt',
    
    # ВАЖНО: Мы УБРАЛИ 'extractor_args' (маскировку под Android).
    # Теперь yt-dlp будет использовать ваши куки как обычный браузер.
    # Это решит проблему "Format not available".
}

@app.route('/')
def home():
    return "Mimik Server (Browser Mode) is Running!"

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
