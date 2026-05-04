"""نوافذ الحوار"""
import customtkinter as ctk
import subprocess
import threading
import re
from utils.arabic import ar
from config import COLORS, DISCONNECT_DURATIONS


def _safe_grab(dialog):
    """تفعيل grab_set بأمان بعد ظهور النافذة"""
    try:
        dialog.grab_set()
    except Exception:
        pass


class DisconnectDialog(ctk.CTkToplevel):
    def __init__(self, master, device_info, on_confirm=None):
        super().__init__(master)
        self.title("Disconnect Device")
        self.geometry("420x320")
        self.configure(fg_color=COLORS["bg_dark"])
        self.resizable(False, False)
        self.result = None
        self.on_confirm = on_confirm

        ip = device_info.get("ip", "")
        vendor = device_info.get("vendor", "")

        ctk.CTkLabel(self, text="⚠️", font=ctk.CTkFont(size=40)).pack(pady=(20,5))
        ctk.CTkLabel(self, text=ar("تأكيد قطع الاتصال"), font=ctk.CTkFont(size=20, weight="bold"), text_color=COLORS["accent_orange"]).pack(pady=5)
        ctk.CTkLabel(self, text=f"IP: {ip}  •  {vendor}", font=ctk.CTkFont(size=13), text_color=COLORS["text_secondary"]).pack(pady=5)
        ctk.CTkLabel(self, text=ar("⚠️ استخدم هذه الميزة فقط على شبكتك الخاصة"), font=ctk.CTkFont(size=11), text_color=COLORS["accent_red"]).pack(pady=(5,10))
        ctk.CTkLabel(self, text=ar("اختر مدة القطع:"), font=ctk.CTkFont(size=13), text_color=COLORS["text_primary"]).pack(pady=(5,5))

        self.duration_var = ctk.StringVar(value="5 دقائق")
        dur_frame = ctk.CTkFrame(self, fg_color="transparent")
        dur_frame.pack(pady=5)
        for dur_name in DISCONNECT_DURATIONS.keys():
            ctk.CTkRadioButton(dur_frame, text=ar(dur_name), variable=self.duration_var, value=dur_name, font=ctk.CTkFont(size=12), text_color=COLORS["text_primary"]).pack(side="left", padx=8)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=15)
        ctk.CTkButton(btn_frame, text=ar("إلغاء"), width=120, fg_color=COLORS["bg_input"], hover_color=COLORS["bg_card_hover"], command=self.destroy).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text=ar("✂️ قطع الاتصال"), width=120, fg_color=COLORS["accent_red"], hover_color=COLORS["hover_red"], command=self._confirm).pack(side="left", padx=10)

        self.after(100, lambda: _safe_grab(self))

    def _confirm(self):
        dur = DISCONNECT_DURATIONS.get(self.duration_var.get(), 300)
        if self.on_confirm:
            self.on_confirm(dur)
        self.destroy()


class PortResultDialog(ctk.CTkToplevel):
    def __init__(self, master, ip, ports):
        super().__init__(master)
        self.title(f"Port Scan - {ip}")
        self.geometry("600x500")
        self.configure(fg_color=COLORS["bg_dark"])

        ctk.CTkLabel(self, text=ar(f"🔍 نتائج فحص المنافذ - {ip}"), font=ctk.CTkFont(size=18, weight="bold"), text_color=COLORS["text_primary"]).pack(pady=(20,5))
        ctk.CTkLabel(self, text=ar(f"تم العثور على {len(ports)} منفذ مفتوح"), font=ctk.CTkFont(size=13), text_color=COLORS["text_secondary"]).pack(pady=(0,10))

        scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_sidebar"])
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        if not ports:
            ctk.CTkLabel(scroll, text=ar("لم يتم العثور على منافذ مفتوحة"), text_color=COLORS["text_muted"]).pack(pady=50)
        else:
            for p in ports:
                pf = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"], corner_radius=8)
                pf.pack(fill="x", pady=3, padx=5)
                rl = p.get("risk_level", "unknown")
                if rl == "high":
                    color, icon = COLORS["accent_red"], "🔴"
                elif rl == "medium":
                    color, icon = COLORS["accent_orange"], "🟡"
                else:
                    color, icon = COLORS["accent_green"], "🟢"
                txt = f"{icon} Port {p['port']}/{p['protocol']}  •  {p['service']}  •  {p['state']}"
                ctk.CTkLabel(pf, text=txt, font=ctk.CTkFont(size=13, weight="bold"), text_color=color).pack(anchor="w", padx=15, pady=(8,2))
                ctk.CTkLabel(pf, text=f"   {p.get('risk', '')}", font=ctk.CTkFont(size=11), text_color=COLORS["text_secondary"]).pack(anchor="w", padx=15, pady=(0,8))

        ctk.CTkButton(self, text=ar("إغلاق"), width=120, fg_color=COLORS["bg_input"], hover_color=COLORS["bg_card_hover"], command=self.destroy).pack(pady=15)
        self.after(100, lambda: _safe_grab(self))


class SpeedResultDialog(ctk.CTkToplevel):
    def __init__(self, master, result):
        super().__init__(master)
        self.title("Speed Test Results")
        self.geometry("450x380")
        self.configure(fg_color=COLORS["bg_dark"])

        ctk.CTkLabel(self, text="⚡", font=ctk.CTkFont(size=40)).pack(pady=(20,5))
        ctk.CTkLabel(self, text=ar("نتائج اختبار السرعة"), font=ctk.CTkFont(size=20, weight="bold"), text_color=COLORS["text_primary"]).pack(pady=5)

        rf = ctk.CTkFrame(self, fg_color=COLORS["bg_sidebar"], corner_radius=12)
        rf.pack(fill="x", padx=30, pady=15)

        metrics = [
            ("⬇️  " + ar("التحميل"), f"{result['download']} Mbps", COLORS["accent_green"]),
            ("⬆️  " + ar("الرفع"), f"{result['upload']} Mbps", COLORS["accent_blue"]),
            ("📡  Ping", f"{result['ping']} ms", COLORS["accent_orange"]),
            ("🌐  " + ar("السيرفر"), result.get("server", "N/A"), COLORS["text_secondary"]),
        ]
        for label, value, color in metrics:
            mf = ctk.CTkFrame(rf, fg_color="transparent")
            mf.pack(fill="x", padx=20, pady=8)
            ctk.CTkLabel(mf, text=label, font=ctk.CTkFont(size=14), text_color=COLORS["text_secondary"]).pack(side="left")
            ctk.CTkLabel(mf, text=value, font=ctk.CTkFont(size=16, weight="bold"), text_color=color).pack(side="right")

        ctk.CTkButton(self, text=ar("إغلاق"), width=120, fg_color=COLORS["bg_input"], hover_color=COLORS["bg_card_hover"], command=self.destroy).pack(pady=15)
        self.after(100, lambda: _safe_grab(self))


class GameModeDialog(ctk.CTkToplevel):
    """نافذة اختيار الجهاز ذو الأولوية في وضع الألعاب"""
    def __init__(self, master, devices, on_confirm=None):
        super().__init__(master)
        self.title("Game Mode")
        self.geometry("440x460")
        self.configure(fg_color=COLORS["bg_dark"])
        self.resizable(False, False)
        self.on_confirm = on_confirm

        ctk.CTkLabel(self, text="🎮", font=ctk.CTkFont(size=40)).pack(pady=(15,3))
        ctk.CTkLabel(self, text=ar("اختر الجهاز ذو الأولوية"), font=ctk.CTkFont(size=18, weight="bold"), text_color=COLORS["accent_green"]).pack(pady=3)
        ctk.CTkLabel(self, text=ar("سيحصل هذا الجهاز على كامل السرعة\nبينما يُحدَّد الباقون بـ 512kbit"), font=ctk.CTkFont(size=12), text_color=COLORS["text_secondary"]).pack(pady=(0,8))

        scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_sidebar"], height=200)
        scroll.pack(fill="x", padx=20, pady=5)

        self.selected_ip = ctk.StringVar(value="")
        for dev in devices:
            ip = dev["ip"]
            vendor = dev.get("vendor", "غير معروف")
            hostname = dev.get("hostname", "")
            label = f"{ip}  •  {vendor}"
            if hostname and hostname != "غير معروف":
                label += f"  ({hostname})"
            if dev.get("is_local"):
                label += ar("  ← جهازك")
            ctk.CTkRadioButton(scroll, text=label, variable=self.selected_ip, value=ip,
                               font=ctk.CTkFont(size=12), text_color=COLORS["text_primary"]).pack(anchor="w", padx=10, pady=5)

        # تحديد جهازك افتراضياً
        local = next((d for d in devices if d.get("is_local")), None)
        if local:
            self.selected_ip.set(local["ip"])
        elif devices:
            self.selected_ip.set(devices[0]["ip"])

        # معلومة
        ctk.CTkLabel(self, text=ar("💡 اختر جهازك للألعاب، أو أي جهاز تريد إعطاءه الأولوية"),
                     font=ctk.CTkFont(size=11), text_color=COLORS["text_muted"], wraplength=380).pack(pady=(8,5))

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=12)
        ctk.CTkButton(btn_frame, text=ar("إلغاء"), width=130, height=36,
                      fg_color=COLORS["bg_input"], hover_color=COLORS["bg_card_hover"],
                      command=self.destroy).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text=ar("🎮 تفعيل وضع الألعاب"), width=180, height=36,
                      fg_color=COLORS["accent_green"], hover_color=COLORS["hover_green"],
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._confirm).pack(side="left", padx=10)

        self.after(100, lambda: _safe_grab(self))

    def _confirm(self):
        ip = self.selected_ip.get()
        if ip and self.on_confirm:
            self.on_confirm(ip)
        self.destroy()


class GameMonitorDialog(ctk.CTkToplevel):
    """نافذة المعلومات الحية لوضع الألعاب - تُظهر ping كل جهاز كإثبات"""
    def __init__(self, master, priority_ip, devices):
        super().__init__(master)
        self.title("🎮 Game Mode — Live Stats")
        self.geometry("480x420")
        self.configure(fg_color=COLORS["bg_dark"])
        self.resizable(False, False)
        self._running = True
        self._priority_ip = priority_ip
        self._devices = [d for d in devices if not d.get("is_router")]

        ctk.CTkLabel(self, text="🎮 " + ar("وضع الألعاب نشط"),
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=COLORS["accent_green"]).pack(pady=(15,3))
        ctk.CTkLabel(self, text=ar(f"الأولوية: {priority_ip}  •  الباقون محدودون بـ 512kbit"),
                     font=ctk.CTkFont(size=12), text_color=COLORS["text_secondary"]).pack(pady=(0,10))

        # جدول الأجهزة
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_sidebar"], corner_radius=8)
        header.pack(fill="x", padx=20, pady=(0,5))
        ctk.CTkLabel(header, text=ar("الجهاز"), width=160, font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=COLORS["text_muted"]).pack(side="left", padx=10, pady=6)
        ctk.CTkLabel(header, text="Ping (ms)", width=100, font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=COLORS["text_muted"]).pack(side="left")
        ctk.CTkLabel(header, text=ar("الحالة"), width=120, font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=COLORS["text_muted"]).pack(side="left")

        self._rows = {}
        scroll = ctk.CTkScrollableFrame(self, fg_color=COLORS["bg_sidebar"], corner_radius=8, height=220)
        scroll.pack(fill="x", padx=20, pady=0)

        for dev in self._devices:
            ip = dev["ip"]
            is_priority = (ip == priority_ip)
            row = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"] if is_priority else "transparent", corner_radius=6)
            row.pack(fill="x", pady=2, padx=3)

            icon = "⭐" if is_priority else "🔵"
            vendor = dev.get("vendor", "")[:18]
            ctk.CTkLabel(row, text=f"{icon} {ip}  {vendor}", width=200,
                         font=ctk.CTkFont(size=12), text_color=COLORS["text_primary"],
                         anchor="w").pack(side="left", padx=8, pady=6)

            ping_lbl = ctk.CTkLabel(row, text="...", width=80,
                                    font=ctk.CTkFont(size=13, weight="bold"),
                                    text_color=COLORS["text_muted"])
            ping_lbl.pack(side="left")

            status_lbl = ctk.CTkLabel(row, text="", width=120,
                                      font=ctk.CTkFont(size=11),
                                      text_color=COLORS["text_muted"])
            status_lbl.pack(side="left")

            self._rows[ip] = (ping_lbl, status_lbl, is_priority)

        ctk.CTkLabel(self, text=ar("🔄 يتحدث كل 3 ثوانٍ"),
                     font=ctk.CTkFont(size=11), text_color=COLORS["text_muted"]).pack(pady=8)
        ctk.CTkButton(self, text=ar("إغلاق"), width=120,
                      fg_color=COLORS["bg_input"], hover_color=COLORS["bg_card_hover"],
                      command=self._close).pack(pady=5)

        self.protocol("WM_DELETE_WINDOW", self._close)
        self.after(100, lambda: _safe_grab(self))
        # ابدأ التحديث
        threading.Thread(target=self._update_loop, daemon=True).start()

    def _ping_once(self, ip):
        """ping جهاز وإرجاع الـ latency بالـ ms أو None"""
        try:
            r = subprocess.run(["ping", "-c", "1", "-W", "2", ip],
                               capture_output=True, text=True)
            if r.returncode == 0:
                m = re.search(r"time=([\d.]+)", r.stdout)
                return float(m.group(1)) if m else 0.0
        except Exception:
            pass
        return None

    def _update_loop(self):
        import time
        while self._running:
            for dev in self._devices:
                if not self._running:
                    break
                ip = dev["ip"]
                latency = self._ping_once(ip)
                if ip in self._rows:
                    ping_lbl, status_lbl, is_priority = self._rows[ip]
                    if latency is not None:
                        if latency < 20:
                            color = COLORS["accent_green"]
                            status = ar("ممتاز 🟢") if is_priority else ar("محدود 🔴")
                        elif latency < 60:
                            color = COLORS["accent_orange"]
                            status = ar("جيد 🟡") if is_priority else ar("محدود 🔴")
                        else:
                            color = COLORS["accent_red"]
                            status = ar("بطيء 🔴")
                        try:
                            ping_lbl.after(0, lambda l=ping_lbl, v=f"{latency:.1f}", c=color: (
                                l.configure(text=v, text_color=c)))
                            status_lbl.after(0, lambda s=status_lbl, v=status: s.configure(text=v))
                        except Exception:
                            pass
                    else:
                        try:
                            ping_lbl.after(0, lambda l=ping_lbl: l.configure(text="—", text_color=COLORS["text_muted"]))
                            status_lbl.after(0, lambda s=status_lbl: s.configure(text=ar("غير متاح")))
                        except Exception:
                            pass
            time.sleep(3)

    def _close(self):
        self._running = False
        self.destroy()


class AlertDialog(ctk.CTkToplevel):
    def __init__(self, master, title_text, message, alert_type="info"):
        super().__init__(master)
        self.title(title_text)
        self.geometry("400x220")
        self.configure(fg_color=COLORS["bg_dark"])
        self.resizable(False, False)

        icons = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌", "new_device": "🆕"}
        colors = {"info": COLORS["accent_blue"], "success": COLORS["accent_green"], "warning": COLORS["accent_orange"], "error": COLORS["accent_red"], "new_device": COLORS["accent_cyan"]}

        ctk.CTkLabel(self, text=icons.get(alert_type, "ℹ️"), font=ctk.CTkFont(size=36)).pack(pady=(20,5))
        ctk.CTkLabel(self, text=message, font=ctk.CTkFont(size=14), text_color=colors.get(alert_type, COLORS["text_primary"]), wraplength=350).pack(pady=10)
        ctk.CTkButton(self, text=ar("حسناً"), width=100, fg_color=COLORS["bg_input"], hover_color=COLORS["bg_card_hover"], command=self.destroy).pack(pady=10)

        self.after(100, lambda: _safe_grab(self))
