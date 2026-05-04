"""
نظام الألوان والثيمات
"""
import customtkinter as ctk
from config import COLORS


def setup_theme():
    """تهيئة الثيم الداكن"""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")


def get_color(name):
    """الحصول على لون من الإعدادات"""
    return COLORS.get(name, "#ffffff")
