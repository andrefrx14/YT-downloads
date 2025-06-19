from flask import Flask, request, redirect, url_for, render_template, send_file
import yt_dlp
import os
import glob

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form['url']
    quality = request.form['quality']
    
    # Criar pasta downloads se não existir
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    
    try:
        # Configuração do yt-dlp baseada na qualidade escolhida
        ydl_opts = {
            'outtmpl': 'downloads/%(title)s.%(ext)s',
        }
        
        # Definir formato baseado na qualidade
        if quality == 'best':
            ydl_opts['format'] = 'best'
        elif quality == 'medium':
            ydl_opts['format'] = 'best[height<=720]'
        elif quality == 'low':
            ydl_opts['format'] = 'worst[height>=360]'
        elif quality == 'audio':
            ydl_opts['format'] = 'bestaudio/best'
            # Para converter para MP3 (opcional)
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Primeiro, vamos obter informações do vídeo
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'Vídeo')
            
            # Agora fazer o download
            ydl.download([url])
            
            # Descobrir extensão do arquivo baixado
            if quality == 'audio':
                ext = 'mp3'
            else:
                ext = info.get('ext', 'mp4')
            filename = f"{video_title}.{ext}"
            filepath = os.path.join('downloads', filename)
            # Se não encontrar, tenta qualquer arquivo com o título
            if not os.path.exists(filepath):
                files = glob.glob(f"downloads/{video_title}.*")
                if files:
                    filepath = files[0]
                else:
                    raise Exception("Arquivo não encontrado após download.")
        
        # Envia o arquivo para o usuário baixar
        return send_file(filepath, as_attachment=True, download_name=os.path.basename(filepath))
        
    except Exception as e:
        return f'''
        <div style="max-width: 600px; margin: 50px auto; padding: 30px; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h1>❌ Erro no Download</h1>
            <p><strong>Erro:</strong> {str(e)}</p>
            <p>Tente com outra URL ou verifique sua conexão.</p>
            <a href="/" style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #dc3545; color: white; text-decoration: none; border-radius: 5px;">← Tentar Novamente</a>
        </div>
        '''

if __name__ == '__main__':
    app.run(debug=True)