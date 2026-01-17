from flask import Flask, request, send_file, jsonify
import yt_dlp
import os
import glob
import time
import shutil

app = Flask(__name__)

# Папка для временного хранения загрузок
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def cleanup_folder():
    """Удаляет старые файлы (старше 10 минут), чтобы не забивать диск"""
    now = time.time()
    for f in os.listdir(DOWNLOAD_FOLDER):
        f_path = os.path.join(DOWNLOAD_FOLDER, f)
        if os.stat(f_path).st_mtime < now - 600: # 600 секунд = 10 минут
            try:
                if os.path.isfile(f_path):
                    os.remove(f_path)
            except Exception as e:
                print(f"Ошибка очистки: {e}")

@app.route('/music', methods=['GET'])
def get_music():
    # 1. Получаем запрос (например: /music?q=Linkin Park Numb)
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "No query provided"}), 400

    cleanup_folder() # Чистим мусор перед началом

    # Уникальное имя для файла, чтобы запросы не конфликтовали
    req_id = str(int(time.time() * 1000))
    output_template = os.path.join(DOWNLOAD_FOLDER, f"{req_id}_%(title)s.%(ext)s")

    # 2. Настройки yt-dlp (взяты из твоего кода)
    search_string = f"ytsearch1:{query}"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        # Эмуляция мобильных клиентов для обхода ограничений
        'extractor_args': {'youtube': {'player_client': ['android', 'ios']}},
        # Конвертация в MP3
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }],
        'quiet': True,
        'nocheckcertificate': True,
    }

    try:
        downloaded_file = None
        
        # 3. Скачивание
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_string, download=True)
            if not info.get('entries'):
                 return jsonify({"error": "Song not found"}), 404
            
            # Определяем имя скачанного файла (он будет с расширением .mp3)
            # yt-dlp может немного изменить имя, поэтому ищем по ID запроса
            list_of_files = glob.glob(os.path.join(DOWNLOAD_FOLDER, f"{req_id}_*.mp3"))
            if list_of_files:
                downloaded_file = list_of_files[0]

        if downloaded_file and os.path.exists(downloaded_file):
            # 4. Отправляем файл пользователю
            # ВАЖНО: Мы не удаляем файл сразу после return, 
            # за очистку отвечает функция cleanup_folder при следующем вызове.
            filename = os.path.basename(downloaded_file)
            return send_file(
                downloaded_file, 
                as_attachment=True, 
                download_name=filename, 
                mimetype='audio/mpeg'
            )
        else:
             return jsonify({"error": "Download failed"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "Music Server is Running!"

if __name__ == '__main__':
    # Запуск сервера на порту 8080
    app.run(host='0.0.0.0', port=8080)
