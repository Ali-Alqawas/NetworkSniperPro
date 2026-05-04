"""
بطاقة الجهاز المحسّنة - تعرض معلومات الجهاز مع أزرار التحكم
"""
import customtkinter as ctk
from utils.arabic import ar
from config import COLORS, DEVICE_TYPE_ICONS, DEFAULT_DEVICE_ICON


class DeviceCard(ctk.CTkFrame):
    """بطاقة جهاز واحد في قائمة الأجهزة"""

    def __init__(self, master, device_info, on_disconnect=None, on_reconnect=None,
                 on_port_scan=None, on_copy_mac=None, is_disconnected=False, **kwargs):
        super().__init__(master, fg_color=COLORS["bg_card"], corner_radius=12,
                        border_width=1, border_color=COLORS["bg_card_hover"], **kwargs)

        self.device_info = device_info
        self.on_disconnect = on_disconnect
        self.on_reconnect = on_reconnect
        self.on_port_scan = on_port_scan
        self.on_copy_mac = on_copy_mac
        self._is_disconnected = is_disconnected

        self._build_ui()

        # Hover effect
        self.bind("<Enter>", lambda e: self.configure(fg_color=COLORS["bg_card_hover"]))
        self.bind("<Leave>", lambda e: self.configure(fg_color=COLORS["bg_card"]))

    def _get_device_icon(self):
        """اختيار أيقونة حسب نوع الجهاز"""
        vendor = self.device_info.get("vendor", "").lower()
        if self.device_info.get("is_router"):
            return "📡"
        if self.device_info.get("is_local"):
            return "🖥️"
        for key, icon in DEVICE_TYPE_ICONS.items():
            if key in vendor:
                return icon
        return DEFAULT_DEVICE_ICON

    def _build_ui(self):
        ip = self.device_info.get("ip", "")
        mac = self.device_info.get("mac", "")
        hostname = self.device_info.get("hostname", "غير معروف")
        vendor = self.device_info.get("vendor", "غير معروف")
        icon = self._get_device_icon()
        is_local = self.device_info.get("is_local", False)
        is_router = self.device_info.get("is_router", False)

        # الجزء الأيسر - معلومات الجهاز
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=15, pady=12)

        # السطر الأول: أيقونة + IP + حالة
        row1 = ctk.CTkFrame(info_frame, fg_color="transparent")
        row1.pack(fill="x", anchor="w")

        icon_label = ctk.CTkLabel(row1, text=f"{icon}", font=ctk.CTkFont(size=22))
        icon_label.pack(side="left", padx=(0, 8))

        ip_label = ctk.CTkLabel(
            row1, text=ip, font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        ip_label.pack(side="left", padx=(0, 10))

        # شارة الحالة
        if self._is_disconnected:
            status_text = ar("مقطوع 🔴")
            status_color = COLORS["accent_red"]
        elif is_local:
            status_text = ar("جهازك 🟢")
            status_color = COLORS["accent_green"]
        elif is_router:
            status_text = ar("الراوتر 📡")
            status_color = COLORS["accent_cyan"]
        else:
            status_text = ar("متصل 🟢")
            status_color = COLORS["accent_green"]

        status_badge = ctk.CTkLabel(
            row1, text=status_text, font=ctk.CTkFont(size=11),
            text_color=status_color,
            fg_color=COLORS["bg_input"], corner_radius=8,
            padx=8, pady=2
        )
        status_badge.pack(side="left")

        # السطر الثاني: MAC + Vendor + Hostname
        row2 = ctk.CTkFrame(info_frame, fg_color="transparent")
        row2.pack(fill="x", anchor="w", pady=(5, 0))

        details = f"MAC: {mac}  •  {vendor}"
        if hostname and hostname != "غير معروف":
            details += f"  •  {hostname}"

        detail_label = ctk.CTkLabel(
            row2, text=details, font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"], anchor="w"
        )
        detail_label.pack(side="left")

        # الجزء الأيمن - أزرار التحكم
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(side="right", padx=15, pady=12)

        # لا تعرض أزرار التحكم لجهازك أو الراوتر
        if is_local or is_router:
            tag = ar("محمي 🛡️") if is_local else ar("البوابة 🌐")
            lbl = ctk.CTkLabel(btn_frame, text=tag, text_color=COLORS["text_muted"],
                              font=ctk.CTkFont(size=11))
            lbl.pack(pady=5)
            return

        # زر فحص المنافذ
        if self.on_port_scan:
            btn_ports = ctk.CTkButton(
                btn_frame, text=ar("🔍 فحص المنافذ"), width=120, height=30,
                font=ctk.CTkFont(size=12),
                fg_color=COLORS["accent_blue"], hover_color=COLORS["hover_blue"],
                command=lambda: self.on_port_scan(self.device_info)
            )
            btn_ports.pack(pady=(0, 5))

        # زر قطع / إعادة الاتصال
        if self._is_disconnected and self.on_reconnect:
            btn_conn = ctk.CTkButton(
                btn_frame, text=ar("✅ إعادة الاتصال"), width=120, height=30,
                font=ctk.CTkFont(size=12),
                fg_color=COLORS["accent_green"], hover_color=COLORS["hover_green"],
                command=lambda: self.on_reconnect(self.device_info)
            )
            btn_conn.pack(pady=(0, 5))
        elif self.on_disconnect:
            btn_disc = ctk.CTkButton(
                btn_frame, text=ar("✂️ قطع الاتصال"), width=120, height=30,
                font=ctk.CTkFont(size=12),
                fg_color=COLORS["accent_red"], hover_color=COLORS["hover_red"],
                command=lambda: self.on_disconnect(self.device_info)
            )
            btn_disc.pack(pady=(0, 5))

        # زر نسخ MAC
        if self.on_copy_mac and mac and "N/A" not in mac:
            btn_copy = ctk.CTkButton(
                btn_frame, text=ar("📋 نسخ MAC"), width=120, height=28,
                font=ctk.CTkFont(size=11),
                fg_color=COLORS["bg_input"], hover_color=COLORS["bg_card_hover"],
                text_color=COLORS["text_secondary"],
                command=lambda: self.on_copy_mac(mac)
            )
            btn_copy.pack()

    def set_disconnected(self, disconnected):
        """تحديث حالة الجهاز"""
        self._is_disconnected = disconnected
        # إعادة بناء الواجهة
        for widget in self.winfo_children():
            widget.destroy()
        self._build_ui()
