"""
أدوات الشبكة المساعدة
"""
import socket
import re
import subprocess
import shutil
import os


def get_local_ip():
    """الحصول على عنوان IP المحلي — من نفس interface الـ default gateway"""
    try:
        # استخراج الـ src IP من الـ default route مباشرة
        result = subprocess.check_output(["ip", "route", "show", "default"], text=True)
        # مثال: default via 192.168.1.1 dev wlp2s0 proto dhcp src 192.168.1.105
        match = re.search(r"src (\d+\.\d+\.\d+\.\d+)", result)
        if match:
            return match.group(1)
        # إذا لم يكن src موجوداً، استخرج الـ interface ثم IP منه
        iface_match = re.search(r"dev (\S+)", result)
        if iface_match:
            iface = iface_match.group(1)
            addr_result = subprocess.check_output(
                ["ip", "-4", "addr", "show", "dev", iface], text=True
            )
            addr_match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)/", addr_result)
            if addr_match:
                return addr_match.group(1)
    except Exception:
        pass
    try:
        # fallback: أخذ أول IP غير loopback
        result = subprocess.check_output(["ip", "-4", "addr", "show"], text=True)
        for match in re.finditer(r"inet (\d+\.\d+\.\d+\.\d+)/", result):
            ip = match.group(1)
            if not ip.startswith("127."):
                return ip
    except Exception:
        pass
    return "192.168.1.2"


def get_local_network():
    """استخراج نطاق الشبكة المحلي مع الـ prefix الصحيح من النظام"""
    try:
        # قراءة الـ default route للحصول على الـ interface
        route = subprocess.check_output(["ip", "route", "show", "default"], text=True)
        iface_match = re.search(r"dev (\S+)", route)
        if iface_match:
            iface = iface_match.group(1)
            # قراءة الـ subnet الكامل مع الـ prefix من الـ interface مباشرة
            addr_out = subprocess.check_output(
                ["ip", "-4", "addr", "show", "dev", iface], text=True
            )
            # مثال: inet 192.168.1.105/24 أو inet 10.0.0.5/8
            net_match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)/(\d+)", addr_out)
            if net_match:
                ip, prefix = net_match.group(1), int(net_match.group(2))
                # احسب عنوان الشبكة (network address) من الـ IP والـ prefix
                import ipaddress
                network = ipaddress.IPv4Network(f"{ip}/{prefix}", strict=False)
                return str(network)
    except Exception:
        pass
    # fallback: /24 من الـ IP المحلي
    local_ip = get_local_ip()
    parts = local_ip.split('.')
    return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"


def get_gateway_ip():
    """استخراج عنوان الراوتر (البوابة)"""
    try:
        result = subprocess.check_output(["ip", "route"], text=True)
        match = re.search(r"default via (\d+\.\d+\.\d+\.\d+)", result)
        if match:
            return match.group(1)
    except Exception:
        pass
    # افتراضي
    try:
        import ipaddress
        network = get_local_network()
        net = ipaddress.IPv4Network(network, strict=False)
        return str(net.network_address + 1)
    except Exception:
        local_ip = get_local_ip()
        parts = local_ip.split('.')
        return f"{parts[0]}.{parts[1]}.{parts[2]}.1"


def get_default_interface():
    """استخراج اسم واجهة الشبكة الافتراضية"""
    try:
        result = subprocess.check_output(["ip", "route"], text=True)
        match = re.search(r"default .+ dev (\S+)", result)
        if match:
            return match.group(1)
    except Exception:
        pass
    return "eth0"


def is_nmap_installed():
    """التحقق من تثبيت nmap"""
    return shutil.which("nmap") is not None


def is_root():
    """التحقق هل التطبيق يعمل بصلاحيات root"""
    return os.geteuid() == 0


def validate_ip(ip):
    """التحقق من صحة عنوان IP"""
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False
    parts = ip.split('.')
    return all(0 <= int(p) <= 255 for p in parts)


def validate_network_range(network_range):
    """التحقق من صحة نطاق الشبكة"""
    pattern = r'^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$'
    if not re.match(pattern, network_range):
        return False
    ip_part, cidr = network_range.split('/')
    if not validate_ip(ip_part):
        return False
    return 0 <= int(cidr) <= 32


def measure_interface_speed(duration=1.5):
    """
    قياس سرعة الـ interface الحالي من /proc/net/dev خلال مدة محددة.
    يُرجع (dl_mbps, ul_mbps) — بدون إنترنت، بدون أدوات خارجية.
    """
    iface = get_default_interface()
    def _read_bytes():
        try:
            with open("/proc/net/dev") as f:
                for line in f:
                    if iface in line:
                        cols = line.split()
                        return int(cols[1]), int(cols[9])  # rx_bytes, tx_bytes
        except Exception:
            pass
        return 0, 0

    import time
    rx1, tx1 = _read_bytes()
    time.sleep(duration)
    rx2, tx2 = _read_bytes()

    dl_mbps = round((rx2 - rx1) * 8 / duration / 1_000_000, 2)
    ul_mbps = round((tx2 - tx1) * 8 / duration / 1_000_000, 2)
    return max(dl_mbps, 0.0), max(ul_mbps, 0.0)


def get_bssid(iface=None):
    """جلب عنوان الـ MAC للراوتر (BSSID) للشبكة الحالية"""
    if not iface:
        iface = get_default_interface()
    try:
        result = subprocess.check_output(["iw", "dev", iface, "link"], text=True)
        match = re.search(r"Connected to ([0-9A-Fa-f:]{17})", result)
        if match:
            return match.group(1).upper()
    except Exception:
        pass
    
    # محاولة ثانية عبر arp
    gateway_ip = get_gateway_ip()
    try:
        result = subprocess.check_output(["ip", "neigh", "show", gateway_ip], text=True)
        match = re.search(r"lladdr ([0-9A-Fa-f:]{17})", result)
        if match:
            return match.group(1).upper()
    except Exception:
        pass
    return None

def get_wireless_interfaces():
    """الحصول على قائمة بكروت الواي فاي المتاحة"""
    interfaces = []
    try:
        result = subprocess.check_output(["iw", "dev"], text=True)
        for line in result.split("\n"):
            match = re.search(r"Interface (\S+)", line)
            if match:
                interfaces.append(match.group(1))
    except Exception:
        pass
    return interfaces

def enable_monitor_mode(iface):
    """تفعيل وضع المراقبة لكارت واي فاي محدد"""
    try:
        subprocess.check_call(["ip", "link", "set", iface, "down"])
        subprocess.check_call(["iw", "dev", iface, "set", "type", "monitor"])
        subprocess.check_call(["ip", "link", "set", iface, "up"])
        return True
    except Exception as e:
        log.error(f"فشل تفعيل وضع المراقبة على {iface}: {e}")
        return False

def disable_monitor_mode(iface):
    """إلغاء وضع المراقبة لكارت واي فاي محدد"""
    try:
        subprocess.check_call(["ip", "link", "set", iface, "down"])
        subprocess.check_call(["iw", "dev", iface, "set", "type", "managed"])
        subprocess.check_call(["ip", "link", "set", iface, "up"])
        return True
    except Exception as e:
        log.error(f"فشل إرجاع {iface} للوضع العادي: {e}")
        return False

def validate_mac(mac):
    """التحقق من صحة عنوان MAC"""
    pattern = r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$'
    return bool(re.match(pattern, mac))
