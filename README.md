<div align="center">
  <img src="assets/icons/app_icon.png" alt="Logo" width="120" height="120">
  <h1>🎯 Network Sniper Pro</h1>
  <p><strong>Advanced Network Management & Security Auditing Tool</strong></p>
  <p><i>Developed by <b>Ali-Alqawas</b></i></p>

  [![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
  [![License](https://img.shields.io/badge/License-MIT-green.svg?style=flat-square)](LICENSE)
  
  [**عربي**](README-ar.md) | [**English**](README.md)
</div>

---

## 📌 Overview

**Network Sniper Pro** is a cutting-edge, cross-platform graphical tool designed for deep network monitoring, intelligent bandwidth management, and advanced security auditing. Built on top of robust frameworks like `scapy` and `iptables`, it provides network administrators and security researchers with unparalleled control over local networks.

## 🚀 Features

* **Advanced Device Discovery:** Utilizes `Nmap` for deep OS fingerprinting, vendor identification, and real-time device tracking.
* **Smart Disconnection Engine:** Employs three distinct strategies to isolate devices:
  * **ARP Spoofing:** Standard local network disruption.
  * **Deauth Attacks (IEEE 802.11):** Forceful kick for open or isolated (AP Isolation) wireless networks.
  * **Iptables Blocking:** Kernel-level packet dropping (ideal when acting as a Hotspot/Gateway).
* **Persistent Blacklist:** Automatically re-applies disconnection policies to devices even if they disconnect, change IP, and reconnect.
* **Smart Game Mode (Bandwidth Limiter):** Prioritize your bandwidth and restrict network traffic for other users to ensure ultra-low latency during gaming sessions.
* **Port Scanner:** Comprehensive TCP/UDP port scanning to identify open vulnerabilities on connected devices.
* **VIP Whitelist:** Protect specific devices (like your own PC or Smart TV) from accidental disconnection or Game Mode restrictions.
* **Live Analytics Dashboard:** Real-time visual metrics tracking active devices, disconnected targets, and protected VIPs.
* **Smart Filtering:** Instant search by IP, MAC, hostname, or Vendor.
* **Dynamic Theming:** Built-in sleek Dark/Light modes with customizable accent colors using `customtkinter`.

## 🛠️ Tech Stack
* **UI/UX:** `customtkinter` (Modern, hardware-accelerated GUI).
* **Networking Core:** `scapy` (Packet crafting), `Nmap` (Scanning), `iw` & `iptables` (Linux kernel networking).
* **Data Persistence:** SQLite3 (Device History & Analytics) & JSON (Settings).

## 📦 Installation

**Requirements:**
Linux-based OS (Debian/Ubuntu/Kali recommended) with Python 3.8+

```bash
# 1. Clone the repository
git clone https://github.com/YourUsername/NetworkSniperPro.git
cd NetworkSniperPro

# 2. Install system dependencies
sudo apt-get update
sudo apt-get install nmap aircrack-ng iptables

# 3. Install Python requirements
pip3 install -r requirements.txt

# 4. Run the application (Root privileges required for advanced network manipulation)
sudo python3 main.py
```

## ⚠️ Disclaimer
This tool is intended for **educational purposes and authorized network auditing only**. The developer (`Ali-Alqawas`) assumes no liability and is not responsible for any misuse or damage caused by this program. Only use it on networks you own or have explicit permission to manage.

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/YourUsername/NetworkSniperPro/issues).

---
<div align="center">
  <sub>Built by <b>Ali-Alqawas</b> • 2026</sub>
</div>
