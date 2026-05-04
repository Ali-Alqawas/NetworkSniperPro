<div align="center">

# 🔫 Network Sniper Pro

**أداة احترافية لمراقبة وإدارة الشبكات المحلية**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Platform](https://img.shields.io/badge/Platform-Linux-orange?logo=linux)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-2.0-purple)

*by [Ali-Alqawas](https://github.com/Ali-Alqawas)*

</div>

---

## 📌 نبذة عن البرنامج

**Network Sniper Pro** أداة سطح مكتب مبنية بـ Python تمنحك رؤية كاملة وتحكماً تاماً في الأجهزة المتصلة بشبكتك المحلية. تجمع بين فحص الشبكة السريع، ومراقبة الأجهزة الحية، وإدارة الاتصالات، وتحسين أداء الألعاب — كل ذلك في واجهة رسومية أنيقة بالكامل باللغة العربية.

---

## ✨ المميزات الرئيسية

| الميزة | الوصف |
|--------|-------|
| 📡 **رادار الشبكة** | فحص متوازٍ بـ 50 thread يكتشف جميع الأجهزة خلال ثوانٍ |
| 👁️ **المراقبة الحية** | تنبيه فوري عند اتصال أو انقطاع أي جهاز |
| ✂️ **قطع الاتصال** | ARP Spoofing لقطع أي جهاز مع تحديد المدة (5 دقائق / ساعة / دائم) |
| 🎮 **وضع الألعاب** | إعطاء أولوية كاملة لجهازك وتحديد باقي الأجهزة بـ 512kbit |
| 🔍 **فحص المنافذ** | كشف المنافذ المفتوحة مع تصنيف مستوى الخطر |
| ⚡ **اختبار السرعة** | قياس سرعة التحميل والرفع والـ Ping |
| 📊 **التصدير** | تصدير التقارير بصيغة CSV أو PDF |

---

## 🖥️ متطلبات التشغيل

- **نظام التشغيل:** Linux (Ubuntu / Debian / Kali)
- **Python:** 3.10 أو أحدث
- **أدوات النظام:** `nmap`, `iproute2`, `tc` (traffic control)
- **صلاحيات:** يُنصح بالتشغيل كـ `root` لكامل الوظائف

---

## 🚀 التثبيت والتشغيل

```bash
# 1. تثبيت nmap
sudo apt install nmap

# 2. تثبيت المكتبات
pip install -r requirements.txt

# 3. التشغيل (بصلاحيات root للوظائف الكاملة)
sudo python3 main.py
```

أو استخدم سكريبت التشغيل المرفق:

```bash
chmod +x launch.sh
./launch.sh
```

---

## 📦 المكتبات المستخدمة

```
customtkinter   — واجهة رسومية حديثة
scapy           — ARP Spoofing وتحليل الحزم
arabic-reshaper — دعم النصوص العربية
python-bidi     — اتجاه النص العربي
speedtest-cli   — اختبار سرعة الإنترنت
fpdf2           — توليد تقارير PDF
Pillow          — معالجة الصور
```

---

## 🗂️ هيكل المشروع

```
NetworkSniperPro/
├── main.py              # نقطة الدخول
├── config.py            # الإعدادات المركزية
├── requirements.txt
├── launch.sh
├── core/
│   ├── scanner.py       # محرك فحص الشبكة
│   ├── disconnector.py  # قطع الاتصال (ARP Spoofing)
│   ├── monitor.py       # المراقبة الحية
│   ├── port_scanner.py  # فحص المنافذ
│   ├── game_mode.py     # وضع الألعاب (tc/HTB)
│   └── speed_test.py    # اختبار السرعة
├── ui/
│   ├── app.py           # النافذة الرئيسية
│   ├── sidebar.py       # الشريط الجانبي
│   ├── device_card.py   # بطاقة الجهاز
│   ├── dialogs.py       # نوافذ الحوار
│   └── themes.py        # الثيم والألوان
├── utils/
│   ├── network.py       # أدوات الشبكة
│   ├── exporter.py      # التصدير CSV/PDF
│   ├── logger.py        # نظام التسجيل
│   └── arabic.py        # معالجة النصوص العربية
└── assets/
    └── icons/
```

---

## ⚠️ تنبيه قانوني

هذه الأداة مخصصة **للاستخدام على شبكتك الخاصة فقط**. استخدامها على شبكات الغير دون إذن مخالف للقانون. المطور غير مسؤول عن أي استخدام غير مشروع.

---

## 👤 المطور

**Ali-Alqawas** — مهندس شبكات وأمن معلومات

---

<div align="center">
صُنع بـ ❤️ للمجتمع العربي التقني
</div>
