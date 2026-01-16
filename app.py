from flask import Flask, request, redirect, jsonify
import yt_dlp
import logging

app = Flask(__name__)

# Настройки для Render.com
ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'ytsearch',
    'socket_timeout': 10,
    # На Render нормальный интернет, хаки не нужны
}

@app.route('/')
def home():
    return "Mimik Server on Render is Working!"

@app.route('/play')
def play_music():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            
            if 'entries' in info and len(info['entries']) > 0:
                video_data = info['entries'][0]
                audio_url = video_data['url']
                return redirect(audio_url, code=302)
            else:
                return jsonify({"error": "Nothing found"}), 404
                
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
