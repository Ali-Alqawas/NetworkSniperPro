"""
وضع الألعاب - HTB مع أولوية لجهاز محدد وحد ديناميكي للباقين
الاستراتيجية: تحديد download + upload للآخرين بنسبة من السرعة الفعلية للخط
"""
import subprocess
import threading
import shutil
from utils.logger import log
from utils.network import get_default_interface
from config import GAME_MODE_AUTO_STOP_MINUTES


class GameMode:
    def __init__(self):
        self.is_active = False
        self._auto_stop_timer = None
        self._interface = get_default_interface()
        self._priority_ip = None
        self._dl_limit = "512kbit"
        self._ul_limit = "256kbit"

    def is_tc_available(self):
        return shutil.which("tc") is not None

    def activate(self, priority_ip, on_status=None, dl_kbit=512, ul_kbit=256):
        if self.is_active:
            return False
        if not self.is_tc_available():
            if on_status:
                on_status(False, "tc غير مثبت! قم بتثبيته: sudo apt install iproute2")
            return False
        self._priority_ip = priority_ip
        self._interface = get_default_interface()
        self._dl_limit = f"{dl_kbit}kbit"
        self._ul_limit = f"{ul_kbit}kbit"
        thread = threading.Thread(target=self._apply_tc_rules, args=(on_status,), daemon=True)
        thread.start()
        return True

    def _apply_tc_rules(self, on_status=None):
        iface = self._interface
        try:
            # مسح القواعد القديمة
            subprocess.run(["sudo", "tc", "qdisc", "del", "dev", iface, "root"],
                           capture_output=True)

            # HTB root qdisc — default class 30 (للآخرين)
            subprocess.run([
                "sudo", "tc", "qdisc", "add", "dev", iface, "root",
                "handle", "1:", "htb", "default", "30"
            ], check=True, capture_output=True)

            # Class 1:10 — جهاز الأولوية: سرعة كاملة بدون حد
            subprocess.run([
                "sudo", "tc", "class", "add", "dev", iface,
                "parent", "1:", "classid", "1:10", "htb",
                "rate", "1000mbit", "ceil", "1000mbit", "prio", "1"
            ], check=True, capture_output=True)

            # Class 1:30 — الباقون: محدودون بالسرعة المحددة
            subprocess.run([
                "sudo", "tc", "class", "add", "dev", iface,
                "parent", "1:", "classid", "1:30", "htb",
                "rate", self._dl_limit, "ceil", self._dl_limit, "prio", "7"
            ], check=True, capture_output=True)

            # فلتر src: حركة الخروج من جهاز الأولوية → class 1:10
            subprocess.run([
                "sudo", "tc", "filter", "add", "dev", iface,
                "parent", "1:", "protocol", "ip", "prio", "1",
                "u32", "match", "ip", "src", self._priority_ip,
                "flowid", "1:10"
            ], check=True, capture_output=True)

            # فلتر dst: حركة الدخول لجهاز الأولوية → class 1:10
            subprocess.run([
                "sudo", "tc", "filter", "add", "dev", iface,
                "parent", "1:", "protocol", "ip", "prio", "2",
                "u32", "match", "ip", "dst", self._priority_ip,
                "flowid", "1:10"
            ], check=True, capture_output=True)

            self.is_active = True
            log.info(
                f"وضع الألعاب: أولوية لـ {self._priority_ip} | "
                f"الباقي ⬇️{self._dl_limit} ⬆️{self._ul_limit} على {iface}"
            )

            if GAME_MODE_AUTO_STOP_MINUTES > 0:
                self._auto_stop_timer = threading.Timer(
                    GAME_MODE_AUTO_STOP_MINUTES * 60, self.deactivate
                )
                self._auto_stop_timer.daemon = True
                self._auto_stop_timer.start()

            if on_status:
                on_status(True,
                    f"وضع الألعاب مفعل ✅\n"
                    f"الأولوية: {self._priority_ip}\n"
                    f"الآخرون: ⬇️{self._dl_limit}  ⬆️{self._ul_limit}"
                )

        except subprocess.CalledProcessError as e:
            self.is_active = False
            err = e.stderr.decode().strip() if e.stderr else str(e)
            log.error(f"فشل وضع الألعاب: {err}")
            if on_status:
                on_status(False, f"فشل التفعيل:\n{err}")
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
            subprocess.run(
                ["sudo", "tc", "qdisc", "del", "dev", self._interface, "root"],
                capture_output=True
            )
            self.is_active = False
            self._priority_ip = None
            log.info("تم إلغاء وضع الألعاب")
            if on_status:
                on_status(False, "تم إلغاء وضع الألعاب")
        except Exception as e:
            log.error(f"خطأ في الإلغاء: {e}")

    def toggle(self, priority_ip=None, on_status=None, dl_kbit=512, ul_kbit=256):
        if self.is_active:
            self.deactivate(on_status)
        else:
            self.activate(priority_ip, on_status, dl_kbit, ul_kbit)

    def cleanup(self):
        if self.is_active:
            self.deactivate()
