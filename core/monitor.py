"""
مراقبة حية للشبكة - فحص دوري واكتشاف أجهزة جديدة
"""
import threading
import time
from utils.logger import log
from config import SCAN_INTERVAL_SECONDS


class NetworkMonitor:
    def __init__(self, scanner):
        self.scanner = scanner
        self.is_monitoring = False
        self._timer = None
        self._known_devices = {}   # {ip: device_info}
        self._on_new_device = None
        self._on_device_left = None
        self._on_update = None
        self._network_range = None

    def start(self, network_range, on_new_device=None, on_device_left=None, on_update=None):
        """بدء المراقبة الحية"""
        if self.is_monitoring:
            return
        self.is_monitoring = True
        self._network_range = network_range
        self._on_new_device = on_new_device
        self._on_device_left = on_device_left
        self._on_update = on_update
        log.info(f"بدء المراقبة الحية كل {SCAN_INTERVAL_SECONDS} ثانية")
        # فحص فوري عند التفعيل بدلاً من الانتظار 30 ثانية
        self._do_scan()

    def _schedule_scan(self):
        if not self.is_monitoring:
            return
        self._timer = threading.Timer(SCAN_INTERVAL_SECONDS, self._do_scan)
        self._timer.daemon = True
        self._timer.start()

    def _do_scan(self):
        if not self.is_monitoring:
            return

        def on_complete(devices):
            if not self.is_monitoring:
                return
            new_ips = {}
            for dev in devices:
                new_ips[dev["ip"]] = dev

            # أجهزة جديدة
            for ip, dev in new_ips.items():
                if ip not in self._known_devices:
                    log.info(f"جهاز جديد: {ip} ({dev.get('vendor', 'unknown')})")
                    if self._on_new_device:
                        self._on_new_device(dev)

            # أجهزة اختفت
            for ip, dev in self._known_devices.items():
                if ip not in new_ips:
                    log.info(f"جهاز اختفى: {ip}")
                    if self._on_device_left:
                        self._on_device_left(dev)

            self._known_devices = new_ips

            if self._on_update:
                self._on_update(devices)

            # جدولة الفحص التالي
            self._schedule_scan()

        def on_error(msg):
            log.error(f"خطأ في المراقبة: {msg}")
            self._schedule_scan()

        self.scanner.scan(self._network_range, on_complete=on_complete, on_error=on_error)

    def stop(self):
        """إيقاف المراقبة"""
        self.is_monitoring = False
        if self._timer:
            self._timer.cancel()
            self._timer = None
        self.scanner.stop()
        log.info("تم إيقاف المراقبة الحية")

    def get_known_devices(self):
        return dict(self._known_devices)

    def set_initial_devices(self, devices):
        """تعيين الأجهزة المعروفة من فحص سابق"""
        self._known_devices = {dev["ip"]: dev for dev in devices}
