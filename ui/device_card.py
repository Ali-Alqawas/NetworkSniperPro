"""
بطاقة الجهاز — تصميم نظيف بحواف ناعمة
"""
import customtkinter as ctk
from utils.arabic import ar
from utils.device_names import set_name, delete_name
from config import COLORS, DEVICE_TYPE_ICONS, DEFAULT_DEVICE_ICON


class DeviceCard(ctk.CTkFrame):
    def __init__(self, master, device_info, on_disconnect=None, on_reconnect=None,
                 on_port_scan=None, on_copy_mac=None, is_disconnected=False,
                 on_rename=None, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["bg_input"],
            **kwargs
        )
        self.device_info   = device_info
        self.on_disconnect = on_disconnect
        self.on_reconnect  = on_reconnect
        self.on_port_scan  = on_port_scan
        self.on_copy_mac   = on_copy_mac
        self.on_rename     = on_rename
        self._is_disconnected = is_disconnected
        self._build_ui()
        self.bind("<Enter>", lambda e: self.configure(fg_color=COLORS["bg_card_hover"]))
        self.bind("<Leave>", lambda e: self.configure(fg_color=COLORS["bg_card"]))

    def _get_icon(self):
        vendor = self.device_info.get("vendor", "").lower()
        if self.device_info.get("is_router"):  return "📡"
        if self.device_info.get("is_local"):   return "🖥️"
        for key, icon in DEVICE_TYPE_ICONS.items():
            if key in vendor:
                return icon
        return DEFAULT_DEVICE_ICON

    def _build_ui(self):
        ip        = self.device_info.get("ip", "")
        mac       = self.device_info.get("mac", "")
        hostname  = self.device_info.get("hostname", "غير معروف")
        vendor    = self.device_info.get("vendor", "غير معروف")
        is_local  = self.device_info.get("is_local", False)
        is_router = self.device_info.get("is_router", False)
        name_src  = self.device_info.get("name_source", "unknown")

        # ── معلومات الجهاز (يسار) ───────────────────────
        info = ctk.CTkFrame(self, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True, padx=16, pady=12)

        row1 = ctk.CTkFrame(info, fg_color="transparent")
        row1.pack(fill="x", anchor="w")

        ctk.CTkLabel(row1, text=self._get_icon(),
                     font=ctk.CTkFont(size=20)).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(row1, text=ip,
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=COLORS["text_primary"]).pack(side="left", padx=(0, 10))

        # شارة الحالة
        if self._is_disconnected:
            badge_text, badge_color = ar("مقطوع"), COLORS["accent_red"]
        elif is_local:
            badge_text, badge_color = ar("جهازك ●"), COLORS["accent_green"]
        elif is_router:
            badge_text, badge_color = ar("الراوتر ◈"), COLORS["accent_gold"]
        else:
            badge_text, badge_color = ar("متصل ●"), COLORS["accent_green"]

        ctk.CTkLabel(row1, text=badge_text,
                     font=ctk.CTkFont(size=10),
                     text_color=badge_color,
                     fg_color=COLORS["bg_input"],
                     corner_radius=6, padx=8, pady=2).pack(side="left")

        # اسم الجهاز — السطر الثاني بارز
        row_name = ctk.CTkFrame(info, fg_color="transparent")
        row_name.pack(fill="x", anchor="w", pady=(4, 0))

        if hostname and hostname != "غير معروف":
            name_color = COLORS["accent_cyan"] if name_src == "saved" else COLORS["text_primary"]
            name_icon  = "✏️ " if name_src == "saved" else ""
            ctk.CTkLabel(row_name, text=f"{name_icon}{hostname}",
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=name_color, anchor="w").pack(side="left")
        else:
            ctk.CTkLabel(row_name, text=ar("اسم غير معروف"),
                         font=ctk.CTkFont(size=12),
                         text_color=COLORS["text_muted"], anchor="w").pack(side="left")

        # السطر الثالث: MAC + Vendor
        row2 = ctk.CTkFrame(info, fg_color="transparent")
        row2.pack(fill="x", anchor="w", pady=(2, 0))

        ctk.CTkLabel(row2, text=f"MAC: {mac}  •  {vendor}",
                     font=ctk.CTkFont(size=11),
                     text_color=COLORS["text_secondary"],
                     anchor="w").pack(side="left")

        # ── أزرار التحكم (يمين) ─────────────────────────
        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(side="right", padx=14, pady=12)

        if is_local or is_router:
            tag = ar("محمي 🛡️") if is_local else ar("البوابة 🌐")
            ctk.CTkLabel(btns, text=tag,
                         text_color=COLORS["text_muted"],
                         font=ctk.CTkFont(size=11)).pack(pady=5)
            return

        if self.on_port_scan:
            ctk.CTkButton(
                btns, text=ar("🔍 فحص المنافذ"), width=118, height=28,
                font=ctk.CTkFont(size=11),
                fg_color=COLORS["accent_blue"], hover_color=COLORS["hover_blue"],
                corner_radius=8,
                command=lambda: self.on_port_scan(self.device_info)
            ).pack(pady=(0, 4))

        if self._is_disconnected and self.on_reconnect:
            ctk.CTkButton(
                btns, text=ar("✅ إعادة الاتصال"), width=118, height=28,
                font=ctk.CTkFont(size=11),
                fg_color=COLORS["accent_green"], hover_color=COLORS["hover_green"],
                corner_radius=8,
                command=lambda: self.on_reconnect(self.device_info)
            ).pack(pady=(0, 4))
        elif self.on_disconnect:
            ctk.CTkButton(
                btns, text=ar("✂️ قطع الاتصال"), width=118, height=28,
                font=ctk.CTkFont(size=11),
                fg_color=COLORS["accent_red"], hover_color=COLORS["hover_red"],
                corner_radius=8,
                command=lambda: self.on_disconnect(self.device_info)
            ).pack(pady=(0, 4))

        if self.on_copy_mac and mac and "N/A" not in mac:
            ctk.CTkButton(
                btns, text=ar("📋 نسخ MAC"), width=118, height=26,
                font=ctk.CTkFont(size=10),
                fg_color=COLORS["bg_input"], hover_color=COLORS["bg_card_hover"],
                text_color=COLORS["text_secondary"], corner_radius=8,
                command=lambda: self.on_copy_mac(mac)
            ).pack(pady=(0, 4))

        # زر تسمية الجهاز — يظهر دائماً للأجهزة الأخرى
        if mac and "N/A" not in mac:
            ctk.CTkButton(
                btns, text=ar("✏️ تسمية"), width=118, height=26,
                font=ctk.CTkFont(size=10),
                fg_color=COLORS["bg_input"], hover_color=COLORS["bg_card_hover"],
                text_color=COLORS["accent_cyan"], corner_radius=8,
                command=self._open_rename_dialog
            ).pack()

    def _open_rename_dialog(self):
        mac      = self.device_info.get("mac", "")
        current  = self.device_info.get("hostname", "")
        ip       = self.device_info.get("ip", "")

        dialog = ctk.CTkToplevel(self)
        dialog.title("تسمية الجهاز")
        dialog.geometry("380x220")
        dialog.configure(fg_color=COLORS["bg_dark"])
        dialog.resizable(False, False)

        ctk.CTkLabel(dialog, text=ar("✏️ تسمية الجهاز"),
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=COLORS["text_primary"]).pack(pady=(18, 4))
        ctk.CTkLabel(dialog, text=f"IP: {ip}  •  MAC: {mac}",
                     font=ctk.CTkFont(size=11),
                     text_color=COLORS["text_muted"]).pack(pady=(0, 10))

        entry = ctk.CTkEntry(dialog, width=280, height=36,
                             placeholder_text=ar("اكتب اسماً للجهاز..."),
                             font=ctk.CTkFont(size=13),
                             fg_color=COLORS["bg_input"],
                             text_color=COLORS["text_primary"])
        entry.pack(pady=(0, 4))
        if current and current != "غير معروف":
            entry.insert(0, current)

        def _save():
            name = entry.get().strip()
            if name:
                set_name(mac, name)
                self.device_info["hostname"]    = name
                self.device_info["name_source"] = "saved"
            else:
                delete_name(mac)
                self.device_info["hostname"]    = "غير معروف"
                self.device_info["name_source"] = "unknown"
            if self.on_rename:
                self.on_rename()
            dialog.destroy()

        btn_f = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_f.pack(pady=10)
        ctk.CTkButton(btn_f, text=ar("إلغاء"), width=110,
                      fg_color=COLORS["bg_input"], hover_color=COLORS["bg_card_hover"],
                      command=dialog.destroy).pack(side="left", padx=8)
        ctk.CTkButton(btn_f, text=ar("💾 حفظ"), width=110,
                      fg_color=COLORS["accent_cyan"], hover_color=COLORS["accent_blue"],
                      command=_save).pack(side="left", padx=8)

        entry.bind("<Return>", lambda e: _save())
        dialog.after(100, lambda: dialog.grab_set())
