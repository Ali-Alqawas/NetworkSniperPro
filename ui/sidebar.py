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
        ctk.CTkLabel(tf, text="Network Sniper",
                     font=ctk.CTkFont(size=17, weight="bold"),
                     text_color=COLORS["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(tf, text="Pro v2.0",
                     font=ctk.CTkFont(size=11),
                     text_color=COLORS["accent_gold"]).pack(anchor="w")

        self._divider(1)

        # ── أدوات الفحص ─────────────────────────────────
        self._section(2, "أدوات الفحص")
        self.btn_scan    = self._btn(3, "📡  رادار الشبكة",   "accent_gold",   "hover_gold",    "scan")
        self.btn_stop    = self._btn(4, "🛑  إيقاف الفحص",   "accent_red",    "hover_red",     "stop",    state="disabled")
        self.btn_monitor = self._btn(5, "👁️  المراقبة الحية", "accent_purple", "accent_purple", "monitor")

        self._divider(6)

        # ── أدوات التحكم ─────────────────────────────────
        self._section(7, "أدوات التحكم")
        self.btn_game  = self._btn(8, "🎮  وضع الألعاب",   "accent_green",  "hover_green",  "game_mode")
        self.btn_speed = self._btn(9, "⚡  اختبار السرعة", "accent_orange", "hover_orange", "speed_test")

        self._divider(11)

        # ── التصدير ──────────────────────────────────────
        self._section(12, "التصدير")
        self.btn_csv = self._btn(13, "📊  تصدير CSV", "bg_input", "bg_card_hover", "export_csv", secondary=True)
        self.btn_pdf = self._btn(14, "📄  تصدير PDF", "bg_input", "bg_card_hover", "export_pdf", secondary=True)

        self._divider(15)

        # ── الثيم — قسم مستقل ────────────────────────────
        self._section(16, "المظهر")
        self.btn_theme = self._btn(17, "☀️  الوضع النهاري", "bg_input", "bg_card_hover", "toggle_theme", secondary=True)
        # padding سفلي لرفع الزر عن الحافة
        ctk.CTkFrame(self, height=16, fg_color="transparent").grid(row=18, column=0)

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
                                       hover_color=COLORS["accent_purple"])

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
            text=ar("🌙  الوضع الليلي" if mode == "light" else "☀️  الوضع النهاري")
        )
