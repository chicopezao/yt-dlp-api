import yt_dlp
from flask import Flask, request, jsonify, Response, redirect, send_file
import requests
import asyncio
import aiohttp
import io
import zipfile
from aiohttp import ClientSession

app = Flask(__name__)

# Pesquisa usando API World Ecletix
def search_youtube(query):
    print(f"Pesquisando no YouTube: {query}")
    url = f"https://world-ecletix.onrender.com/api/pesquisayt?query={query}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if 'formattedVideos' in data and data['formattedVideos']:
            print(f"{len(data['formattedVideos'])} vídeos encontrados.")
            return data['formattedVideos']
    print("Nenhum vídeo encontrado.")
    return None

# Pega link direto de áudio
def get_audio_url(video_url):
    print(f"Extraindo link do áudio: {video_url}")
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'cookiefile': 'cookies.txt'   # <-- aqui adicionamos
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        return info['url']

# Pega link direto de vídeo
def get_video_url(video_url):
    print(f"Extraindo link do vídeo: {video_url}")
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'merge_output_format': 'mp4',
        'cookiefile': 'cookies.txt'   # <-- aqui também
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        return info['url']

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
}
CHUNK_SIZE = 262144  # 256 KB

async def stream_file(url):
    async with ClientSession(headers=HEADERS) as session:
        async with session.get(url) as resp:
            async for chunk in resp.content.iter_chunked(CHUNK_SIZE):
                yield chunk

# --- /play ---
@app.route('/play')
async def play():
    name = request.args.get('name')
    if not name:
        return jsonify({'error': 'Parâmetro "name" é obrigatório.'}), 400

    videos = search_youtube(name)
    if not videos:
        return jsonify({'error': 'Nenhum vídeo encontrado.'}), 404

    video_url = videos[0]['link']
    try:
        audio_url = get_audio_url(video_url)

        return Response(
            stream_file(audio_url),
            mimetype="audio/mpeg",
            headers={
                "Content-Disposition": f'attachment; filename="{name}.mp3"'
            },
            direct_passthrough=True
        )
    except Exception as e:
        print(f"Erro ao baixar áudio: {e}")
        return jsonify({'error': 'Erro ao baixar o áudio.', 'details': str(e)}), 500

# --- /playvideo ---
@app.route('/playvideo')
async def playvideo():
    name = request.args.get('name')
    if not name:
        return jsonify({'error': 'Parâmetro "name" é obrigatório.'}), 400

    videos = search_youtube(name)
    if not videos:
        return jsonify({'error': 'Nenhum vídeo encontrado.'}), 404

    video_url = videos[0]['link']
    try:
        video_stream_url = get_video_url(video_url)

        return Response(
            stream_file(video_stream_url),
            mimetype="video/mp4",
            headers={
                "Content-Disposition": f'attachment; filename="{name}.mp4"'
            },
            direct_passthrough=True
        )
    except Exception as e:
        print(f"Erro ao baixar vídeo: {e}")
        return jsonify({'error': 'Erro ao baixar o vídeo.', 'details': str(e)}), 500

# --- /playlink ---
@app.route('/playlink')
async def playlink():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Parâmetro "url" é obrigatório.'}), 400

    try:
        audio_url = get_audio_url(url)

        return Response(
            stream_file(audio_url),
            mimetype="audio/mpeg",
            headers={
                "Content-Disposition": 'attachment; filename="audio.mp3"'
            },
            direct_passthrough=True
        )
    except Exception as e:
        print(f"Erro ao baixar áudio (link): {e}")
        return jsonify({'error': 'Erro ao baixar o áudio.', 'details': str(e)}), 500

# --- /videolink ---
@app.route('/videolink')
async def videolink():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Parâmetro "url" é obrigatório.'}), 400

    try:
        video_stream_url = get_video_url(url)

        return Response(
            stream_file(video_stream_url),
            mimetype="video/mp4",
            headers={
                "Content-Disposition": 'attachment; filename="video.mp4"'
            },
            direct_passthrough=True
        )
    except Exception as e:
        print(f"Erro ao baixar vídeo (link): {e}")
        return jsonify({'error': 'Erro ao baixar o vídeo.', 'details': str(e)}), 500

# --- /playlist ---
@app.route('/playlist')
async def playlist():
    names = request.args.getlist('name')
    if not names:
        return jsonify({'error': 'Parâmetro "name" é obrigatório (pode ser múltiplo).'}), 400

    memory_file = io.BytesIO()

    async with ClientSession(headers=HEADERS) as session:
        with zipfile.ZipFile(memory_file, 'w') as zipf:
            for name in names:
                try:
                    videos = search_youtube(name)
                    if not videos:
                        continue

                    video_url = videos[0]['link']
                    audio_url = get_audio_url(video_url)

                    async with session.get(audio_url) as resp:
                        content = await resp.read()

                    zipf.writestr(f"{name}.mp3", content)
                except Exception as e:
                    print(f"Erro ao baixar {name}: {e}")

    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype='application/zip',
        download_name='playlist.zip',
        as_attachment=True
        )
# Iniciar servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
