"""
NetworkSniperPro - ملف الإعدادات المركزي
"""

# ================= معلومات التطبيق =================
APP_NAME = "Network Sniper Pro"
APP_VERSION = "2.0"
APP_TITLE = f"{APP_NAME} v{APP_VERSION}"

# ================= أبعاد النافذة =================
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 750
SIDEBAR_WIDTH = 240

# ================= الألوان =================
COLORS_DARK = {
    # ── خلفيات ──────────────────────────────────────────
    "bg_dark":        "#1D1C1C",   # خلفية الشاشة الرئيسية (Shadow)
    "bg_sidebar":     "#262424",   # السايد بار والقوالب (Deep Charcoal)
    "bg_card":        "#262424",   # بطاقات الأجهزة
    "bg_card_hover":  "#2e2b2b",   # hover — أفتح بدرجة واحدة
    "bg_main":        "#1D1C1C",
    "bg_input":       "#2e2b2b",   # حقول الإدخال
    # ── نصوص ────────────────────────────────────────────
    "text_primary":   "#EEE5DA",   # نص رئيسي — دافئ غير أبيض
    "text_secondary": "#b8a99a",   # نص ثانوي
    "text_muted":     "#6e6460",   # نص خافت
    # ── Accent موحد (الذهبي المطفأ) ─────────────────────
    "accent_gold":    "#A88B68",   # اللون الرئيسي للأزرار والأيقونات
    "hover_gold":     "#917558",   # hover للذهبي
    # ── ألوان الحالة ─────────────────────────────────────
    "accent_green":   "#5a9e6f",
    "accent_red":     "#c0544a",
    "accent_orange":  "#c49a3c",
    "accent_blue":    "#5b8db8",
    "accent_purple":  "#9b7ec8",
    "accent_cyan":    "#4a9ead",
    "status_online":  "#5a9e6f",
    "status_offline": "#c0544a",
    "status_disconnected": "#c0544a",
    "status_warning": "#c49a3c",
    "hover_green":    "#4a8e5f",
    "hover_red":      "#a8443a",
    "hover_orange":   "#a8842c",
    "hover_blue":     "#4a7da8",
}

COLORS_LIGHT = {
    # ── خلفيات ──────────────────────────────────────────
    "bg_dark":        "#3E000C",   # خلفية الشاشة — أحمر داكن عميق
    "bg_sidebar":     "#FFECD1",   # السايد بار والقوالب — كريمي دافئ
    "bg_card":        "#FFECD1",   # بطاقات الأجهزة
    "bg_card_hover":  "#F5DFC0",   # hover أغمق قليلاً
    "bg_main":        "#3E000C",
    "bg_input":       "#EDD9B8",   # حقول الإدخال
    # ── نصوص ────────────────────────────────────────────
    "text_primary":   "#1A0005",   # نص رئيسي — داكن جداً على الكريمي
    "text_secondary": "#3D1A10",   # نص ثانوي
    "text_muted":     "#7A4A3A",   # نص خافت
    # ── Accent ───────────────────────────────────────────
    "accent_gold":    "#8B3A20",   # بني-أحمر داكن يتناسق مع الخلفية
    "hover_gold":     "#7A2A10",
    # ── ألوان الحالة ─────────────────────────────────────
    "accent_green":   "#2D6A3F",
    "accent_red":     "#8B2E26",
    "accent_orange":  "#8B5010",
    "accent_blue":    "#2D4E8A",
    "accent_purple":  "#5E3D8A",
    "accent_cyan":    "#2D5E7A",
    "status_online":  "#2D6A3F",
    "status_offline": "#8B2E26",
    "status_disconnected": "#8B2E26",
    "status_warning": "#8B5010",
    "hover_green":    "#1D5A2F",
    "hover_red":      "#7A1E16",
    "hover_orange":   "#7A4000",
    "hover_blue":     "#1D3E7A",
}

# الثيم الافتراضي
CURRENT_THEME = "dark"
COLORS = COLORS_DARK.copy()

# ================= إعدادات Nmap =================
NMAP_TIMEOUT = "15s"
NMAP_SCAN_ARGS = ["-sn", "-PE", "-PA", "-PP"]
NMAP_PORT_SCAN_ARGS = ["-sV", "--top-ports", "100"]
PORT_SCAN_LIST = "21,22,23,25,53,80,110,135,139,143,443,445,1433,3306,3389,5432,5900,6379,8080,8443,8888,27017"

# ================= الثيم =================
THEMES = ["dark", "light"]
DEFAULT_THEME = "dark"

# ================= منافذ الفحص =================
PORT_SCAN_LIST = "21,22,23,25,53,80,110,135,139,143,443,445,1433,3306,3389,5432,5900,6379,8080,8443,8888,27017"

# ================= الثيم =================
THEMES = ["dark", "light"]
DEFAULT_THEME = "dark"

# ================= إعدادات الفحص =================
SCAN_INTERVAL_SECONDS = 30
DEFAULT_NETWORK = "192.168.1.0/24"

# ================= إعدادات قطع الاتصال =================
DISCONNECT_DURATIONS = {
    "5 دقائق": 300,
    "15 دقيقة": 900,
    "ساعة": 3600,
    "دائم": -1,
}

# ================= إعدادات وضع الألعاب =================
GAME_MODE_BANDWIDTH_LIMIT = "512kbit"
GAME_MODE_AUTO_STOP_MINUTES = 120

# ================= تصنيف الأجهزة =================
DEVICE_TYPE_ICONS = {
    "apple": "📱", "samsung": "📱", "huawei": "📱", "xiaomi": "📱",
    "oppo": "📱", "realme": "📱", "oneplus": "📱", "vivo": "📱",
    "google": "📱", "sony": "📺", "lg": "📺",
    "intel": "💻", "dell": "💻", "hp": "💻", "lenovo": "💻",
    "asus": "💻", "acer": "💻", "microsoft": "💻",
    "tp-link": "📡", "d-link": "📡", "netgear": "📡",
    "cisco": "📡", "mikrotik": "📡",
    "hikvision": "📷", "dahua": "📷",
    "amazon": "🔊", "espressif": "🔌", "raspberry": "🖥️",
}
DEFAULT_DEVICE_ICON = "🖥️"

# ================= المنافذ الخطيرة =================
DANGEROUS_PORTS = {
    21: ("FTP", "خطير - نقل ملفات غير مشفر"),
    22: ("SSH", "آمن - اتصال مشفر"),
    23: ("Telnet", "خطير جداً - غير مشفر"),
    25: ("SMTP", "متوسط - بريد إلكتروني"),
    53: ("DNS", "طبيعي - خدمة أسماء"),
    80: ("HTTP", "طبيعي - ويب غير مشفر"),
    110: ("POP3", "متوسط - بريد"),
    135: ("RPC", "خطير - خدمات ويندوز"),
    139: ("NetBIOS", "خطير - مشاركة ملفات"),
    143: ("IMAP", "متوسط - بريد"),
    443: ("HTTPS", "آمن - ويب مشفر"),
    445: ("SMB", "خطير - مشاركة ملفات"),
    1433: ("MSSQL", "خطير - قاعدة بيانات"),
    3306: ("MySQL", "خطير - قاعدة بيانات"),
    3389: ("RDP", "خطير - سطح مكتب بعيد"),
    5432: ("PostgreSQL", "خطير - قاعدة بيانات"),
    5900: ("VNC", "خطير - سطح مكتب بعيد"),
    6379: ("Redis", "خطير - قاعدة بيانات"),
    8080: ("HTTP-Alt", "متوسط - ويب بديل"),
    8443: ("HTTPS-Alt", "آمن - ويب بديل مشفر"),
    27017: ("MongoDB", "خطير - قاعدة بيانات"),
}

# ================= إعدادات التسجيل =================
LOG_DIR = "logs"
LOG_MAX_SIZE = 5 * 1024 * 1024
LOG_BACKUP_COUNT = 3
