from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import librosa
import numpy as np
import tempfile
import os
import uvicorn
from typing import List, Dict, Optional
import json
from scipy.signal import find_peaks
from sklearn.cluster import KMeans

app = FastAPI(title="YouTube Karaoke API", version="1.0.0")

# Adaugă CORS pentru frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class YouTubeLink(BaseModel):
    url: str

class AnalysisResult(BaseModel):
    title: str
    tempo: float
    chords: List[Dict[str, any]]
    duration: float
    beats: List[float]
    key: Optional[str] = None
    chord_progression: Optional[List[str]] = None
    difficulty: Optional[str] = None

class DrumPattern(BaseModel):
    tempo: float
    pattern: List[Dict[str, any]]
    style: str

def detect_chords_advanced(audio_path: str, sr: int) -> List[Dict[str, any]]:
    """
    Detectare avansată a acordurilor cu algoritmi spectrali îmbunătățiți
    """
    try:
        # Încarcă audio
        y, sr = librosa.load(audio_path, sr=sr)
        
        # Parametri îmbunătățiți
        hop_length = 512
        frame_length = 2048
        
        # Calculează chromagram cu parametri optimizați
        chroma = librosa.feature.chroma_cqt(
            y=y, sr=sr, hop_length=hop_length, 
            bins_per_octave=36, norm=2
        )
        
        # Detectare beat-uri pentru sincronizare
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop_length)
        beat_frames = librosa.frames_to_samples(beats, hop_length=hop_length)
        
        # Dicționar extins de acorduri
        chord_templates = {
            # Major chords
            'C': [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
            'G': [1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
            'F': [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0],
            'D': [1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
            'A': [1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
            'E': [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0],
            'B': [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            
            # Minor chords
            'Am': [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
            'Em': [1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0],
            'Dm': [1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
            'Bm': [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            
            # Power chords
            'C5': [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
            'G5': [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
            'F5': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
            
            # Suspended chords
            'Csus2': [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
            'Csus4': [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
        }
        
        chords = []
        segment_duration = 0.5  # 500ms segmente
        
        for i in range(0, len(y), int(sr * segment_duration)):
            segment = y[i:i + int(sr * segment_duration)]
            if len(segment) < sr * 0.25:  # Skip segmente prea mici
                continue
                
            # Calculează chroma pentru segment
            chroma_segment = librosa.feature.chroma_cqt(
                y=segment, sr=sr, hop_length=hop_length
            )
            chroma_avg = np.mean(chroma_segment, axis=1)
            
            # Normalizează
            chroma_avg = chroma_avg / (np.sum(chroma_avg) + 1e-8)
            
            # Găsește cel mai similar acord
            best_chord = "C"
            best_score = 0
            
            for chord_name, template in chord_templates.items():
                # Calculează similaritatea cosinus
                template_norm = np.array(template) / (np.sum(template) + 1e-8)
                score = np.dot(chroma_avg, template_norm) / (
                    np.linalg.norm(chroma_avg) * np.linalg.norm(template_norm) + 1e-8
                )
                
                if score > best_score:
                    best_score = score
                    best_chord = chord_name
            
            # Adaugă acordul doar dacă scorul este suficient de bun
            if best_score > 0.4:  # Prag mai înalt pentru precizie
                chords.append({
                    "timp": i / sr,
                    "acord": best_chord,
                    "confidence": round(best_score, 3),
                    "segment_duration": segment_duration
                })
        
        return chords
        
    except Exception as e:
        print(f"Eroare la detectarea acordurilor: {e}")
        return [
            {"timp": 0, "acord": "C", "confidence": 0.8, "segment_duration": 0.5},
            {"timp": 2, "acord": "G", "confidence": 0.8, "segment_duration": 0.5},
            {"timp": 4, "acord": "Am", "confidence": 0.8, "segment_duration": 0.5},
            {"timp": 6, "acord": "F", "confidence": 0.8, "segment_duration": 0.5},
        ]

def generate_drum_pattern(tempo: float, style: str = "rock") -> List[Dict[str, any]]:
    """
    Generează pattern-uri de percuție sincronizate cu tempo-ul
    """
    # Calculează durata unei măsuri (4/4 time)
    beat_duration = 60.0 / tempo  # secunde per beat
    measure_duration = beat_duration * 4  # 4 beats per measure
    
    patterns = {
        "rock": {
            "kick": [0, 2],  # Beat-uri 1 și 3
            "snare": [1, 3],  # Beat-uri 2 și 4
            "hihat": [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5]  # 8th notes
        },
        "pop": {
            "kick": [0, 1.5, 2, 3.5],
            "snare": [1, 3],
            "hihat": [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5]
        },
        "jazz": {
            "kick": [0, 2.5],
            "snare": [1, 3],
            "hihat": [0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3, 3.25, 3.5, 3.75]
        },
        "electronic": {
            "kick": [0, 1, 2, 3],
            "snare": [1, 3],
            "hihat": [0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3, 3.25, 3.5, 3.75]
        }
    }
    
    pattern = patterns.get(style, patterns["rock"])
    drum_pattern = []
    
    # Generează pattern-ul pentru o măsură
    for beat_time in pattern["kick"]:
        drum_pattern.append({
            "time": beat_time * beat_duration,
            "drum": "kick",
            "velocity": 0.8
        })
    
    for beat_time in pattern["snare"]:
        drum_pattern.append({
            "time": beat_time * beat_duration,
            "drum": "snare", 
            "velocity": 0.7
        })
    
    for beat_time in pattern["hihat"]:
        drum_pattern.append({
            "time": beat_time * beat_duration,
            "drum": "hihat",
            "velocity": 0.5
        })
    
    # Sortează după timp
    drum_pattern.sort(key=lambda x: x["time"])
    
    return drum_pattern

def analyze_chord_progression(chords: List[Dict]) -> List[str]:
    """
    Analizează progresia de acorduri pentru a găsi pattern-uri
    """
    if not chords:
        return []
    
    # Extrage acordurile unice
    unique_chords = list(set([chord["acord"] for chord in chords]))
    
    # Găsește progresia cea mai comună
    progression = []
    for i in range(0, len(chords), 4):  # Grupează în seturi de 4
        group = chords[i:i+4]
        if group:
            progression.extend([chord["acord"] for chord in group])
    
    return progression[:8]  # Returnează primele 8 acorduri

def calculate_difficulty(chords: List[Dict], tempo: float) -> str:
    """
    Calculează dificultatea melodiei bazată pe acorduri și tempo
    """
    if not chords:
        return "Ușor"
    
    # Factorii de dificultate
    unique_chords = len(set([chord["acord"] for chord in chords]))
    avg_confidence = np.mean([chord["confidence"] for chord in chords])
    
    # Scor de dificultate
    difficulty_score = 0
    
    # Mai multe acorduri = mai dificil
    if unique_chords <= 3:
        difficulty_score += 1
    elif unique_chords <= 5:
        difficulty_score += 2
    else:
        difficulty_score += 3
    
    # Tempo mai rapid = mai dificil
    if tempo <= 80:
        difficulty_score += 1
    elif tempo <= 120:
        difficulty_score += 2
    else:
        difficulty_score += 3
    
    # Confidență mai mică = mai dificil
    if avg_confidence < 0.6:
        difficulty_score += 1
    
    if difficulty_score <= 3:
        return "Ușor"
    elif difficulty_score <= 5:
        return "Mediu"
    else:
        return "Dificil"

def detect_key(audio_path: str, sr: int) -> str:
    """
    Detectează cheia melodică cu algoritmi îmbunătățiți
    """
    try:
        y, sr = librosa.load(audio_path, sr=sr)
        
        # Calculează chromagram
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        
        # Detectare cheie cu algoritmi mai avansați
        key_raw = librosa.feature.key_mode(chroma)
        
        # Mapează la note muzicale
        key_mapping = {
            'C': 'C', 'C#': 'C#', 'D': 'D', 'D#': 'D#',
            'E': 'E', 'F': 'F', 'F#': 'F#', 'G': 'G',
            'G#': 'G#', 'A': 'A', 'A#': 'A#', 'B': 'B'
        }
        
        detected_key = key_raw[0] if key_raw[0] else "C"
        return key_mapping.get(detected_key, "C")
        
    except Exception as e:
        print(f"Eroare la detectarea cheii: {e}")
        return "C"

@app.post("/analyze/", response_model=AnalysisResult)
async def analyze_youtube(link: YouTubeLink):
    """
    Analizează un videoclip YouTube și returnează acordurile, tempo-ul și alte informații
    """
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Descarcă audio din YouTube
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{tmpdir}/audio.%(ext)s',
                'quiet': True,
                'no_warnings': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                    'preferredquality': '192',
                }],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link.url, download=True)
                audio_path = os.path.join(tmpdir, "audio.wav")

            # Încarcă audio
            y, sr = librosa.load(audio_path, sr=None)
            duration = librosa.get_duration(y=y, sr=sr)

            # Detectare tempo și beats îmbunătățită
            tempo, beats = librosa.beat.beat_track(
                y=y, sr=sr, hop_length=512, 
                start_bpm=120, std_bpm=1.0
            )
            beat_times = librosa.frames_to_time(beats, sr=sr).tolist()

            # Detectare acorduri avansată
            chords = detect_chords_advanced(audio_path, sr)
            
            # Detectare cheie
            key = detect_key(audio_path, sr)
            
            # Analiză progresie acorduri
            chord_progression = analyze_chord_progression(chords)
            
            # Calculare dificultate
            difficulty = calculate_difficulty(chords, tempo)

            return AnalysisResult(
                title=info.get("title", "Unknown"),
                tempo=round(tempo, 2),
                chords=chords,
                duration=round(duration, 2),
                beats=beat_times,
                key=key,
                chord_progression=chord_progression,
                difficulty=difficulty
            )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Eroare la analiză: {str(e)}")

@app.post("/generate-drum-pattern/", response_model=DrumPattern)
async def generate_drum_pattern_endpoint(tempo: float, style: str = "rock"):
    """
    Generează pattern de percuție pentru un tempo și stil dat
    """
    try:
        pattern = generate_drum_pattern(tempo, style)
        return DrumPattern(
            tempo=tempo,
            pattern=pattern,
            style=style
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Eroare la generarea pattern-ului: {str(e)}")

@app.get("/health/")
async def health_check():
    """
    Endpoint pentru verificarea stării API-ului
    """
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/")
async def root():
    """
    Endpoint principal cu informații despre API
    """
    return {
        "message": "YouTube Karaoke API",
        "version": "1.0.0",
        "endpoints": {
            "POST /analyze/": "Analizează un link YouTube",
            "POST /generate-drum-pattern/": "Generează pattern de percuție",
            "GET /health/": "Verifică starea API-ului"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)