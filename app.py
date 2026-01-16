from flask import Flask, request, redirect, jsonify
import yt_dlp
import os

app = Flask(__name__)

# Проверка наличия куки
if os.path.exists('cookies.txt'):
    print("Cookies file found!")
else:
    print("WARNING: cookies.txt NOT FOUND! Authorization may fail.")

ydl_opts = {
    # === ИСПРАВЛЕНИЕ ОШИБКИ ФОРМАТА ===
    # Мы просим формат 140 (это стандартный AAC 128kbps, который есть везде).
    # Если его нет - любой m4a. Если нет - mp4. И только в конце - любой best.
    'format': '140/bestaudio[ext=m4a]/best[ext=mp4]/best',
    
    'noplaylist': True,
    'quiet': True,
    'default_search': 'ytsearch',
    'socket_timeout': 10,
    'cookiefile': 'cookies.txt', 
    
    # Оставляем маскировку
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'web']
        }
    }
}

@app.route('/')
def home():
    return "Mimik Server (Final AAC Version) is Running!"

@app.route('/play')
def play_music():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Searching: {query}")
            # download=False означает "дай мне информацию, но не качай файл на диск"
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            
            if 'entries' in info and len(info['entries']) > 0:
                video_data = info['entries'][0]
                audio_url = video_data.get('url')
                title = video_data.get('title', 'Unknown')
                
                print(f"Found: {title}")
                print(f"URL: {audio_url[:50]}...") # Лог начала ссылки
                
                if audio_url:
                    return redirect(audio_url, code=302)
                else:
                    return jsonify({"error": "No URL found in video data"}), 404
            else:
                return jsonify({"error": "Nothing found"}), 404
                
    except Exception as e:
        print(f"ERROR: {e}")
        # Выводим ошибку текстом, чтобы было понятно
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
