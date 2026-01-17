from flask import Flask, request, redirect
import yt_dlp

app = Flask(__name__)

# Мы изменили путь с '/play' на '/music', чтобы исправить вашу ошибку 404
@app.route('/music')
def stream_music():
    query = request.args.get('q')
    if not query:
        return "No query provided", 400

    print(f"Searching for: {query}")

    # Опции: ищем лучшее аудио (m4a/aac), не скачиваем файл
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch',
        'expire': True, 
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # download=False критически важен, чтобы не качать файл на сервер
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            
            if 'entries' in info:
                video = info['entries'][0]
            else:
                video = info
            
            # Получаем прямую ссылку на поток
            audio_url = video.get('url')
            
            if not audio_url:
                return "Stream URL not found", 404

            print(f"Redirecting to: {audio_url[:50]}...")
            # Перенаправляем ESP32 прямо на сервера Google
            return redirect(audio_url, code=302)

    except Exception as e:
        print(f"Error: {e}")
        return f"Server Error: {e}", 500

if __name__ == '__main__':
    # 0.0.0.0 позволяет доступ с других устройств (ESP32) в сети
    app.run(host='0.0.0.0', port=8080)
