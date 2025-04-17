const express = require("express");
const ytSearch = require("yt-search");
const ytdl = require("yt-dlp");
const app = express();

// Rota para pesquisar o link do vídeo e retornar o áudio
app.get("/play", async (req, res) => {
    const { name } = req.query;
    
    try {
        // Pesquisar vídeo no YouTube usando yt-search
        const { videos } = await ytSearch(name);
        const video = videos[0]; // Pega o primeiro vídeo da pesquisa
        
        if (!video) {
            return res.status(404).json({ error: "Nenhum vídeo encontrado." });
        }

        // Baixar áudio com yt-dlp
        const stream = ytdl(video.url, {
            filter: "audioonly",
            quality: "highestaudio",
        });

        // Configurar o tipo de mídia como áudio
        res.setHeader("Content-Type", "audio/mpeg");

        // Enviar o áudio diretamente para o usuário
        stream.pipe(res);

        stream.on("error", (error) => {
            res.status(500).json({ error: "Erro ao processar o áudio.", details: error.message });
        });

    } catch (error) {
        res.status(500).json({ error: "Erro ao buscar o vídeo ou baixar o áudio.", details: error.message });
    }
});

// Rota para pesquisar o link do vídeo e retornar o vídeo completo
app.get("/playvideo", async (req, res) => {
    const { name } = req.query;
    
    try {
        // Pesquisar vídeo no YouTube usando yt-search
        const { videos } = await ytSearch(name);
        const video = videos[0]; // Pega o primeiro vídeo da pesquisa
        
        if (!video) {
            return res.status(404).json({ error: "Nenhum vídeo encontrado." });
        }

        // Baixar vídeo com yt-dlp
        const stream = ytdl(video.url, {
            quality: "highestvideo",
        });

        // Configurar o tipo de mídia para vídeo
        res.setHeader("Content-Type", "video/mp4");

        // Enviar o vídeo diretamente para o usuário
        stream.pipe(res);

        stream.on("error", (error) => {
            res.status(500).json({ error: "Erro ao processar o vídeo.", details: error.message });
        });

    } catch (error) {
        res.status(500).json({ error: "Erro ao buscar o vídeo ou baixar o vídeo.", details: error.message });
    }
});

// Rota para enviar o áudio a partir de uma URL específica
app.get("/playlink", (req, res) => {
    const { url } = req.query;

    try {
        const stream = ytdl(url, {
            filter: "audioonly",
            quality: "highestaudio",
        });

        // Configurar o tipo de mídia como áudio
        res.setHeader("Content-Type", "audio/mpeg");

        // Enviar o áudio diretamente para o usuário
        stream.pipe(res);

        stream.on("error", (error) => {
            res.status(500).json({ error: "Erro ao processar o áudio.", details: error.message });
        });

    } catch (error) {
        res.status(500).json({ error: "Erro ao baixar o áudio.", details: error.message });
    }
});

// Rota para enviar o vídeo a partir de uma URL específica
app.get("/videolink", (req, res) => {
    const { url } = req.query;

    try {
        const stream = ytdl(url, {
            quality: "highestvideo",
        });

        // Configurar o tipo de mídia para vídeo
        res.setHeader("Content-Type", "video/mp4");

        // Enviar o vídeo diretamente para o usuário
        stream.pipe(res);

        stream.on("error", (error) => {
            res.status(500).json({ error: "Erro ao processar o vídeo.", details: error.message });
        });

    } catch (error) {
        res.status(500).json({ error: "Erro ao baixar o vídeo.", details: error.message });
    }
});

// Iniciar o servidor
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Servidor rodando em http://localhost:${PORT}`);
});