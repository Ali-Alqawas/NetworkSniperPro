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
COLORS = {
    "bg_dark": "#0d1117",
    "bg_sidebar": "#161b22",
    "bg_card": "#1c2333",
    "bg_card_hover": "#252d3d",
    "bg_main": "#0d1117",
    "bg_input": "#21262d",
    "text_primary": "#e6edf3",
    "text_secondary": "#8b949e",
    "text_muted": "#484f58",
    "accent_blue": "#58a6ff",
    "accent_green": "#3fb950",
    "accent_red": "#f85149",
    "accent_orange": "#d29922",
    "accent_purple": "#bc8cff",
    "accent_cyan": "#39d2c0",
    "status_online": "#3fb950",
    "status_offline": "#f85149",
    "status_disconnected": "#f85149",
    "status_warning": "#d29922",
    "hover_blue": "#4090e0",
    "hover_green": "#2ea043",
    "hover_red": "#da3633",
    "hover_orange": "#bb8009",
}

# ================= إعدادات Nmap =================
NMAP_TIMEOUT = "15s"
NMAP_SCAN_ARGS = ["-sn", "-PE", "-PA", "-PP"]
NMAP_PORT_SCAN_ARGS = ["-sV", "--top-ports", "100"]

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
