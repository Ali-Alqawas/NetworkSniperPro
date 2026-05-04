"""
نظام الثيمات — داكن وبيج
"""
import customtkinter as ctk
import config


def setup_theme(mode=None):
    if mode is None:
        mode = config.CURRENT_THEME
    if mode == "light":
        ctk.set_appearance_mode("light")
        config.COLORS.update(config.COLORS_LIGHT)
        config.CURRENT_THEME = "light"
    else:
        ctk.set_appearance_mode("dark")
        config.COLORS.update(config.COLORS_DARK)
        config.CURRENT_THEME = "dark"
    ctk.set_default_color_theme("blue")


def toggle_theme():
    new_mode = "light" if config.CURRENT_THEME == "dark" else "dark"
    setup_theme(new_mode)
    return new_mode


def get_color(name):
    return config.COLORS.get(name, "#ffffff")
