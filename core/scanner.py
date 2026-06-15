"""
محرك فحص الشبكة - nmap مباشرة مع --send-ip لاكتشاف كل الأجهزة
"""
import subprocess
import re
import threading
import socket
from utils.logger import log
from utils.network import validate_network_range, get_gateway_ip, get_local_ip
from utils.device_names import get_name

try:
    from manuf import manuf as manuf_lib
    _mac_parser = manuf_lib.MacParser()
    HAS_MANUF = True
except Exception:
    HAS_MANUF = False


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

    def _get_vendor(self, mac):
        if not mac or "N/A" in mac or len(mac) < 8:
            return "غير معروف"
        # MAC عشوائي: البت الثاني من أول octet = 1
        try:
            first_byte = int(mac.split(":")[0], 16)
            if first_byte & 0x02:
                return "🔀 MAC عشوائي (خصوصية)"
        except Exception:
            pass
        if HAS_MANUF:
            try:
                result = _mac_parser.get_manuf_long(mac) or _mac_parser.get_manuf(mac)
                if result:
                    return result
            except Exception:
                pass
        return "غير معروف"

    def _resolve_hostname(self, ip: str, nmap_hostname: str) -> str:
        """
        محاولة الحصول على اسم الجهاز بطبقات متعددة:
        1. nmap hostname (إذا وجد)
        2. Reverse DNS عبر socket
        الأجهزة ذات MAC عشوائي (هواتف) لا تُعلن عن اسمها — تُعاد كـ "غير معروف"
        """
        # إذا nmap أعطى اسماً حقيقياً استخدمه مباشرة
        if nmap_hostname and nmap_hostname not in ("غير معروف", ip, "_gateway"):
            return nmap_hostname
        if nmap_hostname == "_gateway":
            return "Router"

        # Reverse DNS
        try:
            name = socket.gethostbyaddr(ip)[0]
            if name and name != ip:
                # نظّف الاسم: أزل domain suffix مثل .local أو .home
                name = name.split(".")[0]
                return name
        except Exception:
            pass

        return "غير معروف"

    def _run_scan(self, network_range, on_complete, on_error, on_progress):
        try:
            if on_progress:
                on_progress("جاري فحص الشبكة بـ nmap...")

            with self._lock:
                # --send-ip: يتجاوز AP Isolation ويكتشف أكثر الأجهزة
                self.process = subprocess.Popen(
                    ["sudo", "nmap", "-sn", "--send-ip", "-T4", network_range],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
                )
            output, _ = self.process.communicate(timeout=60)

            if not self.is_scanning:
                return

            if self.process.returncode and self.process.returncode != 0:
                if on_error:
                    on_error(f"فشل Nmap برمز خطأ {self.process.returncode}")
                return

            if on_progress:
                on_progress("جاري تحليل النتائج...")

            devices = self._parse_nmap_output(output)
            log.info(f"تم اكتشاف {len(devices)} جهاز")
            if on_complete:
                on_complete(devices)

        except subprocess.TimeoutExpired:
            if self.process:
                self.process.kill()
            if on_error:
                on_error("انتهت مهلة الفحص")
        except Exception as e:
            log.error(f"خطأ في الفحص: {e}")
            if on_error:
                on_error(str(e))
        finally:
            self.is_scanning = False
            self.process = None

    def _parse_nmap_output(self, output):
        gateway_ip = get_gateway_ip()
        local_ip = get_local_ip()
        devices = []
        current = {}

        for line in output.splitlines():
            if line.startswith("Nmap scan report for"):
                if current.get("ip"):
                    devices.append(current)
                ip_m = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
                if not ip_m:
                    current = {}
                    continue
                ip = ip_m.group(1)
                # hostname: النص قبل (IP)
                raw = line.replace("Nmap scan report for ", "").strip()
                nmap_hostname = re.sub(r'\s*\(\d+\.\d+\.\d+\.\d+\)', '', raw).strip()
                if nmap_hostname == ip:
                    nmap_hostname = "غير معروف"
                current = {
                    "ip": ip, "mac": "", "hostname": nmap_hostname, "vendor": "غير معروف",
                    "is_local": ip == local_ip, "is_router": ip == gateway_ip, "status": "online"
                }
            elif line.startswith("MAC Address:") and current:
                m = re.match(r"MAC Address: ([0-9A-Fa-f:]{17})\s*\((.+)\)", line)
                if m:
                    current["mac"] = m.group(1).upper()
                    nmap_vendor = m.group(2).strip()
                    if nmap_vendor and nmap_vendor.lower() != "unknown":
                        current["vendor"] = nmap_vendor
                    else:
                        current["vendor"] = self._get_vendor(current["mac"])

        if current.get("ip"):
            devices.append(current)

        # أضف جهازك المحلي إذا لم يظهر
        local_ips = {d["ip"] for d in devices}
        if local_ip not in local_ips:
            devices.append({
                "ip": local_ip, "mac": "N/A (جهازك)", "hostname": "localhost",
                "vendor": "Local Machine", "is_local": True, "is_router": False, "status": "online"
            })

        # حل الأسماء + تطبيق الأسماء المحفوظة
        for dev in devices:
            mac = dev.get("mac", "")
            # 1. الاسم المحفوظ يدوياً (أعلى أولوية)
            saved = get_name(mac) if mac and "N/A" not in mac else None
            if saved:
                dev["hostname"] = saved
                dev["name_source"] = "saved"
            else:
                # 2. حل الاسم من nmap + DNS
                resolved = self._resolve_hostname(dev["ip"], dev.get("hostname", "غير معروف"))
                dev["hostname"] = resolved
                dev["name_source"] = "resolved" if resolved != "غير معروف" else "unknown"

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
