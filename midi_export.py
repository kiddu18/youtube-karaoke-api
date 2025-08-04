#!/usr/bin/env python3
"""
Script pentru exportul pattern-urilor de percuție și progresiilor de acorduri în format MIDI
"""

import json
from typing import List, Dict, Any
from midiutil import MIDIFile

class MIDIExporter:
    def __init__(self):
        self.midi = None
        self.tempo = 120
        self.time = 0
        
    def create_midi_file(self, tempo: float = 120):
        """Creează un fișier MIDI nou"""
        self.midi = MIDIFile(1)  # 1 track
        self.tempo = tempo
        self.time = 0
        self.midi.addTempo(0, 0, tempo)
        
    def add_drum_pattern(self, pattern: List[Dict[str, Any]], track: int = 0):
        """Adaugă pattern de percuție în MIDI"""
        if not self.midi:
            raise ValueError("MIDI file not initialized")
            
        # Mapează instrumentele la note MIDI
        drum_mapping = {
            "kick": 36,    # Bass Drum 1
            "snare": 38,   # Acoustic Snare
            "hihat": 42,   # Closed Hi-Hat
            "crash": 49,   # Crash Cymbal 1
            "tom1": 45,    # Low Tom
            "tom2": 47,    # Mid Tom
            "tom3": 50,    # High Tom
        }
        
        for hit in pattern:
            drum_type = hit.get("drum", "kick")
            time = hit.get("time", 0)
            velocity = int(hit.get("velocity", 0.7) * 127)
            
            if drum_type in drum_mapping:
                note = drum_mapping[drum_type]
                self.midi.addNote(track, 9, note, time, 0.25, velocity)
                
    def add_chord_progression(self, chords: List[str], track: int = 0, 
                            duration: float = 1.0, velocity: int = 80):
        """Adaugă progresia de acorduri în MIDI"""
        if not self.midi:
            raise ValueError("MIDI file not initialized")
            
        # Mapează acordurile la note
        chord_notes = {
            "C": [60, 64, 67],      # C major
            "G": [67, 71, 74],      # G major
            "F": [65, 69, 72],      # F major
            "Am": [69, 72, 76],     # A minor
            "Dm": [62, 65, 69],     # D minor
            "Em": [64, 67, 71],     # E minor
            "D": [62, 66, 69],      # D major
            "A": [69, 73, 76],      # A major
            "E": [64, 68, 71],      # E major
            "B": [71, 75, 78],      # B major
            "Bm": [71, 74, 78],     # B minor
            "C5": [60, 67],         # C power chord
            "G5": [67, 74],         # G power chord
            "F5": [65, 72],         # F power chord
        }
        
        for i, chord in enumerate(chords):
            if chord in chord_notes:
                notes = chord_notes[chord]
                time = i * duration
                
                for note in notes:
                    self.midi.addNote(track, 0, note, time, duration, velocity)
                    
    def add_bass_line(self, chords: List[str], track: int = 0, 
                     duration: float = 1.0, velocity: int = 70):
        """Adaugă linie de bas bazată pe acorduri"""
        if not self.midi:
            raise ValueError("MIDI file not initialized")
            
        # Notele de bază pentru fiecare acord
        bass_notes = {
            "C": 36,   # C1
            "G": 43,   # G1
            "F": 41,   # F1
            "Am": 45,  # A1
            "Dm": 38,  # D1
            "Em": 40,  # E1
            "D": 38,   # D1
            "A": 45,   # A1
            "E": 40,   # E1
            "B": 47,   # B1
            "Bm": 47,  # B1
            "C5": 36,  # C1
            "G5": 43,  # G1
            "F5": 41,  # F1
        }
        
        for i, chord in enumerate(chords):
            if chord in bass_notes:
                note = bass_notes[chord]
                time = i * duration
                self.midi.addNote(track, 1, note, time, duration, velocity)
                
    def save_midi(self, filename: str):
        """Salvează fișierul MIDI"""
        if not self.midi:
            raise ValueError("MIDI file not initialized")
            
        with open(filename, "wb") as output_file:
            self.midi.writeFile(output_file)
            
    def export_karaoke_midi(self, analysis_result: Dict[str, Any], 
                           filename: str = "karaoke.mid"):
        """Exportă un fișier MIDI complet pentru karaoke"""
        self.create_midi_file(analysis_result.get("tempo", 120))
        
        # Track 0: Piano (acorduri)
        chords = [chord["acord"] for chord in analysis_result.get("chords", [])]
        self.add_chord_progression(chords, track=0, duration=0.5)
        
        # Track 1: Bass
        self.add_bass_line(chords, track=1, duration=0.5)
        
        # Track 9: Drums (pattern generat)
        if "drum_pattern" in analysis_result:
            self.add_drum_pattern(analysis_result["drum_pattern"], track=9)
        
        self.save_midi(filename)
        return filename

def create_midi_from_analysis(analysis_data: Dict[str, Any], 
                            drum_pattern: List[Dict[str, Any]] = None,
                            output_filename: str = "karaoke_export.mid") -> str:
    """
    Creează un fișier MIDI din rezultatele analizei
    """
    exporter = MIDIExporter()
    
    # Creează fișierul MIDI
    exporter.create_midi_file(analysis_data.get("tempo", 120))
    
    # Adaugă acordurile
    chords = [chord["acord"] for chord in analysis_data.get("chords", [])]
    if chords:
        exporter.add_chord_progression(chords, track=0, duration=0.5)
        exporter.add_bass_line(chords, track=1, duration=0.5)
    
    # Adaugă percuția dacă este disponibilă
    if drum_pattern:
        exporter.add_drum_pattern(drum_pattern, track=9)
    
    # Salvează fișierul
    exporter.save_midi(output_filename)
    
    return output_filename

def main():
    """Funcția principală pentru testare"""
    # Exemplu de utilizare
    analysis_example = {
        "tempo": 120,
        "chords": [
            {"acord": "C", "timp": 0, "confidence": 0.8},
            {"acord": "G", "timp": 2, "confidence": 0.8},
            {"acord": "Am", "timp": 4, "confidence": 0.8},
            {"acord": "F", "timp": 6, "confidence": 0.8},
        ]
    }
    
    drum_pattern_example = [
        {"time": 0, "drum": "kick", "velocity": 0.8},
        {"time": 0.5, "drum": "hihat", "velocity": 0.5},
        {"time": 1, "drum": "snare", "velocity": 0.7},
        {"time": 1.5, "drum": "hihat", "velocity": 0.5},
        {"time": 2, "drum": "kick", "velocity": 0.8},
        {"time": 2.5, "drum": "hihat", "velocity": 0.5},
        {"time": 3, "drum": "snare", "velocity": 0.7},
        {"time": 3.5, "drum": "hihat", "velocity": 0.5},
    ]
    
    filename = create_midi_from_analysis(
        analysis_example, 
        drum_pattern_example,
        "test_karaoke.mid"
    )
    
    print(f"Fișier MIDI creat: {filename}")

if __name__ == "__main__":
    main() 