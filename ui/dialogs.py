"""نوافذ الحوار"""
import customtkinter as ctk
import subprocess
import threading
import re
from utils.arabic import ar
from config import COLORS, DISCONNECT_DURATIONS, PALETTE_BG, PALETTE_CARD
from ui.smart_scroll import SmartScrollFrame


def _safe_grab(dialog):
    """تفعيل grab_set بأمان بعد ظهور النافذة"""
    try:
        dialog.grab_set()
    except Exception:
        pass


def _center(dialog):
    """توسيط النافذة على الشاشة"""
    dialog.update_idletasks()
    w = dialog.winfo_width()
    h = dialog.winfo_height()
    sw = dialog.winfo_screenwidth()
    sh = dialog.winfo_screenheight()
    dialog.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")


    """ربط عجلة الماوس بـ CTkScrollableFrame على Linux/Windows/Mac"""
    def _wheel(e):
        if e.num == 4:
            scrollable._parent_canvas.yview_scroll(-1, "units")
        elif e.num == 5:
            scrollable._parent_canvas.yview_scroll(1, "units")
        else:
            scrollable._parent_canvas.yview_scroll(int(-e.delta / 120), "units")
    for seq in ("<Button-4>", "<Button-5>", "<MouseWheel>"):
        scrollable.bind(seq, _wheel, add="+")
        scrollable._parent_canvas.bind(seq, _wheel, add="+")
        scrollable._scrollbar.bind(seq, _wheel, add="+")


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

        self.after(100, lambda: (_center(self), _safe_grab(self)))

    def _confirm(self):
        dur = DISCONNECT_DURATIONS.get(self.duration_var.get(), 300)
        if self.on_confirm:
            self.on_confirm(dur)
        self.destroy()


class PortResultDialog(ctk.CTkToplevel):
    def __init__(self, master, ip, ports):
        super().__init__(master)
        self.title(f"Port Scan - {ip}")
        self.geometry("620x520")
        self.configure(fg_color=COLORS["bg_dark"])

        open_ports   = [p for p in ports if p["state"] == "open"]
        closed_ports = [p for p in ports if p["state"] != "open"]

        ctk.CTkLabel(self, text=ar(f"🔍 نتائج فحص المنافذ — {ip}"),
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=COLORS["text_primary"]).pack(pady=(20, 3))

        summary = f"🟢 {len(open_ports)} مفتوح   🔴 {len(closed_ports)} مغلق"
        ctk.CTkLabel(self, text=ar(summary), font=ctk.CTkFont(size=13),
                     text_color=COLORS["text_secondary"]).pack(pady=(0, 10))

        scroll = SmartScrollFrame(self, fg_color=COLORS["bg_sidebar"])
        scroll.pack(fill="both", expand=True, padx=20, pady=5)

        if not ports:
            ctk.CTkLabel(scroll, text=ar("لم تُستلم أي نتائج — تأكد من صلاحيات sudo"),
                         text_color=COLORS["text_muted"]).pack(pady=50)
        elif not open_ports:
            ctk.CTkLabel(scroll, text=ar("✅ لا توجد منافذ مفتوحة — الجهاز محمي"),
                         font=ctk.CTkFont(size=14), text_color=COLORS["accent_green"]).pack(pady=20)
            # عرض أبرز المنافذ المغلقة
            ctk.CTkLabel(scroll, text=ar("المنافذ المفحوصة (كلها مغلقة):"),
                         font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"]).pack(anchor="w", padx=10, pady=(5,3))
            for p in closed_ports[:10]:
                pf = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"], corner_radius=6)
                pf.pack(fill="x", pady=2, padx=5)
                ctk.CTkLabel(pf,
                             text=f"⚫ Port {p['port']}/{p['protocol']}  •  {p['service']}  •  مغلق",
                             font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"]).pack(anchor="w", padx=12, pady=5)
        else:
            # عرض المفتوحة أولاً
            ctk.CTkLabel(scroll, text=ar("⚠️ المنافذ المفتوحة:"),
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=COLORS["accent_orange"]).pack(anchor="w", padx=10, pady=(5,3))
            for p in open_ports:
                pf = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"], corner_radius=8)
                pf.pack(fill="x", pady=3, padx=5)
                rl = p.get("risk_level", "unknown")
                color = COLORS["accent_red"] if rl == "high" else (COLORS["accent_orange"] if rl == "medium" else COLORS["accent_green"])
                icon  = "🔴" if rl == "high" else ("🟡" if rl == "medium" else "🟢")
                ctk.CTkLabel(pf,
                             text=f"{icon} Port {p['port']}/{p['protocol']}  •  {p['service']}",
                             font=ctk.CTkFont(size=13, weight="bold"),
                             text_color=color).pack(anchor="w", padx=15, pady=(8, 2))
                ctk.CTkLabel(pf, text=f"   {p.get('risk','')}",
                             font=ctk.CTkFont(size=11),
                             text_color=COLORS["text_secondary"]).pack(anchor="w", padx=15, pady=(0, 8))

        ctk.CTkButton(self, text=ar("إغلاق"), width=120,
                      fg_color=COLORS["bg_input"], hover_color=COLORS["bg_card_hover"],
                      command=self.destroy).pack(pady=12)
        self.after(100, lambda: (_center(self), _safe_grab(self)))


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
        self.after(100, lambda: (_center(self), _safe_grab(self)))


class GameModeDialog(ctk.CTkToplevel):
    """نافذة اختيار الجهاز + تحديد سرعة الآخرين"""
    def __init__(self, master, devices, on_confirm=None):
        super().__init__(master)
        self.title("Game Mode")
        self.geometry("460x540")
        self.minsize(440, 500)
        self.configure(fg_color=COLORS["bg_dark"])
        self.resizable(False, False)
        self.on_confirm = on_confirm

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(14, 0))
        ctk.CTkLabel(header, text="🎮", font=ctk.CTkFont(size=34)).pack()
        ctk.CTkLabel(header, text=ar("وضع الألعاب"),
                     font=ctk.CTkFont(size=17, weight="bold"),
                     text_color=COLORS["accent_green"]).pack()

        body = SmartScrollFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)

        # ── اختيار الجهاز ──
        ctk.CTkLabel(body, text=ar("الجهاز الذي تريد إعطاءه الأولوية (جهازك):"),
                     font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"]
                     ).pack(anchor="w", padx=20, pady=(8, 2))

        dev_frame = ctk.CTkFrame(body, fg_color=COLORS["bg_sidebar"], corner_radius=8)
        dev_frame.pack(fill="x", padx=16, pady=(0, 8))

        self.selected_ip = ctk.StringVar(value="")
        local = next((d for d in devices if d.get("is_local")), None)
        for dev in devices:
            ip = dev["ip"]
            hostname = dev.get("hostname", "")
            label = ip
            if hostname and hostname not in ("غير معروف", "localhost"):
                label += f"  —  {hostname}"
            if dev.get("is_local"):
                label += ar("  ← جهازك")
            ctk.CTkRadioButton(dev_frame, text=label, variable=self.selected_ip, value=ip,
                               font=ctk.CTkFont(size=12),
                               text_color=COLORS["text_primary"]
                               ).pack(anchor="w", padx=12, pady=4)

        if local:
            self.selected_ip.set(local["ip"])
        elif devices:
            self.selected_ip.set(devices[0]["ip"])

        ctk.CTkFrame(body, height=1, fg_color=COLORS["bg_input"]).pack(fill="x", padx=16, pady=(4, 10))

        # ── قياس السرعة ──
        speed_header = ctk.CTkFrame(body, fg_color="transparent")
        speed_header.pack(fill="x", padx=20, pady=(0, 4))
        ctk.CTkLabel(speed_header,
                     text=ar("سرعة الإنترنت عندك (Mbps):"),
                     font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"]
                     ).pack(side="left")
        self._measure_btn = ctk.CTkButton(
            speed_header, text=ar("📡 قياس تلقائي"), width=120, height=24,
            font=ctk.CTkFont(size=11),
            fg_color=COLORS["accent_blue"], hover_color=COLORS["hover_blue"],
            command=self._auto_measure
        )
        self._measure_btn.pack(side="right")

        speed_frame = ctk.CTkFrame(body, fg_color=COLORS["bg_sidebar"], corner_radius=8)
        speed_frame.pack(fill="x", padx=16, pady=(0, 8))

        for label_txt, var_default, attr in [
            ("⬇️  تحميل (Mbps):", "0.0", "_dl_var"),
            ("⬆️  رفع (Mbps):",   "0.0", "_ul_var"),
        ]:
            row = ctk.CTkFrame(speed_frame, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=5)
            ctk.CTkLabel(row, text=ar(label_txt), font=ctk.CTkFont(size=12),
                         text_color=COLORS["text_secondary"], width=180, anchor="w").pack(side="left")
            var = ctk.StringVar(value=var_default)
            setattr(self, attr, var)
            ctk.CTkEntry(row, textvariable=var, width=80, height=28,
                         fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"],
                         font=ctk.CTkFont(size=12)).pack(side="left", padx=8)

        ctk.CTkFrame(body, height=1, fg_color=COLORS["bg_input"]).pack(fill="x", padx=16, pady=(0, 10))

        # ── الشريط: كم % يحصل عليه الآخرون ──
        ctk.CTkLabel(body,
                     text=ar("كم % من السرعة يحصل عليه باقي الأجهزة؟"),
                     font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"]
                     ).pack(anchor="w", padx=20, pady=(0, 2))
        ctk.CTkLabel(body,
                     text=ar("مثال: 20% تعني أن كل جهاز آخر لن يتجاوز 20% من سرعتك"),
                     font=ctk.CTkFont(size=10), text_color=COLORS["text_muted"]
                     ).pack(anchor="w", padx=20, pady=(0, 6))

        slider_outer = ctk.CTkFrame(body, fg_color=COLORS["bg_sidebar"], corner_radius=8)
        slider_outer.pack(fill="x", padx=16, pady=(0, 4))

        slider_row = ctk.CTkFrame(slider_outer, fg_color="transparent")
        slider_row.pack(fill="x", padx=12, pady=8)

        self._pct_var = ctk.IntVar(value=20)
        self._pct_lbl = ctk.CTkLabel(slider_row, text="20%",
                                      font=ctk.CTkFont(size=13, weight="bold"),
                                      text_color=COLORS["accent_orange"], width=45)
        self._pct_lbl.pack(side="right")
        ctk.CTkSlider(slider_row, from_=5, to=50, number_of_steps=45,
                      variable=self._pct_var,
                      button_color=COLORS["accent_orange"],
                      progress_color=COLORS["accent_orange"],
                      command=self._on_slider).pack(side="left", fill="x", expand=True)

        # نتيجة الحساب بشكل واضح
        self._calc_lbl = ctk.CTkLabel(body, text="",
                                       font=ctk.CTkFont(size=12, weight="bold"),
                                       text_color=COLORS["accent_orange"])
        self._calc_lbl.pack(pady=(4, 8))

        self._dl_var.trace_add("write", lambda *_: self._update_calc())
        self._ul_var.trace_add("write", lambda *_: self._update_calc())
        self._update_calc()

        # Footer
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=2, column=0, pady=(4, 12))
        ctk.CTkButton(footer, text=ar("إلغاء"), width=120, height=34,
                      fg_color=COLORS["bg_input"], hover_color=COLORS["bg_card_hover"],
                      command=self.destroy).pack(side="left", padx=8)
        ctk.CTkButton(footer, text=ar("🎮 تفعيل"), width=160, height=34,
                      fg_color=COLORS["accent_green"], hover_color=COLORS["hover_green"],
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._confirm).pack(side="left", padx=8)

        self.after(100, lambda: (_center(self), _safe_grab(self)))

    def _auto_measure(self):
        self._measure_btn.configure(state="disabled", text=ar("⏳ جاري القياس..."))
        def _measure():
            from utils.network import measure_interface_speed
            dl, ul = measure_interface_speed(duration=1.5)
            self.after(0, lambda: self._set_speed(dl, ul))
        threading.Thread(target=_measure, daemon=True).start()

    def _set_speed(self, dl, ul):
        self._dl_var.set(str(dl if dl > 0 else 1.0))
        self._ul_var.set(str(ul if ul > 0 else 0.5))
        self._measure_btn.configure(state="normal", text=ar("📡 قياس تلقائي"))
        self._update_calc()

    def _on_slider(self, val):
        self._pct_lbl.configure(text=f"{int(val)}%")
        self._update_calc()

    def _update_calc(self):
        try:
            dl = float(self._dl_var.get())
            ul = float(self._ul_var.get())
            pct = self._pct_var.get() / 100
            dl_limit = max(0.1, round(dl * pct, 2))
            ul_limit = max(0.1, round(ul * pct, 2))
            self._calc_lbl.configure(
                text=ar(f"⬇️ الآخرون سيحصلون على: {dl_limit} Mbps تحميل  |  {ul_limit} Mbps رفع")
            )
        except (ValueError, ZeroDivisionError):
            self._calc_lbl.configure(text=ar("أدخل أرقاماً صحيحة"))

    def _confirm(self):
        ip = self.selected_ip.get()
        if not ip:
            return
        try:
            dl = float(self._dl_var.get())
            ul = float(self._ul_var.get())
            pct = self._pct_var.get() / 100
            dl_kbit = max(64, int(dl * pct * 1000))
            ul_kbit = max(64, int(ul * pct * 1000))
        except ValueError:
            dl_kbit, ul_kbit = 512, 256
        if self.on_confirm:
            self.on_confirm(ip, dl_kbit, ul_kbit)
        self.destroy()



class GameMonitorDialog(ctk.CTkToplevel):
    """نافذة المعلومات الحية لوضع الألعاب"""
    def __init__(self, master, priority_ip, devices, dl_limit_kbit=512, ul_limit_kbit=256):
        super().__init__(master)
        self.title("🎮 Game Mode — Live Stats")
        self.geometry("460x400")
        self.configure(fg_color=COLORS["bg_dark"])
        self.resizable(False, False)
        self._running = True
        self._priority_ip = priority_ip
        self._devices = [d for d in devices if not d.get("is_router")]

        ctk.CTkLabel(self, text="🎮 " + ar("وضع الألعاب نشط"),
                     font=ctk.CTkFont(size=17, weight="bold"),
                     text_color=COLORS["accent_green"]).pack(pady=(14, 2))

        # عرض IP + اسم فقط
        priority_dev = next((d for d in devices if d["ip"] == priority_ip), None)
        priority_label = priority_ip
        if priority_dev:
            name = priority_dev.get("hostname", "")
            if name and name not in ("غير معروف", "localhost"):
                priority_label = f"{priority_ip}  —  {name}"

        dl_mbps = round(dl_limit_kbit / 1000, 2)
        ul_mbps = round(ul_limit_kbit / 1000, 2)
        ctk.CTkLabel(self,
                     text=ar(f"الأولوية: {priority_label}\nالآخرون: ⬇️{dl_mbps} Mbps  ⬆️{ul_mbps} Mbps"),
                     font=ctk.CTkFont(size=11), text_color=COLORS["text_secondary"],
                     justify="center").pack(pady=(0, 8))

        # جدول
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_sidebar"], corner_radius=8)
        header.pack(fill="x", padx=20, pady=(0, 4))
        for txt, w in [(ar("الجهاز"), 200), ("Ping (ms)", 90), (ar("الحالة"), 110)]:
            ctk.CTkLabel(header, text=txt, width=w,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=COLORS["text_muted"]).pack(side="left", padx=6, pady=5)

        self._rows = {}
        scroll = SmartScrollFrame(self, fg_color=COLORS["bg_sidebar"], corner_radius=8, height=200)
        scroll.pack(fill="x", padx=20)

        for dev in self._devices:
            ip = dev["ip"]
            is_priority = (ip == priority_ip)
            row = ctk.CTkFrame(scroll,
                               fg_color=COLORS["bg_card"] if is_priority else "transparent",
                               corner_radius=6)
            row.pack(fill="x", pady=2, padx=3)

            # IP + اسم فقط
            hostname = dev.get("hostname", "")
            display = f"{'⭐' if is_priority else '🔵'} {ip}"
            if hostname and hostname not in ("غير معروف", "localhost"):
                display += f"  {hostname}"

            ctk.CTkLabel(row, text=display, width=200,
                         font=ctk.CTkFont(size=11), text_color=COLORS["text_primary"],
                         anchor="w").pack(side="left", padx=8, pady=5)

            ping_lbl = ctk.CTkLabel(row, text="...", width=80,
                                    font=ctk.CTkFont(size=12, weight="bold"),
                                    text_color=COLORS["text_muted"])
            ping_lbl.pack(side="left")

            status_lbl = ctk.CTkLabel(row, text="", width=110,
                                      font=ctk.CTkFont(size=11),
                                      text_color=COLORS["text_muted"])
            status_lbl.pack(side="left")
            self._rows[ip] = (ping_lbl, status_lbl, is_priority)

        ctk.CTkLabel(self, text=ar("🔄 يتحدث كل 3 ثوانٍ"),
                     font=ctk.CTkFont(size=10), text_color=COLORS["text_muted"]).pack(pady=6)
        ctk.CTkButton(self, text=ar("إغلاق"), width=110,
                      fg_color=COLORS["bg_input"], hover_color=COLORS["bg_card_hover"],
                      command=self._close).pack(pady=4)

        self.protocol("WM_DELETE_WINDOW", self._close)
        self.after(100, lambda: (_center(self), _safe_grab(self)))
        threading.Thread(target=self._update_loop, daemon=True).start()

    def _ping_once(self, ip):
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
                if ip not in self._rows:
                    continue
                ping_lbl, status_lbl, is_priority = self._rows[ip]
                if latency is not None:
                    color = (COLORS["accent_green"] if latency < 50
                             else COLORS["accent_orange"] if latency < 150
                             else COLORS["accent_red"])
                    status = ar("أولوية ⭐") if is_priority else ar("محدود 🔴")
                    try:
                        ping_lbl.after(0, lambda l=ping_lbl, v=f"{latency:.0f}", c=color:
                                       l.configure(text=v, text_color=c))
                        status_lbl.after(0, lambda s=status_lbl, v=status:
                                         s.configure(text=v))
                    except Exception:
                        pass
                else:
                    try:
                        ping_lbl.after(0, lambda l=ping_lbl:
                                       l.configure(text="—", text_color=COLORS["text_muted"]))
                        status_lbl.after(0, lambda s=status_lbl:
                                         s.configure(text=ar("غير متاح")))
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

        self.after(100, lambda: (_center(self), _safe_grab(self)))


class ColorPickerDialog(ctk.CTkToplevel):
    """نافذة اختيار لون الخلفية والقوالب ديناميكياً"""

    def __init__(self, master, on_apply=None):
        super().__init__(master)
        self.title("🎨 اختيار الألوان")
        self.geometry("580x660")
        self.minsize(580, 600)
        self.configure(fg_color=COLORS["bg_dark"])
        self.resizable(True, True)
        self.on_apply = on_apply

        import config
        self._sel_bg   = ctk.StringVar(value=config.COLORS["bg_dark"])
        self._sel_card = ctk.StringVar(value=config.COLORS["bg_sidebar"])
        self._target   = ctk.StringVar(value=config.CURRENT_THEME)  # dark أو light

        # ── العنوان ──────────────────────────────────────
        ctk.CTkLabel(self, text=ar("🎨 تخصيص الألوان"),
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=COLORS["text_primary"]).pack(pady=(18, 2))
        ctk.CTkLabel(self, text=ar("اختر لون الخلفية ولون القوالب"),
                     font=ctk.CTkFont(size=12),
                     text_color=COLORS["text_muted"]).pack(pady=(0, 8))

        # ── الأزرار في الأعلى دائماً مرئية ──────────────
        btn_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_sidebar"], corner_radius=10)
        btn_frame.pack(fill="x", padx=16, pady=(0, 8))

        # طبّق على
        ctk.CTkLabel(btn_frame, text=ar("طبّق على:"),
                     font=ctk.CTkFont(size=11),
                     text_color=COLORS["text_muted"]).pack(side="left", padx=(12,4), pady=8)
        ctk.CTkRadioButton(btn_frame, text=ar("🌙 ليلي"), variable=self._target, value="dark",
                           font=ctk.CTkFont(size=11), text_color=COLORS["text_primary"],
                           fg_color=COLORS["accent_gold"], hover_color=COLORS["hover_gold"]
                           ).pack(side="left", padx=(0,6))
        ctk.CTkRadioButton(btn_frame, text=ar("☀️ نهاري"), variable=self._target, value="light",
                           font=ctk.CTkFont(size=11), text_color=COLORS["text_primary"],
                           fg_color=COLORS["accent_gold"], hover_color=COLORS["hover_gold"]
                           ).pack(side="left", padx=(0,10))

        # معاينة
        ctk.CTkLabel(btn_frame, text=ar("معاينة:"),
                     font=ctk.CTkFont(size=11),
                     text_color=COLORS["text_muted"]).pack(side="left", padx=(12, 6), pady=8)
        self.prev_bg = ctk.CTkFrame(btn_frame, width=28, height=20, corner_radius=4,
                                    fg_color=self._sel_bg.get(),
                                    border_width=1, border_color=COLORS["bg_input"])
        self.prev_bg.pack(side="left", padx=(0,3))
        self.prev_bg.pack_propagate(False)
        ctk.CTkLabel(btn_frame, text=ar("خلفية"),
                     font=ctk.CTkFont(size=10),
                     text_color=COLORS["text_muted"]).pack(side="left", padx=(0,8))
        self.prev_card = ctk.CTkFrame(btn_frame, width=28, height=20, corner_radius=4,
                                      fg_color=self._sel_card.get(),
                                      border_width=1, border_color=COLORS["bg_input"])
        self.prev_card.pack(side="left", padx=(0,3))
        self.prev_card.pack_propagate(False)
        ctk.CTkLabel(btn_frame, text=ar("قوالب"),
                     font=ctk.CTkFont(size=10),
                     text_color=COLORS["text_muted"]).pack(side="left", padx=(0,12))

        ctk.CTkButton(btn_frame, text=ar("✅ تطبيق"), width=130, height=32,
                      fg_color=COLORS["accent_gold"], hover_color=COLORS["hover_gold"],
                      text_color=COLORS["text_primary"],
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._apply).pack(side="right", padx=(0,6), pady=6)
        ctk.CTkButton(btn_frame, text=ar("إلغاء"), width=90, height=32,
                      fg_color=COLORS["bg_input"], hover_color=COLORS["bg_card_hover"],
                      text_color=COLORS["text_secondary"],
                      command=self.destroy).pack(side="right", padx=(0,4), pady=6)

        # تحديث المعاينة عند التغيير
        self._sel_bg.trace_add("write",   lambda *_: self.prev_bg.configure(fg_color=self._sel_bg.get()))
        self._sel_card.trace_add("write", lambda *_: self.prev_card.configure(fg_color=self._sel_card.get()))

        # ── القوائم ──────────────────────────────────────
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=16, pady=(0,12))
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(content, text=ar("🖥️  لون الخلفية"),
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=COLORS["text_primary"]).grid(row=0, column=0, pady=(0,6))
        bg_scroll = SmartScrollFrame(content, fg_color=COLORS["bg_sidebar"],
                                           corner_radius=10)
        bg_scroll.grid(row=1, column=0, sticky="nsew", padx=(0,6))
        for name, hex_color, emoji in PALETTE_BG:
            self._color_row(bg_scroll, name, hex_color, emoji, self._sel_bg)

        ctk.CTkLabel(content, text=ar("🗂️  لون القوالب"),
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=COLORS["text_primary"]).grid(row=0, column=1, pady=(0,6))
        card_scroll = SmartScrollFrame(content, fg_color=COLORS["bg_sidebar"],
                                             corner_radius=10)
        card_scroll.grid(row=1, column=1, sticky="nsew", padx=(6,0))
        for name, hex_color, emoji in PALETTE_CARD:
            self._color_row(card_scroll, name, hex_color, emoji, self._sel_card)

        self.after(100, lambda: (_center(self), _safe_grab(self)))

    def _color_row(self, parent, name, hex_color, emoji, var):
        """صف لون واحد مع مربع اللون والاسم"""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=2, padx=4)

        # مربع اللون
        swatch = ctk.CTkFrame(row, width=22, height=22, corner_radius=4,
                               fg_color=hex_color,
                               border_width=1, border_color=COLORS["bg_input"])
        swatch.pack(side="left", padx=(4, 6))
        swatch.pack_propagate(False)

        rb = ctk.CTkRadioButton(
            row,
            text=f"{emoji} {name}  {hex_color}",
            variable=var, value=hex_color,
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_primary"],
            fg_color=COLORS["accent_gold"],
            hover_color=COLORS["hover_gold"],
        )
        rb.pack(side="left")

    def _apply(self):
        if self.on_apply:
            self.on_apply(self._sel_bg.get(), self._sel_card.get(), self._target.get())
        self.destroy()
