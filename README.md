# WordPress Panel Checker 🚀

A fast, multi-threaded Python script designed to check the validity of WordPress login credentials. It features proxy support, WAF/Bot protection bypass mechanisms, and a 3-layer detection system for high accuracy.

**Author:** [denoyey](https://github.com/denoyey)

---

## ✨ Features

* **Multi-threaded Performance:** Uses `ThreadPoolExecutor` for blazing-fast checking.
* **High Accuracy (3-Layer Detection):**
  1. Validates via `wordpress_logged_in` cookies (100% accurate).
  2. Text-based detection parsing the Dashboard/WP-Admin.
  3. XML-RPC Fallback if `wp-login.php` is blocked by WAF.
* **WAF & Bot Bypass:** Utilizes a pool of rotating, powerful, and realistic User-Agents along with custom HTTP headers.
* **Proxy Support:** Automatically loads proxies from `proxies.txt` (HTTP/HTTPS) if available.
* **Real-time Stats:** Beautiful CLI interface with a live progress bar using `tqdm`.
* **Auto-Saving:** Automatically categorizes and saves results (Hits, Bad, Errors) into a `Results` folder.

---

## 🛠️ Requirements

Make sure you have Python 3.x installed on your system. You will also need to install the required Python libraries.

```bash
pip install requests colorama tqdm urllib3
```

## 📝 Input Format

Your target list MUST be formatted strictly as follows:
`URL|USERNAME|PASSWORD`

Example (`list.txt`):

```bash
[http://example.com/wp-login.php](http://example.com/wp-login.php)|admin|password123
[https://testsite.com/wp-login.php](https://testsite.com/wp-login.php)|user1|qazwsx123
```

## 🚀 Usage

1. Clone or download this repository.
2. Prepare your target list in a `.txt` file following the format above.
3. (Optional) If you want to use proxies, create a file named `proxies.txt` in the same directory and add your proxies (Format: `IP:PORT`).
4. Run the script:

```bash
python wp_checker.py
```
1. Enter the name of your target list (e.g., `list.txt`).
2. Enter the number of threads you want to use (Default is 10. Higher threads = faster, but requires better internet/proxies).
3. Wait for the process to finish. Results will be saved in the `Results/` directory.

## 📁 Output Structure
After running the script, a `Results` folder will be generated containing:
- `WP_Success.txt` - Contains all valid / successfully logged-in credentials.
- `Not_working.txt` - Contains failed logins or dead sites.

## ⚠️ Disclaimer
**Educational Purposes Only.**
This tool is created for educational purposes and authorized penetration testing only. The author is not responsible for any misuse, damage, or illegal activities caused by this tool. Do not use this tool against systems you do not own or do not have explicit permission to test.
