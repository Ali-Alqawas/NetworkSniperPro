"""
محرك فحص الشبكة - ping sweep متوازٍ + ARP cache + nmap للتفاصيل
يحل مشكلة AP Isolation حيث الأجهزة لا ترد على ARP لكن ترد على ICMP
"""
import subprocess
import re
import threading
import concurrent.futures
from utils.logger import log
from utils.network import validate_network_range, get_gateway_ip, get_local_ip
from config import NMAP_TIMEOUT


class NetworkScanner:
    def __init__(self):
        self.process = None
        self.is_scanning = False
        self._lock = threading.Lock()

    def scan(self, network_range, on_complete=None, on_error=None, on_progress=None):
        if not validate_network_range(network_range):
            if on_error:
                on_error("نطاق شبكة غير صالح!")
            return
        self.is_scanning = True
        thread = threading.Thread(
            target=self._run_scan,
            args=(network_range, on_complete, on_error, on_progress),
            daemon=True
        )
        thread.start()
        return thread

    def _ping_host(self, ip):
        """ping جهاز واحد - محاولتان بـ 2 ثانية لاستيعاب الأجهزة البطيئة"""
        try:
            result = subprocess.run(
                ["ping", "-c", "2", "-W", "2", ip],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            return result.returncode == 0
        except Exception:
            return False

    def _ping_sweep(self, network_range, on_progress):
        """ping sweep متوازٍ لكل الشبكة لملء ARP cache"""
        # استخراج base IP من network_range مثل 192.168.1.0/24
        base = re.match(r"(\d+\.\d+\.\d+)\.\d+/\d+", network_range)
        if not base:
            return
        base_ip = base.group(1)

        if on_progress:
            on_progress("جاري ping sweep لاكتشاف الأجهزة...")

        ips = [f"{base_ip}.{i}" for i in range(1, 255)]

        # ping متوازٍ بـ 50 thread
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = {executor.submit(self._ping_host, ip): ip for ip in ips}
            alive = []
            for future in concurrent.futures.as_completed(futures):
                if not self.is_scanning:
                    executor.shutdown(wait=False, cancel_futures=True)
                    return []
                ip = futures[future]
                if future.result():
                    alive.append(ip)
                    if on_progress:
                        on_progress(f"تم اكتشاف: {ip}")
        return alive

    def _read_arp_cache(self):
        """قراءة ARP cache من الـ kernel - يعيد {ip: mac}"""
        arp = {}
        try:
            output = subprocess.check_output(["ip", "neigh", "show"], text=True)
            for line in output.splitlines():
                # مثال: 192.168.1.101 dev wlp2s0 lladdr a0:c9:a0:e6:02:63 REACHABLE
                m = re.match(r"(\d+\.\d+\.\d+\.\d+)\s+dev\s+\S+\s+lladdr\s+([0-9a-fA-F:]+)", line)
                if m:
                    arp[m.group(1)] = m.group(2).upper()
        except Exception as e:
            log.error(f"خطأ في قراءة ARP cache: {e}")
        return arp

    def _get_vendor(self, mac):
        """استخراج vendor من MAC عبر nmap أو قاعدة بيانات بسيطة"""
        # قاعدة بيانات بسيطة للـ OUI الشائعة
        oui_db = {
            "34:E8:94": "TP-Link Technologies",
            "A0:C9:A0": "Murata Manufacturing",
            "AC:F6:F7": "LG Electronics",
            "96:A3:8E": "Unknown",
            "E4:A4:71": "HP Inc.",
        }
        prefix = mac[:8].upper()
        return oui_db.get(prefix, "غير معروف")

    def _get_hostname(self, ip):
        """محاولة الحصول على hostname عبر DNS reverse lookup"""
        try:
            result = subprocess.run(
                ["nmap", "-sn", "--host-timeout", "3s", ip],
                capture_output=True, text=True, timeout=5
            )
            m = re.search(r"Nmap scan report for (.+?) \(", result.stdout)
            if m:
                return m.group(1).strip()
        except Exception:
            pass
        return "غير معروف"

    def _run_scan(self, network_range, on_complete, on_error, on_progress):
        try:
            # المرحلة 1: ping sweep لملء ARP cache
            alive_ips = self._ping_sweep(network_range, on_progress)

            if not self.is_scanning:
                return

            if on_progress:
                on_progress("جاري قراءة بيانات الأجهزة...")

            # المرحلة 2: قراءة ARP cache
            arp_cache = self._read_arp_cache()

            # المرحلة 3: nmap على الأجهزة المكتشفة فقط للحصول على hostname
            # (أسرع بكثير من فحص كل الشبكة)
            nmap_data = {}
            if alive_ips:
                targets = " ".join(alive_ips)
                try:
                    with self._lock:
                        self.process = subprocess.Popen(
                            ["sudo", "nmap", "-sn", "--host-timeout", "5s"] + alive_ips,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
                        )
                    nmap_out, _ = self.process.communicate(timeout=30)
                    nmap_data = self._parse_nmap_hostnames(nmap_out)
                except Exception as e:
                    log.warning(f"nmap للـ hostnames فشل: {e}")

            if not self.is_scanning:
                return

            # المرحلة 4: بناء قائمة الأجهزة
            devices = self._build_device_list(alive_ips, arp_cache, nmap_data)

            log.info(f"تم اكتشاف {len(devices)} جهاز")
            if on_complete:
                on_complete(devices)

        except Exception as e:
            log.error(f"خطأ في الفحص: {e}")
            if on_error:
                on_error(str(e))
        finally:
            self.is_scanning = False
            self.process = None

    def _parse_nmap_hostnames(self, output):
        """استخراج hostname لكل IP من مخرجات nmap"""
        data = {}
        for line in output.splitlines():
            if line.startswith("Nmap scan report for"):
                ip_m = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
                if not ip_m:
                    continue
                ip = ip_m.group(1)
                # hostname هو النص قبل (IP)
                raw = line.replace("Nmap scan report for ", "").strip()
                hostname = re.sub(r'\s*\(\d+\.\d+\.\d+\.\d+\)', '', raw).strip()
                data[ip] = hostname if hostname != ip else "غير معروف"
        return data

    def _build_device_list(self, alive_ips, arp_cache, nmap_data):
        gateway_ip = get_gateway_ip()
        local_ip = get_local_ip()
        devices = []

        # أضف جهازك المحلي إذا لم يكن في alive_ips
        all_ips = list(alive_ips)
        if local_ip not in all_ips:
            all_ips.append(local_ip)

        for ip in all_ips:
            is_router = (ip == gateway_ip)
            is_local = (ip == local_ip)
            mac = arp_cache.get(ip, "")
            hostname = nmap_data.get(ip, "غير معروف")

            if mac:
                vendor = self._get_vendor(mac)
            elif is_local:
                mac = "N/A (جهازك)"
                vendor = "Local Machine"
            elif is_router:
                mac = "N/A (Router)"
                vendor = "Router/Gateway"
            else:
                mac = "N/A"
                vendor = "غير معروف"

            devices.append({
                "ip": ip,
                "mac": mac,
                "hostname": hostname,
                "vendor": vendor,
                "is_local": is_local,
                "is_router": is_router,
                "status": "online"
            })

        # ترتيب: الراوتر أولاً، ثم جهازك، ثم الباقي
        devices.sort(key=lambda d: (0 if d["is_router"] else (1 if d["is_local"] else 2), d["ip"]))
        return devices

    def stop(self):
        self.is_scanning = False
        with self._lock:
            if self.process and self.process.poll() is None:
                try:
                    self.process.terminate()
                    self.process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                log.info("تم إيقاف عملية nmap")
