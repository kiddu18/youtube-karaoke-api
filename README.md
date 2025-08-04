# YouTube Karaoke - Acorduri & Percuție

O aplicație care analizează videoclipuri YouTube pentru a extrage acordurile chitarei, tempo-ul și generează percuție sincronizată pentru karaoke.

## 🎯 Funcționalități

- **Analiză automată** a melodiei din link-uri YouTube
- **Detectare acorduri** cu algoritmi de analiză spectrală
- **Detectare tempo** și beat-uri precise
- **Percuție sincronizată** la tempo-ul detectat
- **Interfață karaoke** cu afișare sincronizată a acordurilor
- **API REST** pentru integrare cu alte aplicații

## 🚀 Instalare și Configurare

### Cerințe de sistem
- Python 3.8+
- FFmpeg (pentru procesarea audio)
- 4GB+ RAM (pentru analiza audio)

### Instalare locală

1. **Clonează repository-ul**
```bash
git clone https://github.com/username/youtube-chords-tempo-api.git
cd youtube-chords-tempo-api
```

2. **Instalează dependențele**
```bash
pip install -r requirements.txt
```

3. **Instalează FFmpeg**
- **Windows:** Descarcă de la https://ffmpeg.org/download.html
- **macOS:** `brew install ffmpeg`
- **Linux:** `sudo apt install ffmpeg`

4. **Rulează aplicația**
```bash
python main.py
```

Aplicația va fi disponibilă la `http://localhost:8000`

## 🌐 Deployment

### Railway (Recomandat)

1. **Creează cont Railway**
- Mergi la https://railway.app
- Conectează contul GitHub

2. **Deploy automat**
- Fork acest repository
- Railway va detecta automat și va deploya

3. **Configurare variabile de mediu**
```bash
PYTHON_VERSION=3.9
```

### Render

1. **Creează cont Render**
- Mergi la https://render.com
- Conectează contul GitHub

2. **Configurare service**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python main.py`
- **Environment:** Python 3.9

### Fly.io

1. **Instalează Fly CLI**
```bash
curl -L https://fly.io/install.sh | sh
```

2. **Deploy**
```bash
fly launch
fly deploy
```

## 📡 API Endpoints

### POST /analyze/
Analizează un videoclip YouTube

**Request:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Response:**
```json
{
  "title": "Numele melodiei",
  "tempo": 120.5,
  "chords": [
    {
      "timp": 0.0,
      "acord": "C",
      "confidence": 0.85
    }
  ],
  "duration": 180.5,
  "beats": [0.0, 0.5, 1.0, 1.5],
  "key": "C"
}
```

### GET /health/
Verifică starea API-ului

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

## 🎨 Frontend (Lovable.dev)

Pentru a configura frontend-ul pe Lovable.dev:

1. **Creează aplicația**
- Mergi la https://lovable.dev
- Creează o aplicație nouă

2. **Importă configurația**
- Copiază conținutul din `frontend.json`
- Paste în editorul Lovable

3. **Actualizează URL-ul API**
- Înlocuiește `https://numeleproiectului.up.railway.app` cu URL-ul tău

## 🔧 Configurare avansată

### Optimizare performanță

1. **Cache pentru analize**
```python
# Adaugă în main.py
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_analyze(url: str):
    # logica de analiză
```

2. **Limitare rate**
```python
# Adaugă middleware pentru rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

### Extensii viitoare

1. **Suport pentru alte instrumente**
```python
def detect_bass_line(audio_path: str) -> List[Dict]:
    # Detectare linie de bas
    pass

def detect_piano_chords(audio_path: str) -> List[Dict]:
    # Detectare acorduri pian
    pass
```

2. **Salvare în baza de date**
```python
# Integrare cu Supabase
import supabase

def save_analysis(user_id: str, analysis: dict):
    supabase.table('analyses').insert(analysis).execute()
```

## 🐛 Troubleshooting

### Probleme comune

1. **Eroare FFmpeg**
```
Error: ffmpeg not found
```
**Soluție:** Instalează FFmpeg și asigură-te că este în PATH

2. **Eroare memoria**
```
MemoryError: Unable to allocate array
```
**Soluție:** Reduce dimensiunea segmentelor audio în `detect_chords()`

3. **Eroare YouTube download**
```
Video unavailable
```
**Soluție:** Verifică dacă videoclipul este disponibil public

### Debug

Activează logging-ul detaliat:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Metrici și Monitorizare

### Health checks
```bash
curl https://your-api.railway.app/health/
```

### Monitorizare performanță
```python
import time

@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## 🤝 Contribuții

1. Fork repository-ul
2. Creează un branch pentru feature: `git checkout -b feature/noua-functie`
3. Commit schimbările: `git commit -am 'Adaugă funcționalitate'`
4. Push la branch: `git push origin feature/noua-functie`
5. Creează Pull Request

## 📄 Licență

Acest proiect este licențiat sub MIT License - vezi fișierul [LICENSE](LICENSE) pentru detalii.

## 🙏 Mulțumiri

- [librosa](https://librosa.org/) pentru analiza audio
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) pentru descărcarea YouTube
- [FastAPI](https://fastapi.tiangolo.com/) pentru API-ul web
- [Lovable.dev](https://lovable.dev) pentru platforma frontend

## 📞 Contact

Pentru întrebări sau suport:
- Email: contact@example.com
- GitHub Issues: [Creează issue](https://github.com/username/youtube-chords-tempo-api/issues) 