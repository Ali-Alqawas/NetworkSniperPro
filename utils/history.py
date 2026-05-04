"""
قاعدة بيانات SQLite لتاريخ الأجهزة وسجل الاتصالات
"""
import sqlite3
import os
from datetime import datetime
from utils.logger import log

_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "history.db"
)


def _conn():
    c = sqlite3.connect(_DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init():
    """إنشاء الجداول إذا لم تكن موجودة"""
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                mac         TEXT PRIMARY KEY,
                ip          TEXT,
                hostname    TEXT,
                vendor      TEXT,
                first_seen  TEXT,
                last_seen   TEXT,
                seen_count  INTEGER DEFAULT 1
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                mac       TEXT,
                ip        TEXT,
                event     TEXT,   -- 'connected' | 'disconnected'
                timestamp TEXT
            )
        """)
        c.execute("CREATE INDEX IF NOT EXISTS idx_events_mac ON events(mac)")


def upsert_device(device: dict):
    """تحديث أو إضافة جهاز عند كل فحص"""
    mac = device.get("mac", "")
    if not mac or "N/A" in mac:
        return
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with _conn() as c:
        existing = c.execute("SELECT * FROM devices WHERE mac=?", (mac,)).fetchone()
        if existing:
            c.execute("""
                UPDATE devices SET ip=?, hostname=?, vendor=?, last_seen=?, seen_count=seen_count+1
                WHERE mac=?
            """, (device.get("ip",""), device.get("hostname",""),
                  device.get("vendor",""), now, mac))
        else:
            c.execute("""
                INSERT INTO devices (mac, ip, hostname, vendor, first_seen, last_seen)
                VALUES (?,?,?,?,?,?)
            """, (mac, device.get("ip",""), device.get("hostname",""),
                  device.get("vendor",""), now, now))


def log_event(mac: str, ip: str, event: str):
    """تسجيل حدث اتصال أو انقطاع"""
    if not mac or "N/A" in mac:
        return
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with _conn() as c:
        c.execute("INSERT INTO events (mac,ip,event,timestamp) VALUES (?,?,?,?)",
                  (mac, ip, event, now))


def get_all_devices() -> list:
    """إرجاع كل الأجهزة المعروفة مرتبة بآخر ظهور"""
    with _conn() as c:
        rows = c.execute(
            "SELECT * FROM devices ORDER BY last_seen DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def get_device_events(mac: str, limit: int = 50) -> list:
    """إرجاع آخر أحداث جهاز محدد"""
    with _conn() as c:
        rows = c.execute(
            "SELECT * FROM events WHERE mac=? ORDER BY timestamp DESC LIMIT ?",
            (mac, limit)
        ).fetchall()
        return [dict(r) for r in rows]


def get_recent_events(limit: int = 100) -> list:
    """آخر الأحداث لكل الأجهزة"""
    with _conn() as c:
        rows = c.execute(
            "SELECT * FROM events ORDER BY timestamp DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


# تهيئة عند الاستيراد
try:
    init()
except Exception as e:
    log.error(f"فشل تهيئة قاعدة البيانات: {e}")
