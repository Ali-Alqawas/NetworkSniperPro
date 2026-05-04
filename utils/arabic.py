"""
أدوات معالجة النصوص العربية
"""
import arabic_reshaper
from bidi.algorithm import get_display


def ar(text):
    """تحويل النص العربي للعرض الصحيح في الواجهة"""
    try:
        return get_display(arabic_reshaper.reshape(text))
    except Exception:
        return text
