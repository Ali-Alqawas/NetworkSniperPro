"""
محرك القطع عبر جدار الحماية (iptables)
يستخدم عندما يعمل المستخدم كنقطة اتصال (Hotspot) أو مسار عبور (Gateway)
"""
import subprocess
from utils.logger import log

class IptablesBlocker:
    def __init__(self):
        self._blocked_macs = set()

    def is_available(self):
        try:
            subprocess.check_call(["which", "iptables"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            return False

    def block_mac(self, mac):
        mac = mac.upper()
        if mac in self._blocked_macs:
            return True
            
        try:
            # حجب من التمرير والوصول للإنترنت
            subprocess.check_call(["iptables", "-I", "FORWARD", "-m", "mac", "--mac-source", mac, "-j", "DROP"], stderr=subprocess.DEVNULL)
            subprocess.check_call(["iptables", "-I", "INPUT", "-m", "mac", "--mac-source", mac, "-j", "DROP"], stderr=subprocess.DEVNULL)
            self._blocked_macs.add(mac)
            log.info(f"تم حجب الـ MAC عبر iptables: {mac}")
            return True
        except Exception as e:
            log.error(f"فشل الحجب عبر iptables لـ {mac}: {e}")
            return False

    def unblock_mac(self, mac):
        mac = mac.upper()
        if mac not in self._blocked_macs:
            return False
            
        try:
            # إزالة قواعد الحجب
            subprocess.check_call(["iptables", "-D", "FORWARD", "-m", "mac", "--mac-source", mac, "-j", "DROP"], stderr=subprocess.DEVNULL)
            subprocess.check_call(["iptables", "-D", "INPUT", "-m", "mac", "--mac-source", mac, "-j", "DROP"], stderr=subprocess.DEVNULL)
            self._blocked_macs.remove(mac)
            log.info(f"تم فك الحجب عبر iptables عن: {mac}")
            return True
        except Exception as e:
            log.error(f"فشل فك الحجب عبر iptables عن {mac}: {e}")
            return False

    def is_blocked(self, mac):
        return mac.upper() in self._blocked_macs

    def unblock_all(self):
        macs = list(self._blocked_macs)
        for mac in macs:
            self.unblock_mac(mac)

    def cleanup(self):
        self.unblock_all()
