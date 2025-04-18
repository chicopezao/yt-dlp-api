import requests
import yt_dlp
from flask import Flask, request, Response, jsonify

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

# Rota /play — pesquisa e baixa áudio
@app.route('/play')
def play():
    name = request.args.get('name')
    if not name:
        return jsonify({'error': 'Parâmetro "name" é obrigatório.'}), 400

    videos = search_youtube(name)
    if not videos:
        return jsonify({'error': 'Nenhum vídeo encontrado.'}), 404

    video_url = videos[0]['link']
    print(f"Link do vídeo encontrado: {video_url}")

    try:
        audio_url = get_audio_url(video_url)
        response = requests.get(audio_url, stream=True)

        print("Enviando áudio para download...")
        return Response(
            response.iter_content(chunk_size=524288),
            mimetype="audio/mpeg",
            headers={
                "Content-Disposition": f'attachment; filename="{name}.mp3"'
            }
        )
    except Exception as e:
        print(f"Erro ao processar áudio: {e}")
        return jsonify({'error': 'Erro ao baixar o áudio.', 'details': str(e)}), 500

# Rota /playvideo — pesquisa e baixa vídeo
@app.route('/playvideo')
def playvideo():
    name = request.args.get('name')
    if not name:
        return jsonify({'error': 'Parâmetro "name" é obrigatório.'}), 400

    videos = search_youtube(name)
    if not videos:
        return jsonify({'error': 'Nenhum vídeo encontrado.'}), 404

    video_url = videos[0]['link']
    print(f"Link do vídeo encontrado: {video_url}")

    try:
        video_stream_url = get_video_url(video_url)
        response = requests.get(video_stream_url, stream=True)

        print("Enviando vídeo para download...")
        return Response(
            response.iter_content(chunk_size=524288),
            mimetype="video/mp4",
            headers={
                "Content-Disposition": f'attachment; filename="{name}.mp4"'
            }
        )
    except Exception as e:
        print(f"Erro ao processar vídeo: {e}")
        return jsonify({'error': 'Erro ao baixar o vídeo.', 'details': str(e)}), 500

# Rota /playlink — baixa áudio a partir de URL
@app.route('/playlink')
def playlink():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Parâmetro "url" é obrigatório.'}), 400

    try:
        audio_url = get_audio_url(url)
        response = requests.get(audio_url, stream=True)

        print("Enviando áudio direto para download (link)...")
        return Response(
            response.iter_content(chunk_size=524288),
            mimetype="audio/mpeg",
            headers={
                "Content-Disposition": 'attachment; filename="audio.mp3"'
            }
        )
    except Exception as e:
        print(f"Erro ao processar áudio (link): {e}")
        return jsonify({'error': 'Erro ao baixar o áudio.', 'details': str(e)}), 500

# Rota /videolink — baixa vídeo a partir de URL
@app.route('/videolink')
def videolink():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Parâmetro "url" é obrigatório.'}), 400

    try:
        video_stream_url = get_video_url(url)
        response = requests.get(video_stream_url, stream=True)

        print("Enviando vídeo direto para download (link)...")
        return Response(
            response.iter_content(chunk_size=524288),
            mimetype="video/mp4",
            headers={
                "Content-Disposition": 'attachment; filename="video.mp4"'
            }
        )
    except Exception as e:
        print(f"Erro ao processar vídeo (link): {e}")
        return jsonify({'error': 'Erro ao baixar o vídeo.', 'details': str(e)}), 500

# Iniciar servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
