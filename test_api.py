#!/usr/bin/env python3
"""
Script de test pentru API-ul YouTube Karaoke
"""

import requests
import json
import time
from typing import Dict, Any

class KaraokeAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_health(self) -> bool:
        """Testează endpoint-ul de health check"""
        try:
            response = self.session.get(f"{self.base_url}/health/")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check: {data}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_root(self) -> bool:
        """Testează endpoint-ul principal"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Root endpoint: {data}")
                return True
            else:
                print(f"❌ Root endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Root endpoint error: {e}")
            return False
    
    def test_analyze(self, youtube_url: str) -> Dict[str, Any]:
        """Testează analiza unui videoclip YouTube"""
        try:
            payload = {"url": youtube_url}
            print(f"🔄 Analizez: {youtube_url}")
            
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/analyze/",
                json=payload,
                timeout=300  # 5 minute timeout
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Analiză completă în {end_time - start_time:.2f}s")
                print(f"📊 Rezultate:")
                print(f"   - Titlu: {data.get('title', 'N/A')}")
                print(f"   - Tempo: {data.get('tempo', 'N/A')} BPM")
                print(f"   - Durată: {data.get('duration', 'N/A')}s")
                print(f"   - Cheie: {data.get('key', 'N/A')}")
                print(f"   - Acorduri: {len(data.get('chords', []))}")
                print(f"   - Beat-uri: {len(data.get('beats', []))}")
                return data
            else:
                print(f"❌ Analiză eșuată: {response.status_code}")
                print(f"   Eroare: {response.text}")
                return {}
                
        except requests.exceptions.Timeout:
            print("❌ Timeout la analiză (prea mult timp)")
            return {}
        except Exception as e:
            print(f"❌ Eroare la analiză: {e}")
            return {}
    
    def test_invalid_url(self) -> bool:
        """Testează comportamentul cu URL invalid"""
        try:
            payload = {"url": "https://www.youtube.com/watch?v=INVALID"}
            response = self.session.post(f"{self.base_url}/analyze/", json=payload)
            
            if response.status_code == 400:
                print("✅ URL invalid tratat corect")
                return True
            else:
                print(f"❌ URL invalid nu a fost tratat corect: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Eroare la testarea URL invalid: {e}")
            return False
    
    def run_all_tests(self, test_youtube_url: str = None):
        """Rulează toate testele"""
        print("🚀 Încep testarea API-ului...")
        print("=" * 50)
        
        # Testează health check
        health_ok = self.test_health()
        print()
        
        # Testează root endpoint
        root_ok = self.test_root()
        print()
        
        # Testează URL invalid
        invalid_ok = self.test_invalid_url()
        print()
        
        # Testează analiză reală (dacă este furnizat URL)
        if test_youtube_url:
            print("🎵 Testez analiza cu URL real...")
            result = self.test_analyze(test_youtube_url)
            analyze_ok = bool(result)
            print()
        else:
            analyze_ok = True
            print("⏭️  Săriți testarea analizei (nu este furnizat URL de test)")
            print()
        
        # Rezumat
        print("=" * 50)
        print("📋 REZUMAT TESTE:")
        print(f"   Health Check: {'✅' if health_ok else '❌'}")
        print(f"   Root Endpoint: {'✅' if root_ok else '❌'}")
        print(f"   URL Invalid: {'✅' if invalid_ok else '❌'}")
        print(f"   Analiză Reală: {'✅' if analyze_ok else '❌'}")
        
        all_passed = health_ok and root_ok and invalid_ok and analyze_ok
        print(f"\n🎯 Toate testele: {'✅ PASSEAZĂ' if all_passed else '❌ EȘUEAZĂ'}")
        
        return all_passed

def main():
    """Funcția principală"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Testează API-ul YouTube Karaoke")
    parser.add_argument("--url", help="URL YouTube pentru testare")
    parser.add_argument("--base-url", default="http://localhost:8000", 
                       help="URL-ul de bază al API-ului")
    
    args = parser.parse_args()
    
    tester = KaraokeAPITester(args.base_url)
    success = tester.run_all_tests(args.url)
    
    if success:
        print("\n🎉 Toate testele au trecut cu succes!")
        exit(0)
    else:
        print("\n💥 Unele teste au eșuat!")
        exit(1)

if __name__ == "__main__":
    main() 