# 🌐 IP Tracker

A professional command-line **IP Geolocation & OSINT tool** built with Python 3 for **Kali Linux** and other Unix-like systems.
It queries public geolocation APIs to retrieve information about any IPv4 or IPv6 address, and displays results with a colorful, well-formatted terminal UI.

> ⚠️ **Disclaimer:** This tool is intended for **educational and authorized security research** only. Always respect privacy laws and terms of service.

---

## ✨ Features

- IPv4 & IPv6 validation
- Geolocation lookup (country, region, city, ZIP, lat/long)
- ISP, Organization, ASN, Timezone, Currency, Calling Code, Languages
- Automatic Google Maps link generation
- Country flag emoji
- Network-type inference (Mobile / Proxy / Hosting / Residential)
- Beautiful Rich-powered terminal UI with tables, spinners, and colors
- Reverse DNS, DNS info, Ping latency, Whois lookup
- Batch scanning from a text file
- Export to **JSON**, **CSV**, and **PDF**
- Scan history (stored in `~/.ip_tracker_history.json`)
- Robust error handling (invalid IP, no internet, rate limit, API failure)
- Logging to `ip_tracker.log`

---

## 📋 Requirements

- Python 3.8+
- Kali Linux (or any Linux/macOS/WSL)
- Working internet connection
- Optional: `whois` and `ping` commands (preinstalled on Kali)

---

## 📦 Installation

```bash
# Clone the repository
git clone [https://github.com/yourname/ip_tracker.git](https://github.com/jenishraiyani5-oss/IP-TRACKER.git)
cd ip_tracker

# (Recommended) Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

On Kali Linux, ensure `whois` is available:

```bash
sudo apt update && sudo apt install -y whois iputils-ping
```

---

## 🚀 Usage

Basic lookup:

```bash
python3 main.py 8.8.8.8
```

Using the `--ip` flag:

```bash
python3 main.py --ip 1.1.1.1
```

With additional lookups:

```bash
python3 main.py 8.8.8.8 --dns --ping --whois
```

Batch mode from a text file (one IP per line):

```bash
python3 main.py --file ips.txt --csv report.csv
```

Export to JSON / CSV / PDF:

```bash
python3 main.py 8.8.8.8 --json result.json --csv result.csv --pdf result.pdf
```

Show scan history:

```bash
python3 main.py --history
```

---

## 🔧 API Configuration

By default the tool uses **[ip-api.com](https://ip-api.com)** (free tier — no key required, ~45 requests/minute) with an automatic fallback to **[ipapi.co](https://ipapi.co)**.

If you want to use a paid API (e.g. ipinfo.io, ipgeolocation.io), edit the `PRIMARY_API` constant inside `tracker.py` and add your API key to the request parameters.

---


## 🧱 Project Structure

```
ip_tracker/
├── main.py            # Entry point / CLI
├── tracker.py         # Core API logic
├── validator.py       # IP validation
├── utils.py           # Helpers (logging, spinner, maps URL)
├── banner.py          # ASCII banner
├── network_tools.py   # DNS, Ping, Whois
├── exporter.py        # JSON / CSV / PDF exports
├── requirements.txt
├── README.md
```

---

## 🧪 Example Output

```
======================================================================
        IP TRACKER
======================================================================

╔══════════ IP Tracker Result — 8.8.8.8 🇺🇸 ══════════╗
║ IP Address    : 8.8.8.8                              ║
║ Country       : United States                        ║
║ Region/State  : California                           ║
║ City          : Mountain View                        ║
║ Latitude      : 37.4056                              ║
║ Longitude     : -122.0775                            ║
║ Google Maps   : https://www.google.com/maps?q=37.4056,-122.0775 ║
║ ISP           : Google LLC                           ║
║ Organization  : Google Public DNS                    ║
║ ASN           : AS15169 Google LLC                   ║
║ Time Zone     : America/Los_Angeles                  ║
╚══════════════════════════════════════════════════════╝
```

---

## 📜 License

Released under the **MIT License**. See `LICENSE` for details.

---

## 🙏 Credits

- [ip-api.com](https://ip-api.com) & [ipapi.co](https://ipapi.co) for geolocation data
- [Rich](https://github.com/Textualize/rich) for the beautiful terminal UI
- [ReportLab](https://www.reportlab.com/) for PDF generation
