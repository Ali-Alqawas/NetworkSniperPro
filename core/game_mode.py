"""
وضع الألعاب - يعطي الأولوية لجهاز محدد ويحدد الباقي
"""
import subprocess
import threading
import shutil
import time
from utils.logger import log
from utils.network import get_default_interface
from config import GAME_MODE_BANDWIDTH_LIMIT, GAME_MODE_AUTO_STOP_MINUTES


class GameMode:
    def __init__(self):
        self.is_active = False
        self._auto_stop_timer = None
        self._interface = get_default_interface()
        self._priority_ip = None

    def is_tc_available(self):
        return shutil.which("tc") is not None

    def activate(self, priority_ip, on_status=None):
        if self.is_active:
            return False
        if not self.is_tc_available():
            if on_status:
                on_status(False, "tc غير مثبت! قم بتثبيته: sudo apt install iproute2")
            return False
        self._priority_ip = priority_ip
        self._interface = get_default_interface()  # تحديث عند كل تفعيل
        thread = threading.Thread(target=self._apply_tc_rules, args=(on_status,), daemon=True)
        thread.start()
        return True

    def _apply_tc_rules(self, on_status=None):
        try:
            iface = self._interface
            limit = GAME_MODE_BANDWIDTH_LIMIT
            subprocess.run(["sudo", "tc", "qdisc", "del", "dev", iface, "root"], capture_output=True)
            subprocess.run([
                "sudo", "tc", "qdisc", "add", "dev", iface, "root",
                "handle", "1:", "htb", "default", "30"
            ], check=True, capture_output=True)
            subprocess.run([
                "sudo", "tc", "class", "add", "dev", iface,
                "parent", "1:", "classid", "1:10", "htb",
                "rate", "1000mbit", "ceil", "1000mbit", "prio", "0"
            ], check=True, capture_output=True)
            subprocess.run([
                "sudo", "tc", "class", "add", "dev", iface,
                "parent", "1:", "classid", "1:30", "htb",
                "rate", limit, "ceil", limit, "prio", "7"
            ], check=True, capture_output=True)
            for direction, flowid in [("src", "1:10"), ("dst", "1:10")]:
                subprocess.run([
                    "sudo", "tc", "filter", "add", "dev", iface,
                    "parent", "1:", "protocol", "ip", "prio", "1",
                    "u32", "match", "ip", direction, self._priority_ip,
                    "flowid", flowid
                ], check=True, capture_output=True)
            self.is_active = True
            log.info(f"وضع الألعاب: أولوية لـ {self._priority_ip} | الباقي محدود بـ {limit}")
            if GAME_MODE_AUTO_STOP_MINUTES > 0:
                self._auto_stop_timer = threading.Timer(
                    GAME_MODE_AUTO_STOP_MINUTES * 60, self.deactivate
                )
                self._auto_stop_timer.start()
            if on_status:
                on_status(True, f"وضع الألعاب مفعل ✅\nالأولوية: {self._priority_ip}\nالحد للباقي: {limit}")
        except subprocess.CalledProcessError as e:
            self.is_active = False
            log.error(f"فشل وضع الألعاب: {e}")
            if on_status:
                on_status(False, f"فشل التفعيل: {e.stderr.decode() if e.stderr else str(e)}")
        except Exception as e:
            self.is_active = False
            log.error(f"خطأ: {e}")
            if on_status:
                on_status(False, str(e))

    def deactivate(self, on_status=None):
        try:
            if self._auto_stop_timer:
                self._auto_stop_timer.cancel()
                self._auto_stop_timer = None
            subprocess.run(["sudo", "tc", "qdisc", "del", "dev", self._interface, "root"], capture_output=True)
            self.is_active = False
            self._priority_ip = None
            log.info("تم إلغاء وضع الألعاب")
            if on_status:
                on_status(False, "تم إلغاء وضع الألعاب")
        except Exception as e:
            log.error(f"خطأ في الإلغاء: {e}")

    def toggle(self, priority_ip=None, on_status=None):
        if self.is_active:
            self.deactivate(on_status)
        else:
            self.activate(priority_ip, on_status)

    def cleanup(self):
        if self.is_active:
            self.deactivate()
