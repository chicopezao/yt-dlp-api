from flask import Flask, request, send_file, Response
import requests
import yt_dlp
import os
import io
import logging

# Configurações
COOKIES_FILE = 'cookies.txt'
SEARCH_API = 'https://world-ecletix.onrender.com/api/pesquisayt?query='

# Flask App
app = Flask(__name__)

# Ativar logs
logging.basicConfig(level=logging.INFO)

def baixar_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'cookies': COOKIES_FILE,
        'outtmpl': '-',  # Saída no stdout (stream)
        'quiet': True,
        'noplaylist': True,
        'extract_flat': False,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    buffer = io.BytesIO()
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        logging.info(f'Baixando áudio de {url}')
        result = ydl.download([url])
    return buffer

def baixar_video(url):
    ydl_opts = {
        'format': 'best[ext=mp4]',
        'cookies': COOKIES_FILE,
        'outtmpl': '-',  # Saída no stdout (stream)
        'quiet': True,
        'noplaylist': True,
        'extract_flat': False,
    }
    buffer = io.BytesIO()
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        logging.info(f'Baixando vídeo de {url}')
        result = ydl.download([url])
    return buffer

def obter_link_youtube(nome):
    try:
        logging.info(f'Pesquisando "{nome}"...')
        response = requests.get(SEARCH_API + nome)
        data = response.json()
        first_video = data['formattedVideos'][0]
        link = first_video['link']
        logging.info(f'Link encontrado: {link}')
        return link
    except Exception as e:
        logging.error(f'Erro ao pesquisar: {e}')
        return None

@app.route('/play')
def play():
    nome = request.args.get('name')
    if not nome:
        return {"error": "Parâmetro 'name' é obrigatório"}, 400
    link = obter_link_youtube(nome)
    if not link:
        return {"error": "Não foi possível encontrar o vídeo"}, 404
    try:
        buffer = baixar_audio(link)
        return Response(buffer.getvalue(), mimetype="audio/mpeg")
    except Exception as e:
        logging.error(str(e))
        return {"error": "Erro ao baixar o áudio."}, 500

@app.route('/playvideo')
def playvideo():
    nome = request.args.get('name')
    if not nome:
        return {"error": "Parâmetro 'name' é obrigatório"}, 400
    link = obter_link_youtube(nome)
    if not link:
        return {"error": "Não foi possível encontrar o vídeo"}, 404
    try:
        buffer = baixar_video(link)
        return Response(buffer.getvalue(), mimetype="video/mp4")
    except Exception as e:
        logging.error(str(e))
        return {"error": "Erro ao baixar o vídeo."}, 500

@app.route('/playlink')
def playlink():
    url = request.args.get('url')
    if not url:
        return {"error": "Parâmetro 'url' é obrigatório"}, 400
    try:
        buffer = baixar_audio(url)
        return Response(buffer.getvalue(), mimetype="audio/mpeg")
    except Exception as e:
        logging.error(str(e))
        return {"error": "Erro ao baixar o áudio."}, 500

@app.route('/videolink')
def videolink():
    url = request.args.get('url')
    if not url:
        return {"error": "Parâmetro 'url' é obrigatório"}, 400
    try:
        buffer = baixar_video(url)
        return Response(buffer.getvalue(), mimetype="video/mp4")
    except Exception as e:
        logging.error(str(e))
        return {"error": "Erro ao baixar o vídeo."}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
