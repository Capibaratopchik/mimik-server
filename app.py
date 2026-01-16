from flask import Flask, request, Response, jsonify
import yt_dlp
import requests

app = Flask(__name__)

ydl_opts = {
    'format': 'bestaudio[ext=m4a]/best[ext=mp4]/best', # M4A/AAC лучше всего для ESP
    'noplaylist': True,
    'quiet': True,
    'default_search': 'ytsearch',
    'socket_timeout': 10,
    'nocheckcertificate': True,
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'ios']
        }
    },
    'force_ipv4': True
}

@app.route('/')
def home():
    return "Mimik Proxy Server is Running!"

@app.route('/play')
def play_music():
    query = request.args.get('q')
    if not query:
        return "No query", 400
    
    try:
        # 1. Получаем прямую ссылку от YouTube
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Searching: {query}")
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            
            if 'entries' not in info or len(info['entries']) == 0:
                return "Not found", 404
            
            video_data = info['entries'][0]
            audio_url = video_data.get('url')
            print(f"Proxying: {video_data.get('title')}")

        # 2. Подключаемся к YouTube сами (как сервер)
        # stream=True важно - мы не качаем файл в память, а читаем поток
        req = requests.get(audio_url, stream=True, timeout=10)

        # 3. Функция-генератор, которая отдает данные кусочками
        def generate():
            for chunk in req.iter_content(chunk_size=4096):
                if chunk:
                    yield chunk

        # 4. Отдаем ответ ESP32 как непрерывный поток
        return Response(generate(), headers={
            'Content-Type': 'audio/mp4', # Или audio/aac
            'Content-Disposition': 'inline; filename="music.m4a"'
        })

    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
