"""النافذة الرئيسية للتطبيق"""
import customtkinter as ctk
from datetime import datetime
from utils.arabic import ar
from utils.network import get_local_network, get_gateway_ip, is_nmap_installed, is_root
from utils.exporter import export_csv, export_pdf, export_json
from utils.logger import log
import utils.settings as settings
import utils.history as history
from core.scanner import NetworkScanner
from core.disconnector import Disconnector
from core.port_scanner import PortScanner
from core.game_mode import GameMode
from core.speed_test import SpeedTester
from core.monitor import NetworkMonitor
from ui.themes import setup_theme, toggle_theme
from ui.sidebar import Sidebar
from ui.device_card import DeviceCard
from ui.smart_scroll import SmartScrollFrame
from ui.dialogs import DisconnectDialog, PortResultDialog, SpeedResultDialog, AlertDialog, GameModeDialog, GameMonitorDialog, ColorPickerDialog
from config import COLORS, APP_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT


class NetworkSniperApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # تحميل الإعدادات المحفوظة
        self._settings = settings.load()
        self._apply_saved_theme()

        self.title(APP_TITLE)
        self.minsize(820, 560)
        self.configure(fg_color=COLORS["bg_dark"])
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0, minsize=250)
        self.grid_rowconfigure(0, weight=1)
        # توسيط النافذة الرئيسية
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - WINDOW_WIDTH) // 2
        y = (sh - WINDOW_HEIGHT) // 2
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
        # المحركات
        self.scanner = NetworkScanner()
        self.disconnector = Disconnector()
        self.port_scanner = PortScanner()
        self.game_mode = GameMode()
        self.speed_tester = SpeedTester()
        self.monitor = NetworkMonitor(self.scanner)

        # البيانات
        self.devices = []
        self.port_results = {}
        self.is_monitoring = False

        # بناء الواجهة
        self._build_sidebar()
        self._build_main_area()

        # تحميل النطاق المحفوظ في حقل الإدخال
        saved_net = self._settings.get("network_range", "")
        if saved_net:
            self.sidebar.set_network_range(saved_net)

        # تنظيف عند الإغلاق
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        # اعتراض زر التصغير — نستخدم withdraw لأن iconify لا يعمل على كل بيئات Linux
        self.protocol("WM_ICONIFY_WINDOW", self._hide_window)
        self._is_hidden = False

        log.info("تم تشغيل التطبيق")

    def _apply_saved_theme(self):
        """تطبيق الثيم والألوان المحفوظة"""
        import config
        saved_theme = self._settings.get("theme", "dark")
        for palette_key, config_palette in [("colors_dark", config.COLORS_DARK),
                                             ("colors_light", config.COLORS_LIGHT)]:
            saved_colors = self._settings.get(palette_key, {})
            if saved_colors:
                config_palette.update(saved_colors)
        setup_theme(saved_theme)

    def _build_sidebar(self):
        self.sidebar = Sidebar(self, callbacks={
            "scan": self.start_scan,
            "stop": self.stop_scan,
            "monitor": self.toggle_monitor,
            "game_mode": self.toggle_game_mode,
            "speed_test": self.start_speed_test,
            "export_csv": self.do_export_csv,
            "export_json": self.do_export_json,
            "export_pdf": self.do_export_pdf,
            "toggle_theme": self.do_toggle_theme,
            "color_picker": self.open_color_picker,
        })
        # نفس الهوامش من كل الجهات — عائم
        self.sidebar.grid(row=0, column=1, sticky="nsew", padx=(6, 12), pady=12)

    def _build_main_area(self):
        # الإطار الرئيسي — نفس الهوامش من كل الجهات، عائم
        self.main_frame = ctk.CTkFrame(
            self, corner_radius=16,
            fg_color=COLORS["bg_sidebar"],
            border_width=0
        )
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=(12, 6), pady=12)

        # العنوان
        header = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(18, 4))

        self.main_title = ctk.CTkLabel(
            header, text=ar("الأجهزة المتصلة بالشبكة"),
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.main_title.pack(side="left")

        self.device_count = ctk.CTkLabel(
            header, text="",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"]
        )
        self.device_count.pack(side="right")

        # معلومات الشبكة
        info_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=20, pady=(0, 6))

        net = get_local_network()
        self.network_label = ctk.CTkLabel(
            info_frame, text=f"🌐  {net}",
            text_color=COLORS["text_secondary"],
            font=ctk.CTkFont(size=12)
        )
        self.network_label.pack(side="left")

        self.status_label = ctk.CTkLabel(
            info_frame, text="",
            text_color=COLORS["accent_green"],
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="right")

        # شريط التقدم
        self.progress = ctk.CTkProgressBar(
            self.main_frame, mode="indeterminate",
            height=3, progress_color=COLORS["accent_gold"],
            fg_color=COLORS["bg_input"]
        )
        self.progress.pack(fill="x", padx=20, pady=(0, 6))
        self.progress.set(0)

        # قائمة الأجهزة
        self.devices_list = SmartScrollFrame(
            self.main_frame,
            fg_color=COLORS["bg_dark"],
            corner_radius=12
        )
        self.devices_list.pack(pady=4, padx=14, fill="both", expand=True)

        # شريط الحالة
        self.statusbar = ctk.CTkFrame(
            self.main_frame, height=32,
            fg_color=COLORS["bg_input"],
            corner_radius=10
        )
        self.statusbar.pack(fill="x", padx=14, pady=(6, 12))

        self.statusbar_text = ctk.CTkLabel(
            self.statusbar, text=ar("جاهز"),
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"]
        )
        self.statusbar_text.pack(side="left", padx=14)

        self.time_label = ctk.CTkLabel(
            self.statusbar, text="",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"]
        )
        self.time_label.pack(side="right", padx=14)

        self._show_welcome()

    def _show_welcome(self):
        self._clear_list()
        wf = ctk.CTkFrame(self.devices_list, fg_color="transparent")
        wf.pack(expand=True, fill="both")
        ctk.CTkLabel(wf, text="🔫", font=ctk.CTkFont(size=48)).pack(pady=(80,10))
        ctk.CTkLabel(wf, text=ar("مرحباً بك في Network Sniper Pro"), font=ctk.CTkFont(size=20, weight="bold"), text_color=COLORS["text_primary"]).pack(pady=5)
        ctk.CTkLabel(wf, text=ar("اضغط على 'رادار الشبكة' لبدء فحص الأجهزة المتصلة"), font=ctk.CTkFont(size=14), text_color=COLORS["text_secondary"]).pack(pady=5)

        if not is_nmap_installed():
            ctk.CTkLabel(wf, text=ar("⚠️ Nmap غير مثبت! قم بتثبيته: sudo apt install nmap"), font=ctk.CTkFont(size=13), text_color=COLORS["accent_red"]).pack(pady=10)
        if not is_root():
            ctk.CTkLabel(wf, text=ar("⚠️ يُنصح بالتشغيل كـ root: sudo python3 main.py"), font=ctk.CTkFont(size=13), text_color=COLORS["accent_orange"]).pack(pady=5)

    def _clear_list(self):
        for w in self.devices_list.winfo_children():
            w.destroy()

    def _set_status(self, text, color=None):
        self.statusbar_text.configure(text=ar(text), text_color=color or COLORS["text_muted"])

    # ====== فحص الشبكة ======
    def start_scan(self):
        if not is_nmap_installed():
            self._clear_list()
            ctk.CTkLabel(self.devices_list, text=ar("❌ Nmap غير مثبت! sudo apt install nmap"), text_color=COLORS["accent_red"], font=ctk.CTkFont(size=16)).pack(pady=100)
            return

        self._clear_list()
        self.sidebar.set_scanning(True)
        self.progress.configure(mode="indeterminate")
        self.progress.start()
        self._set_status("جاري الفحص...", COLORS["accent_blue"])

        ctk.CTkLabel(self.devices_list, text=ar("🔍 جاري تمشيط الشبكة، يرجى الانتظار..."), font=ctk.CTkFont(size=16), text_color=COLORS["accent_blue"]).pack(pady=100)

        # استخدام النطاق المدخل يدوياً أو الاكتشاف التلقائي
        custom = self.sidebar.get_network_range()
        from utils.network import validate_network_range
        net = custom if custom and validate_network_range(custom) else get_local_network()
        # حفظ النطاق المستخدم
        settings.set("network_range", net)
        self.network_label.configure(text=f"🌐 {net}")
        self.scanner.scan(net, on_complete=lambda d: self.after(0, lambda: self._on_scan_complete(d)), on_error=lambda e: self.after(0, lambda: self._on_scan_error(e)), on_progress=lambda m: self.after(0, lambda: self._set_status(m, COLORS["accent_blue"])))

    def stop_scan(self):
        self.scanner.stop()
        self.progress.stop()
        self.progress.set(0)
        self.sidebar.set_scanning(False)
        self._clear_list()
        ctk.CTkLabel(self.devices_list, text=ar("🛑 تم إيقاف الفحص"), text_color=COLORS["accent_orange"], font=ctk.CTkFont(size=16)).pack(pady=100)
        self._set_status("تم الإيقاف", COLORS["accent_orange"])

    def _on_scan_complete(self, devices):
        self.progress.stop()
        self.progress.set(0)
        self.sidebar.set_scanning(False)
        self.devices = devices
        # حفظ في قاعدة البيانات
        for dev in devices:
            history.upsert_device(dev)
        self._render_devices()
        now = datetime.now().strftime("%H:%M:%S")
        self._set_status(f"آخر فحص: {now} — {len(devices)} جهاز", COLORS["accent_green"])
        self.time_label.configure(text=now)
        self.device_count.configure(text=f"{len(devices)} " + ar("جهاز"))
        log.info(f"عرض {len(devices)} جهاز")

    def _on_scan_error(self, msg):
        self.progress.stop()
        self.progress.set(0)
        self.sidebar.set_scanning(False)
        self._clear_list()
        ctk.CTkLabel(self.devices_list, text=ar("❌ حدث خطأ أثناء الفحص"), text_color=COLORS["accent_red"], font=ctk.CTkFont(size=16)).pack(pady=(80,10))
        ctk.CTkLabel(self.devices_list, text=msg, text_color=COLORS["text_muted"], font=ctk.CTkFont(size=11), wraplength=500).pack(pady=5)
        self._set_status("خطأ في الفحص", COLORS["accent_red"])

    def _render_devices(self):
        self._clear_list()
        if not self.devices:
            ctk.CTkLabel(self.devices_list, text=ar("الشبكة فارغة أو الفحص يحتاج صلاحيات sudo"), text_color=COLORS["accent_orange"], font=ctk.CTkFont(size=15)).pack(pady=100)
            return
        for dev in self.devices:
            is_disc = self.disconnector.is_disconnected(dev["ip"])
            card = DeviceCard(self.devices_list, dev, on_disconnect=self._ask_disconnect, on_reconnect=self._do_reconnect, on_port_scan=self._do_port_scan, on_copy_mac=self._copy_mac, is_disconnected=is_disc, on_rename=self._render_devices)
            card.pack(fill="x", pady=4, padx=5)

    # ====== قطع الاتصال ======
    def _ask_disconnect(self, dev):
        DisconnectDialog(self, dev, on_confirm=lambda dur: self._do_disconnect(dev, dur))

    def _do_disconnect(self, dev, duration):
        ip = dev["ip"]
        mac = dev["mac"]
        gw = get_gateway_ip()
        def on_status(target_ip, status):
            self.after(0, lambda: self._render_devices())
        success = self.disconnector.disconnect(ip, mac, gw, duration=duration, on_status=on_status)
        if success:
            self._set_status(f"تم قطع {ip}", COLORS["accent_red"])
            self.after(500, self._render_devices)
        else:
            AlertDialog(self, "Error", ar("فشل قطع الاتصال"), "error")

    def _do_reconnect(self, dev):
        ip = dev["ip"]
        self.disconnector.reconnect(ip)
        self._set_status(f"تم إعادة اتصال {ip}", COLORS["accent_green"])
        self.after(500, self._render_devices)

    # ====== فحص المنافذ ======
    def _do_port_scan(self, dev):
        ip = dev["ip"]
        self._set_status(f"جاري فحص منافذ {ip}...", COLORS["accent_blue"])
        self.progress.configure(mode="indeterminate")
        self.progress.start()
        def on_done(target_ip, ports):
            self.after(0, lambda: self._show_ports(target_ip, ports))
        def on_err(msg):
            self.after(0, lambda: self._port_error(msg))
        self.port_scanner.scan_ports(ip, on_complete=on_done, on_error=on_err)

    def _show_ports(self, ip, ports):
        self.progress.stop()
        self.progress.set(0)
        self.port_results[ip] = ports
        self._set_status(f"فحص المنافذ: {len(ports)} منفذ مفتوح في {ip}", COLORS["accent_green"])
        PortResultDialog(self, ip, ports)

    def _port_error(self, msg):
        self.progress.stop()
        self.progress.set(0)
        self._set_status("خطأ في فحص المنافذ", COLORS["accent_red"])
        AlertDialog(self, "Error", msg, "error")

    # ====== نسخ MAC ======
    def _copy_mac(self, mac):
        self.clipboard_clear()
        self.clipboard_append(mac)
        self._set_status(f"تم نسخ MAC: {mac}", COLORS["accent_green"])

    # ====== وضع الألعاب ======
    def toggle_game_mode(self):
        if self.game_mode.is_active:
            def on_status(active, msg):
                self.after(0, lambda: self._game_status(active, msg))
            self.game_mode.deactivate(on_status=on_status)
        else:
            if not self.devices:
                from utils.network import get_local_ip
                self._start_game_mode(get_local_ip(), 512, 256)
            else:
                GameModeDialog(self, self.devices, on_confirm=self._start_game_mode)

    def _start_game_mode(self, priority_ip, dl_kbit=512, ul_kbit=256):
        def on_status(active, msg):
            self.after(0, lambda: self._game_status(active, msg, priority_ip, dl_kbit, ul_kbit))
        self.game_mode.activate(priority_ip, on_status=on_status, dl_kbit=dl_kbit, ul_kbit=ul_kbit)

    def _game_status(self, active, msg, priority_ip=None, dl_kbit=512, ul_kbit=256):
        self.sidebar.set_game_mode(active)
        color = COLORS["accent_green"] if active else COLORS["text_muted"]
        self._set_status(msg, color)
        if active and priority_ip and self.devices:
            GameMonitorDialog(self, priority_ip, self.devices, dl_kbit, ul_kbit)

    # ====== اختبار السرعة ======
    def start_speed_test(self):
        if not self.speed_tester.is_available():
            AlertDialog(self, "Error", ar("speedtest-cli غير مثبت!\npip install speedtest-cli"), "error")
            return
        self._set_status("جاري اختبار السرعة...", COLORS["accent_orange"])
        self.progress.configure(mode="indeterminate")
        self.progress.start()
        def on_done(result):
            self.after(0, lambda: self._speed_done(result))
        def on_err(msg):
            self.after(0, lambda: self._speed_error(msg))
        def on_prog(msg):
            self.after(0, lambda: self._set_status(msg, COLORS["accent_orange"]))
        self.speed_tester.run_test(on_complete=on_done, on_error=on_err, on_progress=on_prog)

    def _speed_done(self, result):
        self.progress.stop()
        self.progress.set(0)
        self._set_status(f"السرعة: ↓{result['download']}Mbps ↑{result['upload']}Mbps", COLORS["accent_green"])
        SpeedResultDialog(self, result)

    def _speed_error(self, msg):
        self.progress.stop()
        self.progress.set(0)
        self._set_status("خطأ في اختبار السرعة", COLORS["accent_red"])
        AlertDialog(self, "Error", msg, "error")

    # ====== المراقبة الحية ======
    def toggle_monitor(self):
        if self.is_monitoring:
            self.monitor.stop()
            self.is_monitoring = False
            self.sidebar.set_monitoring(False)
            self._set_status("تم إيقاف المراقبة", COLORS["text_muted"])
        else:
            net = get_local_network()
            if self.devices:
                self.monitor.set_initial_devices(self.devices)
            def on_new(dev):
                self.after(0, lambda: self._on_new_device(dev))
            def on_left(dev):
                self.after(0, lambda: self._on_device_left(dev))
            def on_update(devs):
                self.after(0, lambda: self._on_monitor_update(devs))
            self.monitor.start(net, on_new_device=on_new, on_device_left=on_left, on_update=on_update)
            self.is_monitoring = True
            self.sidebar.set_monitoring(True)
            self._set_status("المراقبة الحية نشطة", COLORS["accent_purple"])

    def _on_new_device(self, dev):
        ip = dev.get("ip", "?")
        vendor = dev.get("vendor", "?")
        hostname = dev.get("hostname", "")
        history.upsert_device(dev)
        history.log_event(dev.get("mac",""), ip, "connected")
        self._set_status(f"🆕 جهاز جديد: {ip} ({vendor})", COLORS["accent_cyan"])
        # إشعار نظام
        name = hostname if hostname and hostname != "غير معروف" else vendor
        try:
            import subprocess as _sp
            _sp.Popen(["notify-send", "-i", "network-wireless",
                       "Network Sniper Pro", f"جهاز جديد: {ip}\n{name}"],
                      stdout=_sp.DEVNULL, stderr=_sp.DEVNULL)
        except Exception:
            pass
        AlertDialog(self, "New Device", f"🆕 {ar('جهاز جديد اتصل بالشبكة')}\nIP: {ip}\nVendor: {vendor}", "new_device")

    def _on_device_left(self, dev):
        ip = dev.get("ip", "?")
        history.log_event(dev.get("mac",""), ip, "disconnected")
        self._set_status(f"📴 جهاز غادر: {ip}", COLORS["accent_orange"])

    def _on_monitor_update(self, devs):
        self.devices = devs
        self._render_devices()
        now = datetime.now().strftime("%H:%M:%S")
        self.time_label.configure(text=now)
        self.device_count.configure(text=f"{len(devs)} " + ar("جهاز"))

    def open_color_picker(self):
        ColorPickerDialog(self, on_apply=self._apply_custom_colors)

    def _apply_custom_colors(self, bg_hex, card_hex, target):
        """تطبيق الألوان على الثيم المحدد (dark أو light)"""
        import config
        palette = config.COLORS_DARK if target == "dark" else config.COLORS_LIGHT
        palette["bg_dark"]       = bg_hex
        palette["bg_main"]       = bg_hex
        palette["bg_sidebar"]    = card_hex
        palette["bg_card"]       = card_hex
        palette["bg_card_hover"] = self._darken(card_hex, 15)
        palette["bg_input"]      = self._darken(card_hex, 25)

        # إذا كان الثيم الحالي هو المستهدف — طبّق فوراً على الواجهة
        if target == config.CURRENT_THEME:
            config.COLORS.update(palette)
            self.configure(fg_color=bg_hex)
            self.main_frame.configure(fg_color=card_hex)
            self.devices_list.configure(fg_color=bg_hex)
            self.statusbar.configure(fg_color=config.COLORS["bg_input"])
            self.progress.configure(fg_color=config.COLORS["bg_input"])
            self.sidebar.refresh_theme()
            if self.devices:
                self._render_devices()
            else:
                self._show_welcome()
        log.info(f"تم تطبيق ألوان مخصصة على {target}: bg={bg_hex} card={card_hex}")
        # حفظ الألوان المخصصة
        import config
        settings.set(f"colors_{target}", {
            "bg_dark": config.COLORS_DARK["bg_dark"] if target == "dark" else config.COLORS_LIGHT["bg_dark"],
            "bg_main": config.COLORS_DARK["bg_main"] if target == "dark" else config.COLORS_LIGHT["bg_main"],
            "bg_sidebar": config.COLORS_DARK["bg_sidebar"] if target == "dark" else config.COLORS_LIGHT["bg_sidebar"],
            "bg_card": config.COLORS_DARK["bg_card"] if target == "dark" else config.COLORS_LIGHT["bg_card"],
            "bg_card_hover": config.COLORS_DARK["bg_card_hover"] if target == "dark" else config.COLORS_LIGHT["bg_card_hover"],
            "bg_input": config.COLORS_DARK["bg_input"] if target == "dark" else config.COLORS_LIGHT["bg_input"],
        })

    @staticmethod
    def _darken(hex_color, amount):
        """تغميق لون hex بمقدار معين"""
        hex_color = hex_color.lstrip("#")
        r, g, b = int(hex_color[0:2],16), int(hex_color[2:4],16), int(hex_color[4:6],16)
        r, g, b = max(0,r-amount), max(0,g-amount), max(0,b-amount)
        return f"#{r:02x}{g:02x}{b:02x}"

    # ====== تبديل الثيم ======
    def do_toggle_theme(self):
        new_mode = toggle_theme()
        from config import COLORS
        # ── خلفيات ──────────────────────────────────────
        self.configure(fg_color=COLORS["bg_dark"])
        self.main_frame.configure(fg_color=COLORS["bg_sidebar"])
        self.devices_list.configure(fg_color=COLORS["bg_dark"])
        self.statusbar.configure(fg_color=COLORS["bg_input"])
        self.progress.configure(fg_color=COLORS["bg_input"], progress_color=COLORS["accent_gold"])
        # ── نصوص ────────────────────────────────────────
        self.main_title.configure(text_color=COLORS["text_primary"])
        self.device_count.configure(text_color=COLORS["text_muted"])
        self.network_label.configure(text_color=COLORS["text_secondary"])
        self.status_label.configure(text_color=COLORS["accent_green"])
        self.statusbar_text.configure(text_color=COLORS["text_muted"])
        self.time_label.configure(text_color=COLORS["text_muted"])
        # ── السايد بار (يشمل اسم التطبيق والأزرار) ──────
        self.sidebar.refresh_theme()
        self.sidebar.set_theme(new_mode)
        # ── إعادة رسم المحتوى ───────────────────────────
        if self.devices:
            self._render_devices()
        else:
            self._show_welcome()
        log.info(f"تم تغيير الثيم إلى: {new_mode}")
        settings.set("theme", new_mode)

    # ====== التصدير ======
    def do_export_csv(self):
        if not self.devices:
            AlertDialog(self, "Export", ar("لا توجد بيانات للتصدير. قم بالفحص أولاً."), "warning")
            return
        path = export_csv(self.devices)
        if path:
            self._set_status(f"تم التصدير: {path}", COLORS["accent_green"])
            AlertDialog(self, "Export", f"{ar('تم تصدير CSV بنجاح')}\n{path}", "success")
        else:
            AlertDialog(self, "Error", ar("فشل التصدير"), "error")

    def do_export_json(self):
        if not self.devices:
            AlertDialog(self, "Export", ar("لا توجد بيانات للتصدير. قم بالفحص أولاً."), "warning")
            return
        path = export_json(self.devices, self.port_results if self.port_results else None)
        if path:
            self._set_status(f"تم التصدير: {path}", COLORS["accent_green"])
            AlertDialog(self, "Export", f"{ar('تم تصدير JSON بنجاح')}\n{path}", "success")
        else:
            AlertDialog(self, "Error", ar("فشل التصدير"), "error")

    def do_export_pdf(self):
        if not self.devices:
            AlertDialog(self, "Export", ar("لا توجد بيانات للتصدير. قم بالفحص أولاً."), "warning")
            return
        path = export_pdf(self.devices, self.port_results if self.port_results else None)
        if path:
            self._set_status(f"تم التصدير: {path}", COLORS["accent_green"])
            AlertDialog(self, "Export", f"{ar('تم تصدير PDF بنجاح')}\n{path}", "success")
        else:
            AlertDialog(self, "Error", ar("فشل التصدير - تأكد من تثبيت fpdf2"), "error")

    def _hide_window(self):
        """إخفاء النافذة عبر withdraw (يعمل على كل بيئات Linux)"""
        self._is_hidden = True
        self.withdraw()

    def show_window(self):
        """toggle: إظهار إذا مخفية، إخفاء إذا ظاهرة"""
        if self._is_hidden or self.state() in ("iconic", "withdrawn"):
            self._is_hidden = False
            self.deiconify()
            self.lift()
            self.focus_force()
        else:
            self._hide_window()

    def _on_unmap(self, event):
        if event.widget is self:
            self._is_hidden = True

    def _on_map(self, event):
        if event.widget is self:
            self._is_hidden = False

    # ====== الإغلاق ======
    def _on_close(self):
        log.info("جاري إغلاق التطبيق...")
        self.scanner.stop()
        self.monitor.stop()
        self.port_scanner.cleanup()
        self.disconnector.cleanup()
        self.game_mode.cleanup()
        self.destroy()
