"""
قاعدة بيانات محلية لأسماء الأجهزة — مرتبطة بالـ MAC Address
تُحفظ في ملف JSON وتبقى حتى مع تغير الـ IP
"""
import json
import os

_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "device_names.json")
_db: dict = {}


def _load():
    global _db
    try:
        if os.path.exists(_DB_PATH):
            with open(_DB_PATH, "r", encoding="utf-8") as f:
                _db = json.load(f)
    except Exception:
        _db = {}


def _save():
    try:
        with open(_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(_db, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def get_name(mac: str) -> str | None:
    """إرجاع الاسم المحفوظ للجهاز بناءً على MAC، أو None"""
    if not _db:
        _load()
    return _db.get(mac.upper().strip())


def set_name(mac: str, name: str):
    """حفظ اسم جهاز مرتبط بـ MAC"""
    if not _db and os.path.exists(_DB_PATH):
        _load()
    _db[mac.upper().strip()] = name.strip()
    _save()


def delete_name(mac: str):
    """حذف اسم جهاز"""
    _db.pop(mac.upper().strip(), None)
    _save()


# تحميل عند الاستيراد
_load()
