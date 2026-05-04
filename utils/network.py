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
    """استخراج نطاق الشبكة المحلي"""
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
    network = get_local_network()
    return network.replace("0/24", "1")


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


def validate_mac(mac):
    """التحقق من صحة عنوان MAC"""
    pattern = r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$'
    return bool(re.match(pattern, mac))
