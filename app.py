from flask import Flask, request, Response, stream_with_context
import yt_dlp
import subprocess

app = Flask(__name__)

# Функция для получения прямой ссылки и стриминга через FFMPEG
def get_audio_stream(query):
    # Настройки yt-dlp для поиска
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch', # Искать на YouTube
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Ищем первое видео по запросу
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            if 'entries' in info:
                video_url = info['entries'][0]['url']
                title = info['entries'][0]['title']
                print(f"Found: {title}")
            else:
                return None

            # Запускаем FFMPEG для конвертации потока в MP3 на лету
            # ESP32 любит MP3, 44100Hz, 128k (или меньше для стабильности)
            command = [
                'ffmpeg',
                '-re', 
                '-i', video_url,
                '-f', 'mp3',
                '-acodec', 'libmp3lame',
                '-ab', '96k',   # Битрейт 96k (легче для WiFi ESP32)
                '-ac', '1',     # Моно (для одного динамика)
                '-ar', '44100', # Частота
                '-'
            ]

            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            
            return process.stdout
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route('/stream_music')
def stream_music():
    query = request.args.get('q')
    if not query:
        return "No query provided", 400

    print(f"Streaming request for: {query}")
    
    audio_stream = get_audio_stream(query)

    if not audio_stream:
        return "Error finding video", 404

    # Возвращаем потоковый ответ
    return Response(stream_with_context(audio_stream), mimetype="audio/mpeg")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
