"""الشريط الجانبي"""
import customtkinter as ctk
from utils.arabic import ar
from config import COLORS

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, callbacks=None, **kwargs):
        super().__init__(master, width=240, corner_radius=0, fg_color=COLORS["bg_sidebar"], **kwargs)
        self.callbacks = callbacks or {}
        self.grid_rowconfigure(10, weight=1)
        self._build()

    def _build(self):
        lf = ctk.CTkFrame(self, fg_color="transparent")
        lf.grid(row=0, column=0, padx=20, pady=(25,5), sticky="ew")
        ctk.CTkLabel(lf, text="🔫", font=ctk.CTkFont(size=32)).pack(side="left", padx=(0,8))
        tf = ctk.CTkFrame(lf, fg_color="transparent")
        tf.pack(side="left")
        ctk.CTkLabel(tf, text="Network Sniper", font=ctk.CTkFont(size=18, weight="bold"), text_color=COLORS["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(tf, text="Pro v2.0", font=ctk.CTkFont(size=12), text_color=COLORS["accent_cyan"]).pack(anchor="w")
        ctk.CTkFrame(self, height=2, fg_color=COLORS["bg_card"]).grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        ctk.CTkLabel(self, text=ar("أدوات الفحص"), font=ctk.CTkFont(size=11), text_color=COLORS["text_muted"]).grid(row=2, column=0, padx=25, pady=(5,5), sticky="w")
        self.btn_scan = self._b(3, ar("📡 رادار الشبكة"), COLORS["accent_blue"], COLORS["hover_blue"], self.callbacks.get("scan"))
        self.btn_stop = self._b(4, ar("🛑 إيقاف الفحص"), COLORS["accent_red"], COLORS["hover_red"], self.callbacks.get("stop"), state="disabled")
        self.btn_monitor = self._b(5, ar("👁️ المراقبة الحية"), COLORS["accent_purple"], "#9966cc", self.callbacks.get("monitor"))
        ctk.CTkFrame(self, height=2, fg_color=COLORS["bg_card"]).grid(row=6, column=0, sticky="ew", padx=20, pady=10)
        ctk.CTkLabel(self, text=ar("أدوات التحكم"), font=ctk.CTkFont(size=11), text_color=COLORS["text_muted"]).grid(row=7, column=0, padx=25, pady=(5,5), sticky="w")
        self.btn_game = self._b(8, ar("🎮 وضع الألعاب"), COLORS["accent_green"], COLORS["hover_green"], self.callbacks.get("game_mode"))
        self.btn_speed = self._b(9, ar("⚡ اختبار السرعة"), COLORS["accent_orange"], COLORS["hover_orange"], self.callbacks.get("speed_test"))
        ctk.CTkFrame(self, height=2, fg_color=COLORS["bg_card"]).grid(row=11, column=0, sticky="ew", padx=20, pady=10)
        ctk.CTkLabel(self, text=ar("التصدير"), font=ctk.CTkFont(size=11), text_color=COLORS["text_muted"]).grid(row=12, column=0, padx=25, pady=(5,5), sticky="w")
        self.btn_csv = self._b(13, ar("📊 تصدير CSV"), COLORS["bg_input"], COLORS["bg_card_hover"], self.callbacks.get("export_csv"), tc=COLORS["text_secondary"])
        self.btn_pdf = self._b(14, ar("📄 تصدير PDF"), COLORS["bg_input"], COLORS["bg_card_hover"], self.callbacks.get("export_pdf"), tc=COLORS["text_secondary"])
        ctk.CTkLabel(self, text=ar("نسخة خاصة لمهندسي الشبكات"), text_color=COLORS["text_muted"], font=ctk.CTkFont(size=10)).grid(row=15, column=0, padx=20, pady=(10,15), sticky="s")

    def _b(self, row, text, color, hover, cmd=None, state="normal", tc=None):
        b = ctk.CTkButton(self, text=text, height=38, font=ctk.CTkFont(size=13), fg_color=color, hover_color=hover, corner_radius=10, command=cmd, state=state, text_color=tc or COLORS["text_primary"])
        b.grid(row=row, column=0, padx=20, pady=4, sticky="ew")
        return b

    def set_scanning(self, v):
        self.btn_scan.configure(state="disabled" if v else "normal")
        self.btn_stop.configure(state="normal" if v else "disabled")

    def set_monitoring(self, v):
        if v:
            self.btn_monitor.configure(text=ar("👁️ إيقاف المراقبة"), fg_color=COLORS["accent_red"], hover_color=COLORS["hover_red"])
        else:
            self.btn_monitor.configure(text=ar("👁️ المراقبة الحية"), fg_color=COLORS["accent_purple"], hover_color="#9966cc")

    def set_game_mode(self, v):
        if v:
            self.btn_game.configure(text=ar("🎮 إلغاء وضع الألعاب"), fg_color=COLORS["accent_orange"], hover_color=COLORS["hover_orange"])
        else:
            self.btn_game.configure(text=ar("�� وضع الألعاب"), fg_color=COLORS["accent_green"], hover_color=COLORS["hover_green"])
