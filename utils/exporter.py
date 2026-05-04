"""
أداة تصدير النتائج إلى CSV و PDF مع دعم كامل للعربية
"""
import csv
import os
from datetime import datetime
from utils.logger import log

try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False
    log.warning("fpdf2 غير مثبت - التصدير إلى PDF لن يعمل")

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_ARABIC = True
except ImportError:
    HAS_ARABIC = False

# مسار خط عربي متاح على النظام
_ARABIC_FONT_PATHS = [
    "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoKufiArabic-Regular.ttf",
]

def _get_arabic_font():
    for p in _ARABIC_FONT_PATHS:
        if os.path.exists(p):
            return p
    return None

def _ar(text: str) -> str:
    """تحويل النص العربي للعرض الصحيح في PDF"""
    if not HAS_ARABIC or not text:
        return text
    try:
        return get_display(arabic_reshaper.reshape(str(text)))
    except Exception:
        return text


def export_csv(devices, filepath=None):
    if not filepath:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.expanduser(f"~/NetworkSniperPro_Report_{timestamp}.csv")
    try:
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(["IP Address", "MAC Address", "Hostname", "Vendor", "Status"])
            for dev in devices:
                writer.writerow([
                    dev.get("ip", ""), dev.get("mac", ""),
                    dev.get("hostname", ""), dev.get("vendor", ""),
                    dev.get("status", "Online")
                ])
        log.info(f"تم تصدير CSV: {filepath}")
        return filepath
    except Exception as e:
        log.error(f"فشل تصدير CSV: {e}")
        return None


def export_pdf(devices, port_results=None, filepath=None):
    if not HAS_FPDF:
        log.error("fpdf2 غير مثبت")
        return None
    if not filepath:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.expanduser(f"~/NetworkSniperPro_Report_{timestamp}.pdf")
    try:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # تسجيل الخط العربي إذا متاح
        arabic_font = _get_arabic_font()
        if arabic_font:
            pdf.add_font("Arabic", "", arabic_font)
            pdf.add_font("Arabic", "B", arabic_font)

        def cell_ar(w, h, txt, **kwargs):
            """خلية تدعم العربية تلقائياً"""
            txt = str(txt)
            has_arabic_chars = any('\u0600' <= c <= '\u06ff' for c in txt)
            if has_arabic_chars and arabic_font:
                pdf.set_font("Arabic", size=kwargs.pop("size", 9))
                txt = _ar(txt)
            pdf.cell(w, h, txt, **kwargs)

        # ── العنوان ──────────────────────────────────────
        pdf.set_font("Helvetica", "B", 22)
        pdf.cell(0, 14, "Network Sniper Pro", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 7, f"Scan Report  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                 new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(6)

        # ── ملخص ─────────────────────────────────────────
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, f"Devices Found: {len(devices)}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        # ── جدول الأجهزة ─────────────────────────────────
        col_w = [32, 44, 52, 42, 20]
        headers = ["IP", "MAC", "Hostname", "Vendor", "Status"]
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(40, 40, 60)
        pdf.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            pdf.cell(col_w[i], 8, h, border=1, fill=True, align="C")
        pdf.ln()

        pdf.set_text_color(0, 0, 0)
        for dev in devices:
            hostname = dev.get("hostname", "")
            vendor   = dev.get("vendor", "")
            # الخلايا العادية
            pdf.set_font("Helvetica", "", 8)
            pdf.cell(col_w[0], 7, dev.get("ip", ""), border=1, align="C")
            pdf.cell(col_w[1], 7, dev.get("mac", "")[:17], border=1, align="C")
            # hostname — عربي أو لاتيني
            has_ar_host = any('\u0600' <= c <= '\u06ff' for c in hostname)
            if has_ar_host and arabic_font:
                pdf.set_font("Arabic", size=8)
                pdf.cell(col_w[2], 7, _ar(hostname[:22]), border=1, align="R")
                pdf.set_font("Helvetica", "", 8)
            else:
                pdf.cell(col_w[2], 7, hostname[:22], border=1, align="C")
            # vendor
            has_ar_vendor = any('\u0600' <= c <= '\u06ff' for c in vendor)
            if has_ar_vendor and arabic_font:
                pdf.set_font("Arabic", size=8)
                pdf.cell(col_w[3], 7, _ar(vendor[:20]), border=1, align="R")
                pdf.set_font("Helvetica", "", 8)
            else:
                pdf.cell(col_w[3], 7, vendor[:20], border=1, align="C")
            pdf.cell(col_w[4], 7, dev.get("status", "Up"), border=1, align="C")
            pdf.ln()

        # ── نتائج فحص المنافذ ────────────────────────────
        if port_results:
            pdf.ln(8)
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 9, "Port Scan Results", new_x="LMARGIN", new_y="NEXT")
            for ip, ports in port_results.items():
                pdf.ln(3)
                pdf.set_font("Helvetica", "B", 11)
                pdf.cell(0, 7, f"Host: {ip}", new_x="LMARGIN", new_y="NEXT")
                pw = [22, 38, 28, 62]
                pdf.set_font("Helvetica", "B", 8)
                pdf.set_fill_color(40, 40, 60)
                pdf.set_text_color(255, 255, 255)
                for h, w in zip(["Port", "Service", "State", "Risk"], pw):
                    pdf.cell(w, 7, h, border=1, fill=True, align="C")
                pdf.ln()
                pdf.set_text_color(0, 0, 0)
                for pi in ports:
                    risk = pi.get("risk", "")
                    pdf.set_font("Helvetica", "", 8)
                    pdf.cell(pw[0], 6, str(pi.get("port", "")), border=1, align="C")
                    pdf.cell(pw[1], 6, pi.get("service", ""), border=1, align="C")
                    pdf.cell(pw[2], 6, pi.get("state", ""), border=1, align="C")
                    has_ar_risk = any('\u0600' <= c <= '\u06ff' for c in risk)
                    if has_ar_risk and arabic_font:
                        pdf.set_font("Arabic", size=8)
                        pdf.cell(pw[3], 6, _ar(risk[:35]), border=1, align="R")
                    else:
                        pdf.cell(pw[3], 6, risk[:35], border=1, align="C")
                    pdf.ln()
                pdf.ln(3)

        # ── Footer ───────────────────────────────────────
        pdf.ln(6)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 7, "Generated by Network Sniper Pro v2.0", align="C")

        pdf.output(filepath)
        log.info(f"تم تصدير PDF: {filepath}")
        return filepath
    except Exception as e:
        log.error(f"فشل تصدير PDF: {e}")
        return None
