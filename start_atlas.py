import subprocess
import sys
import os
import time
import threading
import socket


class Colors:
    CORE = '\033[96m'
    HUD = '\033[93m'
    SYS = '\033[92m'
    ERR = '\033[91m'
    RESET = '\033[0m'

def print_log(prefix, color, message):
    print(f"{color}[{prefix}] {message}{Colors.RESET}")

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def kill_ghost_processes():
    print_log("ATLAS", Colors.SYS, "Port 8000 kontrol ediliyor...")
    if is_port_in_use(8000):
        print_log("SİSTEM", Colors.ERR, "Port 8000 dolu! Hayalet süreçler temizleniyor...")
        if os.name == 'nt':
            os.system("taskkill /F /IM python.exe /T > nul 2>&1")
        time.sleep(1)

def stream_output(process, prefix, color):
    try:
        for line in iter(process.stdout.readline, b''):
            text = line.decode('utf-8', errors='replace').strip()
            if text:
                print_log(prefix, color, text)
    except Exception as e:
        print_log("LAUNCHER", Colors.ERR, f"{prefix} okuma hatası: {e}")


def main():
    print_log("ATLAS", Colors.SYS, "=== ATLAS MERKEZİ BAŞLATICI V2.0 AKTİF ===")
    kill_ghost_processes()
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "backend")
    frontend_dir = os.path.join(root_dir, "frontend")
    backend_process = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    threading.Thread(target=stream_output, args=(backend_process, "CORE", Colors.CORE), daemon=True).start()
    time.sleep(10)
    if not is_port_in_use(8000):
        print_log("SİSTEM", Colors.ERR, "HATA: Backend başlatılamadı! Port 8000 hala kapalı.")
        if backend_process.stdout:
            print_log("CORE", Colors.ERR, "Backend logu:")
            for line in backend_process.stdout:
                try:
                    print(line.decode('utf-8', errors='replace').strip())
                except Exception:
                    print(line)
        backend_process.terminate()
        return
    frontend_process = subprocess.Popen(
        ["npm", "start"],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True
    )
    threading.Thread(target=stream_output, args=(frontend_process, "HUD", Colors.HUD), daemon=True).start()
    print_log("ATLAS", Colors.SYS, "=== TÜM SİSTEMLER SENKRONİZE EDİLDİ. CTRL+C İLE KAPATIN ===")
    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print(f"\n{Colors.ERR}[ATLAS] SİSTEM KAPATILIYOR...{Colors.RESET}")
        backend_process.terminate()
        frontend_process.terminate()
        sys.exit(0)

if __name__ == "__main__":
    main()