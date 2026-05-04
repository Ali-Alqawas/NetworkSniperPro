#!/usr/bin/env python3
"""
Network Sniper Pro v2.0
أداة احترافية لمهندسي الشبكات
"""
import sys
import os
import socket
import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.logger import log
from utils.network import is_root

# ── Single Instance via Unix socket lock ──────────────────
_LOCK_PORT = 47892   # port محلي فريد للتطبيق
_lock_socket = None


def _acquire_lock():
    """محاولة الحصول على قفل التطبيق. يرجع True إذا نجح، False إذا كان يعمل بالفعل."""
    global _lock_socket
    try:
        _lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _lock_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
        _lock_socket.bind(("127.0.0.1", _LOCK_PORT))
        _lock_socket.listen(1)
        return True
    except OSError:
        # Port مشغول = التطبيق يعمل بالفعل
        return False


def _release_lock():
    global _lock_socket
    if _lock_socket:
        try:
            _lock_socket.close()
        except Exception:
            pass
        _lock_socket = None


def main():
    if not _acquire_lock():
        print("⚠️  التطبيق يعمل بالفعل.")
        sys.exit(0)

    log.info("=" * 50)
    log.info("Network Sniper Pro v2.0 - Starting")
    log.info("=" * 50)

    if not is_root():
        log.warning("التطبيق يعمل بدون صلاحيات root - بعض الميزات قد لا تعمل")
        print("\n⚠️  يُنصح بتشغيل التطبيق بصلاحيات root:")
        print("   sudo python3 main.py\n")

    # تحرير القفل عند إنهاء العملية بأي طريقة
    signal.signal(signal.SIGTERM, lambda *_: (_release_lock(), sys.exit(0)))
    signal.signal(signal.SIGINT,  lambda *_: (_release_lock(), sys.exit(0)))

    from ui.app import NetworkSniperApp
    app = NetworkSniperApp()
    try:
        app.mainloop()
    finally:
        _release_lock()


if __name__ == "__main__":
    main()
