import os
import logging
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

BASE_DIR = Path(__file__).resolve().parent.parent

class AppConfig:
    """Genel Uygulama Ayarları"""
    APP_NAME = "AR Glass Assistant"
    VERSION = "1.0.0-alpha"
    DEBUG = True 
    LOG_LEVEL = logging.INFO
    
    
    LOG_DIR = BASE_DIR / "backend" / "logs"
    ASSETS_DIR = BASE_DIR / "frontend" / "src" / "assets"

class ServerConfig:
    """FastAPI ve WebSocket Sunucu Ayarları"""
    HOST = "127.0.0.1"
    PORT = 8000
    WS_ENDPOINT = "/ws"
    ALLOWED_ORIGINS = [
        "http://localhost",
        "file://",  
        "*"        
    ]

class AIConfig:
    """Yapay Zeka ve LLM Ayarları"""
    API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Modeller
    SMART_MODEL = "gpt-4-turbo-preview"  # Ana beyin (Pahalı ama zeki)
    FAST_MODEL = "gpt-3.5-turbo"         # Özetleme ve hızlı işler (Ucuz)
    AUDIO_MODEL = "whisper-1"            # Ses tanıma
    
    # Hafıza Limiti (Token tasarrufu için)
    MAX_HISTORY_LENGTH = 10
    TEMPERATURE = 0.7

    @staticmethod
    def validate():
        if not AIConfig.API_KEY:
            raise ValueError("KRİTİK HATA: .env dosyasında OPENAI_API_KEY bulunamadı!")

class AudioConfig:
    """Mikrofon ve Ses İşleme Ayarları (Zanaatkarlık Kısmı)"""
    FORMAT = 8  # pyaudio.paInt16 (Int değeri)
    CHANNELS = 1
    RATE = 16000  # Whisper için standart 16kHz
    CHUNK = 1024  # Tampon boyutu
    
    # Voice Activity Detection (VAD)
    # Bu değerler voice_service.py'de kalibre edilir ama varsayılanlar buradadır.
    DEFAULT_SILENCE_THRESHOLD = 500 
    SILENCE_LIMIT_SECONDS = 1.5  # Konuşma bitti demek için ne kadar beklesin?
    PREV_AUDIO_SECONDS = 0.5     # Cümle başını kaçırmamak için tampon bellek

class UIConfig:
    """Tarayıcı ve Mouse Kontrol Ayarları"""
    # Kaydırma Hissi (Kinetic Scrolling)
    SCROLL_SPEED = 400      # Piksel cinsinden
    SCROLL_STEPS = 12       # Hareketi kaç parçaya bölelim? (Yüksek = Daha yumuşak)
    SCROLL_INTERVAL = 0.01  # Adımlar arası bekleme (saniye)
    
    # Yazı Yazma Hızı (Hacker Effect)
    TYPING_INTERVAL = 0.03  # Harfler arası gecikme
    
    # Güvenlik
    FAILSAFE = True         # Mouse sol üste çekilirse programı durdur

# Dizinlerin var olduğundan emin ol
os.makedirs(AppConfig.LOG_DIR, exist_ok=True)

# Başlangıçta konfigürasyon kontrolü yap
AIConfig.validate()