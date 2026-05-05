#!/bin/bash
# Network Sniper Pro - Launcher
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# التحقق من المكتبات المطلوبة وتثبيتها إذا ناقصة
python3 -c "import customtkinter, scapy, fpdf, speedtest, arabic_reshaper, bidi, PIL, manuf" 2>/dev/null || {
    echo "⚠️  بعض المكتبات غير مثبتة. جاري التثبيت..."
    pip install -r "$DIR/requirements.txt"
}

exec sudo python3 "$DIR/main.py"
