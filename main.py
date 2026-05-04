#!/usr/bin/env python3
"""
Network Sniper Pro v2.0
أداة احترافية لمهندسي الشبكات
"""
import sys
import os

# إضافة مسار المشروع
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.logger import log
from utils.network import is_root


def main():
    log.info("=" * 50)
    log.info("Network Sniper Pro v2.0 - Starting")
    log.info("=" * 50)

    if not is_root():
        log.warning("التطبيق يعمل بدون صلاحيات root - بعض الميزات قد لا تعمل")
        print("\n⚠️  يُنصح بتشغيل التطبيق بصلاحيات root:")
        print("   sudo python3 main.py\n")

    from ui.app import NetworkSniperApp
    app = NetworkSniperApp()
    app.mainloop()


if __name__ == "__main__":
    main()
