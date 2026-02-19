import sys
import asyncio
import json
import logging
import threading
import base64
import os
import cv2
import time
import re
import tempfile
import wikipedia
import edge_tts
import pygame
import urllib.request
import urllib.parse
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from config import AppConfig
ai_speaking = threading.Event()
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

class GlassBrain:
    def process_command(self, user_text, image_data=None):
        return {
            "voice_response": "",
            "hud_text": "",
            "action": "NONE"
        }
class SonicReceptor:
    def calibrate_ambient_noise(self):
        pass
    def listen_and_transcribe(self, visualizer_callback=None):
        try:
            return input("")
        except Exception:
            return None
            return None
class BrowserCommander:
    def execute_action(self, ai_response):
        pass
        pass
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("ATLAS_CORE")
app = FastAPI(title=AppConfig.APP_NAME, version=AppConfig.VERSION, debug=AppConfig.DEBUG)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def speak_text(text):
    def _speak():
        try:
            ai_speaking.set()
            voice = "tr-TR-AhmetNeural"
            communicate = edge_tts.Communicate(text, voice, rate="+5%", pitch="-20Hz")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                temp_path = fp.name
            asyncio.run(communicate.save(temp_path))
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.music.unload()
            os.remove(temp_path)
        except Exception as error:
            logger.error(f"Edge-TTS Seslendirme Hatası: {error}")
        finally:
            ai_speaking.clear()
def set_system_volume(volume_level: int):
    try:
        import platform
        if platform.system() == "Windows":
            nircmd_path = os.path.join(os.getcwd(), "nircmd.exe")
            if not os.path.exists(nircmd_path):
                logger.error("nircmd.exe bulunamadı! Ses seviyesi değiştirilemiyor.")
                return False
            vol = int((volume_level / 100) * 65535)
            os.system(f'"{nircmd_path}" setsysvolume {vol}')
            return True
        else:
            logger.error("Ses seviyesi ayarı sadece Windows'ta destekleniyor.")
            return False
    except Exception as error:
        logger.error(f"Ses ayarı hatası: {error}")
        return False
        logger.error(f"Ses ayarı hatası: {error}")
        return False

class SystemManager:
    def __init__(self):
        logger.info("ATLAS Bileşenleri Yükleniyor...")
        self.brain = GlassBrain()
        self.ears = SonicReceptor()
        self.hands = BrowserCommander()
        
        self.active_websocket: Optional[WebSocket] = None
        self.is_running = False
        self.main_loop = None  
        self.translation_mode = False

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_websocket = websocket
        self.main_loop = asyncio.get_running_loop()
        logger.info("HUD Arayüzü Bağlandı (Neural Link Established)")
        await self.send_to_ui("system_status", {"status": "online", "message": "SYS_CHK_OK"})

    def disconnect(self):
        self.active_websocket = None
        self.is_running = False
        logger.warning("HUD Bağlantısı Koptu.")

    async def send_to_ui(self, message_type: str, payload: dict):
        if self.active_websocket:
            try:
                message = {"type": message_type, "payload": payload}
                await self.active_websocket.send_text(json.dumps(message, ensure_ascii=False))
            except Exception:
                pass

    def _sync_send(self, msg_type: str, payload: dict):
        if self.active_websocket and self.is_running and self.main_loop:
            try:
                asyncio.run_coroutine_threadsafe(self.send_to_ui(msg_type, payload), self.main_loop)
            except Exception:
                pass

    def _visualizer_callback(self, volume_level: float):
        self._sync_send("audio_visualizer", {"volume": volume_level})

    def capture_image(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened(): return None
        ret, frame = cap.read()
        cap.release()
        if ret:
            _, buffer = cv2.imencode('.jpg', frame)
            return base64.b64encode(buffer).decode('utf-8')
        return None


    def process_local_commands(self, user_text_lower: str):
        """Ücretsiz Yerel İşleme Motoru: Tarayıcı açmadan direkt HUD üzerinde işlem yapar."""
        # 1. Ses Seviyesi Ayarlama
        vol_match = re.search(r"ses[i]?.* (\d+)|yüzde (\d+)", user_text_lower)
        if ("ses" in user_text_lower or "seviye" in user_text_lower) and vol_match:
            try:
                vol = int(vol_match.group(1) or vol_match.group(2))
                if set_system_volume(vol):
                    return {"voice": f"Sistem sesi yüzde {vol} olarak ayarlandı.", "hud": f"VOLUME: {vol}%", "action": "VOL_CHANGE"}
            except Exception as e:
                logger.error(f"Ses seviyesi ayarlanırken hata: {e}")

        # 2. WIKIPEDIA ARAMASI (Gözlük Ekranına Basar)
        search_match = re.search(r"kimdir|nedir|hakkında bilgi ver", user_text_lower)
        if search_match:
            query = user_text_lower.replace("kimdir", "").replace("nedir", "").replace("hakkında bilgi ver", "").strip()
            if query:
                try:
                    wikipedia.set_lang("tr")
                    summary = wikipedia.summary(query, sentences=2)
                    self._sync_send("info_panel", {"title": query.upper(), "text": summary})
                    return {"voice": summary, "hud": f"WIKIPEDIA: {query.upper()}", "action": "SHOW_INFO"}
                except Exception as error:
                    logger.warning(f"Wiki bulunamadı: {error}")
                    pass # Bulamazsa ChatGPT'ye düşmesi için devam eder

        # 3. YOUTUBE MÜZİK (HUD üzerinde görünmez çalar)
        yt_match = re.search(r"youtubeden|youtube'dan|şarkı|müzik|parça|play|çal|oynat|aç", user_text_lower)
        if yt_match:
            try:
                # Komuttan şarkı adını ayıkla (ör: 'youtubeden shape of you çal')
                song_name = user_text_lower
                for key in ["youtubeden", "youtube'dan", "şarkı", "müzik", "parça", "çal", "oynat", "aç"]:
                    song_name = song_name.replace(key, "")
                song_name = song_name.strip()
                logger.info(f"YouTube araması: {song_name}")
                query_string = urllib.parse.urlencode({"search_query": song_name})
                with urllib.request.urlopen("https://www.youtube.com/results?" + query_string) as response:
                    html = response.read().decode()
                search_results = re.findall(r"watch\?v=([a-zA-Z0-9_-]{11})", html)
                if search_results:
                    video_id = search_results[0]
                    self._sync_send("media_player", {"command": "play", "vid": video_id, "title": song_name.upper()})
                    return {"voice": f"Frekans ayarlandı. {song_name} çalınıyor.", "hud": f"PLAYING: {song_name.upper()}", "action": "HUD_MUSIC"}
                else:
                    logger.error(f"YouTube'da şarkı bulunamadı: {song_name}")
                    return {"voice": "YouTube'da şarkı bulunamadı.", "hud": "NO MUSIC FOUND", "action": "NO_MUSIC"}
            except Exception as error:
                logger.error(f"YouTube Arama Hatası: {error}")
                return {"voice": "YouTube arama hatası oluştu.", "hud": "YOUTUBE ERROR", "action": "NO_MUSIC"}

        # 4. ŞARKILARI DURDURMA (Arayüzdeki iframe'i kapatır)
        if any(word in user_text_lower for word in ["şarkıyı durdur", "müziği durdur", "sesi kes", "durdur"]):
            self._sync_send("media_player", {"command": "stop"})
            return {"voice": "Medya durduruldu.", "hud": "MEDIA STOPPED", "action": "STOP_HUD_MUSIC"}

        return None # Yerel komut eşleşmediyse ChatGPT'ye gider.


    def _voice_processing_loop(self):
        logger.info("ATLAS Ses İzleme Motoru Başladı.")
        self._sync_send("hud_update", {"text": "Calibrating Audio...", "state": "processing"})
        self.ears.calibrate_ambient_noise()
        self._sync_send("hud_update", {"text": "Listening...", "state": "listening"})

        global ai_speaking
        while self.is_running:
            try:
                # AI konuşuyorsa mikrofonu geçici olarak devre dışı bırak
                if ai_speaking.is_set():
                    time.sleep(0.1)
                    continue

                user_text = self.ears.listen_and_transcribe(visualizer_callback=self._visualizer_callback)

                if user_text:
                    logger.info(f"Kullanıcı: {user_text}")
                    user_text_lower = user_text.lower()

                    # --- 1. ÇEVİRİ MODU KONTROLÜ ---
                    if "çeviri modunu aç" in user_text_lower or "altyazı modunu aç" in user_text_lower:
                        self.translation_mode = True
                        speak_text("Çeviri modu aktif edildi efendim. Bulut zeka devre dışı.")
                        self._sync_send("ai_response", {"user_text": "-", "hud_text": "TRANSCRIPTION ONLINE"})
                        self._sync_send("hud_update", {"text": "Standing By", "state": "idle"})
                        continue

                    elif "çeviri modunu kapat" in user_text_lower or "altyazı modunu kapat" in user_text_lower:
                        self.translation_mode = False
                        speak_text("Taktiksel zeka tekrar devrede.")
                        self._sync_send("ai_response", {"user_text": "-", "hud_text": "ATLAS CORE ONLINE"})
                        self._sync_send("hud_update", {"text": "Standing By", "state": "idle"})
                        continue

                    if self.translation_mode:
                        self._sync_send("ai_response", {"user_text": user_text, "hud_text": "-"})
                        self._sync_send("hud_update", {"text": "Transcribing", "state": "listening"})
                        continue

                    self._sync_send("ai_response", {"user_text": user_text, "hud_text": "-"})
                    self._sync_send("hud_update", {"text": "Processing...", "state": "thinking"})

                    # --- 2. YEREL İŞLEME MOTORU (Wikipedia & HUD Player) ---
                    local_response = self.process_local_commands(user_text_lower)

                    if local_response:
                        voice_text = local_response["voice"]
                        hud_text = local_response["hud"]

                        self._sync_send("ai_response", {"user_text": "-", "hud_text": hud_text})
                        speak_text(voice_text)
                        self._sync_send("hud_update", {"text": "ACTION COMPLETE", "state": "idle"})
                        continue

                    # --- 3. BULUT ZEKA (OpenAI Görüntü/Sohbet) ---
                    image_data = None
                    if any(word in user_text_lower for word in ["bu ne", "ne görüyorsun", "tanı", "buna bak"]):
                        self._sync_send("hud_update", {"text": "Accessing Optical Sensor...", "state": "vision"})
                        image_data = self.capture_image()
                        if not image_data:
                            self._sync_send("ai_response", {"user_text": user_text, "hud_text": "[OPTICAL SENSOR OFFLINE]"})
                            continue

                    ai_response = self.brain.process_command(user_text, image_data=image_data)

                    voice_text = ai_response.get("voice_response", "İşlem tamamlandı.")
                    hud_text = ai_response.get("hud_text", voice_text)

                    self._sync_send("ai_response", {"user_text": "-", "hud_text": hud_text})

                    if voice_text:
                        speak_text(voice_text)

                    # Tarayıcı Aksiyonları
                    action = ai_response.get("action", "NONE")
                    if action != "NONE":
                        self.hands.execute_action(ai_response)

                    self._sync_send("hud_update", {"text": "Standing By", "state": "idle"})

            except Exception as error:
                logger.error(f"Döngü Hatası: {error}")
                time.sleep(1)

    def start_listening_thread(self):
        if not self.is_running:
            self.is_running = True
            threading.Thread(target=self._voice_processing_loop, daemon=True).start()

system = SystemManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await system.connect(websocket)
    system.start_listening_thread()
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        system.disconnect()
    except Exception:
        system.disconnect()

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)