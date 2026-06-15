"""
حفظ واسترجاع إعدادات التطبيق بين الجلسات
"""
import json
import os

_SETTINGS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "settings.json"
)

_DEFAULTS = {
    "theme": "dark",
    "network_range": "",          # فارغ = اكتشاف تلقائي
    "colors_dark": {},
    "colors_light": {},
}


def load() -> dict:
    try:
        if os.path.exists(_SETTINGS_PATH):
            with open(_SETTINGS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                # دمج مع الافتراضيات لضمان وجود كل المفاتيح
                return {**_DEFAULTS, **data}
    except Exception:
        pass
    return dict(_DEFAULTS)


def save(settings: dict):
    try:
        with open(_SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def get(key: str, default=None):
    return load().get(key, default)


def set_value(key: str, value):
    s = load()
    s[key] = value
    save(s)
