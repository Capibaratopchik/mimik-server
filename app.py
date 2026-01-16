from flask import Flask, request, redirect, jsonify
import requests
import logging

app = Flask(__name__)

# Используем публичный инстанс Piped API
# Если этот будет медленным, можно заменить на https://api.piped.io
PIPED_API_URL = "https://pipedapi.kavin.rocks"

@app.route('/')
def home():
    return "Mimik Music Server (Piped API Version) is Running!"

@app.route('/play')
def play_music():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        # 1. Ищем видео по запросу
        print(f"Searching Piped for: {query}")
        search_url = f"{PIPED_API_URL}/search"
        params = {'q': query, 'filter': 'music_songs'} # Фильтр 'music_songs' ищет именно музыку
        
        r_search = requests.get(search_url, params=params, timeout=5)
        r_search.raise_for_status()
        results = r_search.json().get('items', [])
        
        if not results:
            # Если музыки не нашли, пробуем искать просто видео
            params = {'q': query, 'filter': 'videos'}
            r_search = requests.get(search_url, params=params, timeout=5)
            results = r_search.json().get('items', [])

        if not results:
             return jsonify({"error": "Nothing found"}), 404

        # Берем первый результат
        first_video = results[0]
        # Piped иногда возвращает ссылку вида "/watch?v=ID", нам нужен только ID
        video_id = first_video['url'].replace("/watch?v=", "")
        print(f"Found ID: {video_id} - {first_video.get('title')}")

        # 2. Получаем потоки (streams) для этого видео
        stream_url = f"{PIPED_API_URL}/streams/{video_id}"
        r_stream = requests.get(stream_url, timeout=5)
        r_stream.raise_for_status()
        stream_data = r_stream.json()

        # 3. Ищем аудиопоток (формат m4a/mp4, так как ESP32 любит AAC)
        # Piped возвращает список 'audioStreams'
        audio_streams = stream_data.get('audioStreams', [])
        
        target_url = None
        
        # Пытаемся найти m4a поток
        for stream in audio_streams:
            if stream.get('format') == 'm4a':
                target_url = stream.get('url')
                break
        
        # Если m4a нет, берем любой аудио
        if not target_url and len(audio_streams) > 0:
            target_url = audio_streams[0].get('url')

        if target_url:
            # Делаем редирект на поток
            return redirect(target_url, code=302)
        else:
            return jsonify({"error": "No audio streams found"}), 404

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
