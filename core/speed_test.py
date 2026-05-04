"""
اختبار سرعة الشبكة
"""
import threading
from utils.logger import log

try:
    import speedtest
    HAS_SPEEDTEST = True
except ImportError:
    HAS_SPEEDTEST = False
    log.warning("speedtest-cli غير مثبت")


class SpeedTester:
    def __init__(self):
        self.is_testing = False
        self.last_result = None

    def is_available(self):
        return HAS_SPEEDTEST

    def run_test(self, on_complete=None, on_error=None, on_progress=None):
        """تشغيل اختبار السرعة في thread منفصل"""
        if not HAS_SPEEDTEST:
            if on_error:
                on_error("speedtest-cli غير مثبت!")
            return
        if self.is_testing:
            return

        self.is_testing = True
        thread = threading.Thread(
            target=self._test, args=(on_complete, on_error, on_progress), daemon=True
        )
        thread.start()

    def _test(self, on_complete, on_error, on_progress):
        try:
            st = speedtest.Speedtest()

            if on_progress:
                on_progress("جاري اختيار أفضل سيرفر...")
            st.get_best_server()

            if on_progress:
                on_progress("جاري اختبار سرعة التحميل...")
            download = st.download() / 1_000_000  # Mbps

            if on_progress:
                on_progress("جاري اختبار سرعة الرفع...")
            upload = st.upload() / 1_000_000  # Mbps

            ping = st.results.ping
            server = st.results.server.get("sponsor", "Unknown")

            result = {
                "download": round(download, 2),
                "upload": round(upload, 2),
                "ping": round(ping, 1),
                "server": server,
            }
            self.last_result = result
            log.info(f"اختبار السرعة: ↓{result['download']}Mbps ↑{result['upload']}Mbps Ping:{result['ping']}ms")

            if on_complete:
                on_complete(result)
        except Exception as e:
            log.error(f"خطأ في اختبار السرعة: {e}")
            if on_error:
                on_error(str(e))
        finally:
            self.is_testing = False
