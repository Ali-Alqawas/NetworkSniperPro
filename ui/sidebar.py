"""الشريط الجانبي"""
import customtkinter as ctk
from utils.arabic import ar
from config import COLORS


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, callbacks=None, **kwargs):
        super().__init__(master, width=240, corner_radius=16,
                         fg_color=COLORS["bg_sidebar"], **kwargs)
        self.callbacks = callbacks or {}
        self.grid_rowconfigure(10, weight=1)
        self._build()

    def _build(self):
        # ── الشعار ──────────────────────────────────────
        lf = ctk.CTkFrame(self, fg_color="transparent")
        lf.grid(row=0, column=0, padx=20, pady=(28, 8), sticky="ew")
        ctk.CTkLabel(lf, text="🔫", font=ctk.CTkFont(size=30)).pack(side="left", padx=(0, 10))
        tf = ctk.CTkFrame(lf, fg_color="transparent")
        tf.pack(side="left")
        self.lbl_name = ctk.CTkLabel(tf, text="Network Sniper",
                     font=ctk.CTkFont(size=17, weight="bold"),
                     text_color=COLORS["text_primary"])
        self.lbl_name.pack(anchor="w")
        self.lbl_ver = ctk.CTkLabel(tf, text="Pro v2.0",
                     font=ctk.CTkFont(size=11),
                     text_color=COLORS["accent_gold"])
        self.lbl_ver.pack(anchor="w")

        self._divider(1)

        # ── نطاق الشبكة ─────────────────────────────────
        self._section(2, "نطاق الشبكة")
        net_frame = ctk.CTkFrame(self, fg_color="transparent")
        net_frame.grid(row=3, column=0, padx=16, pady=(0, 4), sticky="ew")
        self.network_entry = ctk.CTkEntry(
            net_frame, height=30, placeholder_text="192.168.1.0/24",
            font=ctk.CTkFont(size=11), fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"], border_width=0
        )
        self.network_entry.pack(fill="x")
        self.network_entry.bind("<Return>", lambda e: self.callbacks.get("scan", lambda: None)())

        # ── أدوات الفحص ─────────────────────────────────
        self._section(4, "أدوات الفحص")
        self.btn_scan    = self._btn(5, "📡  رادار الشبكة",   "accent_gold",   "hover_gold",    "scan")
        self.btn_stop    = self._btn(6, "🛑  إيقاف الفحص",   "accent_red",    "hover_red",     "stop",    state="disabled")
        self.btn_monitor = self._btn(7, "👁️  المراقبة الحية", "accent_purple", "accent_blue",   "monitor")

        self._divider(8)

        # ── أدوات التحكم ─────────────────────────────────
        self._section(9, "أدوات التحكم")
        self.btn_game  = self._btn(10, "🎮  وضع الألعاب",   "accent_green",  "hover_green",  "game_mode")
        self.btn_speed = self._btn(11, "⚡  اختبار السرعة", "accent_orange", "hover_orange", "speed_test")

        self._divider(12)

        # ── التصدير ──────────────────────────────────────
        self._section(13, "التصدير")
        self.btn_csv  = self._btn(14, "📊  تصدير CSV",  "bg_input", "bg_card_hover", "export_csv",  secondary=True)
        self.btn_json = self._btn(15, "🗂️  تصدير JSON", "bg_input", "bg_card_hover", "export_json", secondary=True)
        self.btn_pdf  = self._btn(16, "📄  تصدير PDF",  "bg_input", "bg_card_hover", "export_pdf",  secondary=True)

        self._divider(17)

        # ── المظهر ───────────────────────────────────────
        self._section(18, "المظهر")
        self.btn_theme  = self._btn(19, "☀️  Theme",             "bg_input", "bg_card_hover", "toggle_theme", secondary=True)
        self.btn_colors = self._btn(20, "🎨  اختيار الألوان", "bg_input", "bg_card_hover", "color_picker", secondary=True)
        ctk.CTkFrame(self, height=16, fg_color="transparent").grid(row=21, column=0)

    def _divider(self, row):
        ctk.CTkFrame(self, height=1, fg_color=COLORS["bg_input"]).grid(
            row=row, column=0, sticky="ew", padx=18, pady=6)

    def _section(self, row, label):
        ctk.CTkLabel(self, text=ar(label),
                     font=ctk.CTkFont(size=10),
                     text_color=COLORS["text_muted"]).grid(
            row=row, column=0, padx=24, pady=(2, 2), sticky="w")

    def _btn(self, row, text, color_key, hover_key, cb_key, state="normal", secondary=False):
        fg    = COLORS[color_key]
        hover = COLORS[hover_key]
        tc    = COLORS["text_secondary"] if secondary else COLORS["text_primary"]
        b = ctk.CTkButton(
            self, text=ar(text), height=36,
            font=ctk.CTkFont(size=12, weight="bold" if not secondary else "normal"),
            fg_color=fg, hover_color=hover, corner_radius=10,
            text_color=tc, state=state,
            command=self.callbacks.get(cb_key)
        )
        b.grid(row=row, column=0, padx=16, pady=3, sticky="ew")
        return b

    def refresh_theme(self):
        """تحديث كل ألوان السايد بار عند تبديل الثيم"""
        self.configure(fg_color=COLORS["bg_sidebar"])
        self.lbl_name.configure(text_color=COLORS["text_primary"])
        self.lbl_ver.configure(text_color=COLORS["accent_gold"])
        self.network_entry.configure(fg_color=COLORS["bg_input"],
                                     text_color=COLORS["text_primary"])
        for btn in (self.btn_csv, self.btn_json, self.btn_pdf, self.btn_theme, self.btn_colors):
            btn.configure(fg_color=COLORS["bg_input"],
                          hover_color=COLORS["bg_card_hover"],
                          text_color=COLORS["text_secondary"])
        self.btn_scan.configure(fg_color=COLORS["accent_gold"],
                                hover_color=COLORS["hover_gold"])

    def get_network_range(self) -> str:
        """إرجاع النطاق المدخل أو فارغ للاكتشاف التلقائي"""
        return self.network_entry.get().strip()

    def set_network_range(self, value: str):
        self.network_entry.delete(0, "end")
        self.network_entry.insert(0, value)

    # ── حالة الأزرار ─────────────────────────────────────
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
