from flask import Flask, request, redirect, jsonify
import yt_dlp

app = Flask(__name__)

# --- НАСТРОЙКИ НА ОСНОВЕ ВАШЕГО ПРИМЕРА ---
ydl_opts = {
    'format': 'bestaudio/best', # Ищем лучшее аудио
    'noplaylist': True,
    'quiet': True,
    'default_search': 'ytsearch',
    'socket_timeout': 10,
    
    # Отключаем проверку сертификатов (как в вашем примере)
    'nocheckcertificate': True,
    
    # Используем мобильные клиенты (как в вашем примере)
    # Это ключевой момент, почему ваш пример работает без куки
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'ios']
        }
    },
    
    # Принудительный IPv4 (чтобы избежать ошибок DNS на сервере)
    'force_ipv4': True
}

@app.route('/')
def home():
    return "Mimik Server (Mobile Client Mode) is Running!"

@app.route('/play')
def play_music():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Searching: {query}")
            
            # 1. Сначала получаем информацию о видео
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            
            if 'entries' in info and len(info['entries']) > 0:
                video_data = info['entries'][0]
                
                # 2. Ищем ссылку именно на аудио (m4a или mp4)
                # ESP32 не умеет WebM/Opus, поэтому нам нужно отфильтровать форматы
                formats = video_data.get('formats', [])
                target_url = None
                
                # Приоритет 1: формат 140 (AAC, m4a) - идеален для ESP32
                for f in formats:
                    if f.get('format_id') == '140':
                        target_url = f.get('url')
                        break
                
                # Приоритет 2: любой mp4 аудио
                if not target_url:
                    for f in formats:
                        if f.get('ext') == 'm4a' or f.get('ext') == 'mp4':
                            if f.get('acodec') != 'none': # Есть звук
                                target_url = f.get('url')
                                break
                
                # Приоритет 3: берем то, что yt-dlp считает 'url' по умолчанию
                if not target_url:
                    target_url = video_data.get('url')

                title = video_data.get('title', 'Unknown')
                print(f"Found: {title}")
                
                if target_url:
                    # Редирект на прямой поток
                    return redirect(target_url, code=302)
                else:
                    return jsonify({"error": "No suitable audio URL found"}), 404
            else:
                return jsonify({"error": "Nothing found"}), 404
                
    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
