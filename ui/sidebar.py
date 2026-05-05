"""الشريط الجانبي"""
import customtkinter as ctk
from utils.arabic import ar
from config import COLORS
from ui.smart_scroll import SmartScrollFrame


class Sidebar(SmartScrollFrame):
    """
    الـ Sidebar نفسه هو SmartScrollFrame:
    - corner_radius صحيح مباشرة
    - fg_color صحيح بدون طبقات
    - عجلة الماوس تعمل تلقائياً
    """
    def __init__(self, master, callbacks=None, **kwargs):
        import config as _cfg
        super().__init__(
            master,
            width=250,
            corner_radius=16,
            fg_color=(_cfg.COLORS_LIGHT["bg_sidebar"], _cfg.COLORS_DARK["bg_sidebar"]),
            scrollbar_button_color=COLORS["bg_input"],
            scrollbar_button_hover_color=COLORS["bg_card_hover"],
            **kwargs
        )
        self.callbacks = callbacks or {}
        self.grid_columnconfigure(0, weight=1)
        self._build()

    def _build(self):
        s = self  # المحتوى مباشرة في الـ Sidebar

        # ── الشعار ──────────────────────────────────────
        lf = ctk.CTkFrame(s, fg_color="transparent")
        lf.grid(row=0, column=0, padx=20, pady=(22, 8), sticky="ew")
        ctk.CTkLabel(lf, text="🔫", font=ctk.CTkFont(size=28)).pack(side="left", padx=(0, 10))
        tf = ctk.CTkFrame(lf, fg_color="transparent")
        tf.pack(side="left")
        self.lbl_name = ctk.CTkLabel(tf, text="Network Sniper",
                                     font=ctk.CTkFont(size=16, weight="bold"),
                                     text_color=COLORS["text_primary"])
        self.lbl_name.pack(anchor="w")
        self.lbl_ver = ctk.CTkLabel(tf, text="Pro v2.0",
                                    font=ctk.CTkFont(size=11),
                                    text_color=COLORS["accent_gold"])
        self.lbl_ver.pack(anchor="w")

        self._div(s, 1)

        # ── نطاق الشبكة ─────────────────────────────────
        self._sec(s, 2, "نطاق الشبكة")
        net_frame = ctk.CTkFrame(s, fg_color="transparent")
        net_frame.grid(row=3, column=0, padx=16, pady=(0, 4), sticky="ew")
        self.network_entry = ctk.CTkEntry(
            net_frame, height=30, placeholder_text="192.168.1.0/24",
            font=ctk.CTkFont(size=11), fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"], border_width=0
        )
        self.network_entry.pack(fill="x")
        self.network_entry.bind("<Return>",
                                lambda e: self.callbacks.get("scan", lambda: None)())

        self._div(s, 4)

        # ── أدوات الفحص ─────────────────────────────────
        self._sec(s, 5, "أدوات الفحص")
        self.btn_scan    = self._btn(s, 6,  "📡  رادار الشبكة",   "accent_gold",   "hover_gold",   "scan")
        self.btn_stop    = self._btn(s, 7,  "🛑  إيقاف الفحص",   "accent_red",    "hover_red",    "stop", state="disabled")
        self.btn_monitor = self._btn(s, 8,  "👁️  المراقبة الحية", "accent_purple", "accent_blue",  "monitor")

        self._div(s, 9)

        # ── أدوات التحكم ─────────────────────────────────
        self._sec(s, 10, "أدوات التحكم")
        self.btn_game  = self._btn(s, 11, "🎮  وضع الألعاب",   "accent_green",  "hover_green",  "game_mode")
        self.btn_speed = self._btn(s, 12, "⚡  اختبار السرعة", "accent_orange", "hover_orange", "speed_test")

        self._div(s, 13)

        # ── التصدير ──────────────────────────────────────
        self._sec(s, 14, "التصدير")
        self.btn_csv  = self._btn(s, 15, "📊  تصدير CSV",  "bg_input", "bg_card_hover", "export_csv",  secondary=True)
        self.btn_json = self._btn(s, 16, "🗂️  تصدير JSON", "bg_input", "bg_card_hover", "export_json", secondary=True)
        self.btn_pdf  = self._btn(s, 17, "📄  تصدير PDF",  "bg_input", "bg_card_hover", "export_pdf",  secondary=True)

        self._div(s, 18)

        # ── المظهر ───────────────────────────────────────
        self._sec(s, 19, "المظهر")
        self.btn_theme  = self._btn(s, 20, "☀️  Theme",          "bg_input", "bg_card_hover", "toggle_theme", secondary=True)
        self.btn_colors = self._btn(s, 21, "🎨  اختيار الألوان", "bg_input", "bg_card_hover", "color_picker", secondary=True)
        ctk.CTkFrame(s, height=12, fg_color="transparent").grid(row=22, column=0)

    # ── helpers ──────────────────────────────────────────
    def _div(self, parent, row):
        ctk.CTkFrame(parent, height=1, fg_color=COLORS["bg_input"]).grid(
            row=row, column=0, sticky="ew", padx=18, pady=5)

    def _sec(self, parent, row, label):
        ctk.CTkLabel(parent, text=ar(label), font=ctk.CTkFont(size=10),
                     text_color=COLORS["text_muted"]).grid(
            row=row, column=0, padx=24, pady=(2, 1), sticky="w")

    def _btn(self, parent, row, text, color_key, hover_key, cb_key,
             state="normal", secondary=False):
        b = ctk.CTkButton(
            parent, text=ar(text), height=36,
            font=ctk.CTkFont(size=12, weight="normal" if secondary else "bold"),
            fg_color=COLORS[color_key], hover_color=COLORS[hover_key],
            corner_radius=10,
            text_color=COLORS["text_secondary"] if secondary else COLORS["text_primary"],
            state=state,
            command=self.callbacks.get(cb_key)
        )
        b.grid(row=row, column=0, padx=16, pady=3, sticky="ew")
        return b

    # ── theme ────────────────────────────────────────────
    def refresh_theme(self):
        import config
        # tuple (light, dark) حتى يختار CTkScrollableFrame الصحيح تلقائياً
        color_tuple = (config.COLORS_LIGHT["bg_sidebar"], config.COLORS_DARK["bg_sidebar"])
        self._parent_frame.configure(fg_color=color_tuple)
        self.configure(
            scrollbar_button_color=COLORS["bg_input"],
            scrollbar_button_hover_color=COLORS["bg_card_hover"]
        )
        self.lbl_name.configure(text_color=COLORS["text_primary"])
        self.lbl_ver.configure(text_color=COLORS["accent_gold"])
        self.network_entry.configure(fg_color=COLORS["bg_input"],
                                     text_color=COLORS["text_primary"])
        for btn in (self.btn_csv, self.btn_json, self.btn_pdf,
                    self.btn_theme, self.btn_colors):
            btn.configure(fg_color=COLORS["bg_input"],
                          hover_color=COLORS["bg_card_hover"],
                          text_color=COLORS["text_secondary"])
        self.btn_scan.configure(fg_color=COLORS["accent_gold"],
                                hover_color=COLORS["hover_gold"])

    def get_network_range(self) -> str:
        return self.network_entry.get().strip()

    def set_network_range(self, value: str):
        self.network_entry.delete(0, "end")
        self.network_entry.insert(0, value)

    # ── button states ────────────────────────────────────
    def set_scanning(self, v):
        self.btn_scan.configure(state="disabled" if v else "normal")
        self.btn_stop.configure(state="normal" if v else "disabled")

    def set_monitoring(self, v):
        if v:
            self.btn_monitor.configure(text=ar("👁️  إيقاف المراقبة"),
                                       fg_color=COLORS["accent_red"],
                                       hover_color=COLORS["hover_red"])
        else:
            self.btn_monitor.configure(text=ar("👁️  المراقبة الحية"),
                                       fg_color=COLORS["accent_purple"],
                                       hover_color=COLORS["accent_blue"])

    def set_game_mode(self, v):
        if v:
            self.btn_game.configure(text=ar("🎮  إلغاء وضع الألعاب"),
                                    fg_color=COLORS["accent_orange"],
                                    hover_color=COLORS["hover_orange"])
        else:
            self.btn_game.configure(text=ar("🎮  وضع الألعاب"),
                                    fg_color=COLORS["accent_green"],
                                    hover_color=COLORS["hover_green"])

    def set_theme(self, mode):
        self.btn_theme.configure(
            text="🌙  Theme" if mode == "light" else "☀️  Theme"
        )
