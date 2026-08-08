# 🛡️ دیویپ گارد | DEVIP Guard

<div dir="rtl" align="center">

**کتابخانه حرفه‌ای تشخیص محتوای نامناسب**

<a href="https://www.python.org/">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blueviolet?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
</a>
<a href="LICENSE">
  <img src="https://img.shields.io/badge/License-MIT-brightgreen?style=for-the-badge&logo=opensourceinitiative&logoColor=white" alt="License" />
</a>
<a href="https://fastapi.tiangolo.com/">
  <img src="https://img.shields.io/badge/FastAPI-0.100%2B-teal?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
</a>
<a href="https://github.com/AbolfazlZarei-dev/devip-guard/releases">
  <img src="https://img.shields.io/github/v/release/AbolfazlZarei-dev/devip-guard?color=orange&style=for-the-badge&logo=github&logoColor=white" alt="Release" />
</a>
<a href="https://github.com/AbolfazlZarei-dev/devip-guard/releases">
  <img src="https://img.shields.io/github/downloads/AbolfazlZarei-dev/devip-guard/total?color=blue&style=for-the-badge&logo=github&logoColor=white" alt="Downloads" />
</a>

</div>

---

## 🎯 درباره پروژه

<div dir="rtl">

**DEVIP Guard** یک کتابخانه قدرتمند و سبک برای تشخیص محتوای نامناسب در تصاویر، گیف‌ها و ویدیوها است. این ابزار با استفاده از مدل‌های پیشرفته یادگیری عمیق و موتور اجرایی ONNX، با دقت بالای ۹۵٪ محتوای نامناسب را شناسایی می‌کند.

</div>

---

## ✨ ویژگی‌های برجسته

| ویژگی | توضیحات |
|:-----:|---------|
| ⚡ **سرعت بالا** | تشخیص در کمتر از نیم ثانیه |
| 🎯 **دقت ۹۵٪** | آموزش دیده روی میلیون‌ها تصویر |
| 🖼️ **فرمت‌های مختلف** | تصویر، گیف و ویدیو |
| 🔒 **حریم خصوصی** | پردازش کاملاً محلی |
| 🌐 **API عمومی** | بدون نیاز به احراز هویت |
| 🕊️ **تشخیص حجاب** | تشخیص خودکار حجاب اسلامی |
| 💰 **رایگان** | کاملاً رایگان برای همه |
| 🎨 **رابط وب** | رابط کاربری زیبا و مدرن |
| 🖥️ **خط فرمان** | ابزار کامل خط فرمان |

---

## 📥 دانلود مدل‌ها

> ⚠️ **نکته مهم**: فایل‌های مدل به دلیل حجم بالا در **[GitHub Releases](https://github.com/AbolfazlZarei-dev/devip-guard/releases)** قرار گرفته‌اند.

### 📋 لیست مدل‌ها

| ردیف | نام مدل | توضیحات | حجم | لینک دانلود |
|:----:|---------|---------|:---:|:-----------:|
| ۱ | `devip_guard_model.onnx` | مدل پیش‌فرض MobileNet V2 | ۱۴ مگابایت | [📥 دانلود](https://github.com/AbolfazlZarei-dev/devip-guard/releases/download/v1.0.0/devip_guard_model.onnx) |
| ۲ | `devip_guard_m2model.onnx` | مدل بهینه‌شده MobileNet V2 | ۱۴ مگابایت | [📥 دانلود](https://github.com/AbolfazlZarei-dev/devip-guard/releases/download/v1.0.0/devip_guard_m2model.onnx) |
| ۳ | `devip_guard_i3model.onnx` | مدل Inception V3 (دقت بالا) | ۹۲ مگابایت | [📥 دانلود](https://github.com/AbolfazlZarei-dev/devip-guard/releases/download/v1.0.0/devip_guard_i3model.onnx) |

---

## 🚀 نصب و راه‌اندازی

### ۱. کلون کردن مخزن

```bash
git clone https://github.com/AbolfazlZarei-dev/devip-guard.git
cd devip-guard
```

### ۲. دانلود مدل‌ها

**روش اول - دانلود با PowerShell (ویندوز):**
```powershell
# ایجاد پوشه مدل
New-Item -ItemType Directory -Force -Path "devip_guard_model"

# دانلود مدل پیش‌فرض
Invoke-WebRequest -Uri "https://github.com/AbolfazlZarei-dev/devip-guard/releases/download/v1.0.0/devip_guard_model.onnx" -OutFile "devip_guard_model/devip_guard_model.onnx"

# دانلود مدل بهینه‌شده
Invoke-WebRequest -Uri "https://github.com/AbolfazlZarei-dev/devip-guard/releases/download/v1.0.0/devip_guard_m2model.onnx" -OutFile "devip_guard_model/devip_guard_m2model.onnx"

# دانلود مدل Inception V3
Invoke-WebRequest -Uri "https://github.com/AbolfazlZarei-dev/devip-guard/releases/download/v1.0.0/devip_guard_i3model.onnx" -OutFile "devip_guard_model/devip_guard_i3model.onnx"
```

**روش دوم - دانلود با curl:**
```bash
# ایجاد پوشه مدل
mkdir -p devip_guard_model

# دانلود مدل‌ها
curl -L https://github.com/AbolfazlZarei-dev/devip-guard/releases/download/v1.0.0/devip_guard_model.onnx -o devip_guard_model/devip_guard_model.onnx
curl -L https://github.com/AbolfazlZarei-dev/devip-guard/releases/download/v1.0.0/devip_guard_m2model.onnx -o devip_guard_model/devip_guard_m2model.onnx
curl -L https://github.com/AbolfazlZarei-dev/devip-guard/releases/download/v1.0.0/devip_guard_i3model.onnx -o devip_guard_model/devip_guard_i3model.onnx
```

**روش سوم - دانلود با wget:**
```bash
# ایجاد پوشه مدل
mkdir -p devip_guard_model

# دانلود مدل‌ها
wget https://github.com/AbolfazlZarei-dev/devip-guard/releases/download/v1.0.0/devip_guard_model.onnx -O devip_guard_model/devip_guard_model.onnx
wget https://github.com/AbolfazlZarei-dev/devip-guard/releases/download/v1.0.0/devip_guard_m2model.onnx -O devip_guard_model/devip_guard_m2model.onnx
wget https://github.com/AbolfazlZarei-dev/devip-guard/releases/download/v1.0.0/devip_guard_i3model.onnx -O devip_guard_model/devip_guard_i3model.onnx
```

**روش چهارم - دانلود دستی:**  
به صفحه [Releases](https://github.com/AbolfazlZarei-dev/devip-guard/releases) بروید و فایل‌ها را دانلود کنید.

### ۳. نصب پکیج

```bash
pip install -e .
```

---

## 💻 شروع سریع

```python
from devip_guard import DevipGuardDetector

# راه‌اندازی تشخیص‌دهنده
detector = DevipGuardDetector()

# تشخیص تصویر با قابلیت تشخیص حجاب
result = detector.classify_with_veil("image.jpg")

# نمایش نتیجه
print(f"آیا محتوا نامناسب است؟ {result['is_nsfw']}")
print(f"امتیاز NSFW: {result['adjusted_nsfw_score']:.2%}")
print(f"دسته غالب: {result['dominant_category']}")
```

### خروجی نمونه:

```
🟢 محتوای ایمن
امتیاز NSFW: ۱۴٪
دسته غالب: neutral
پیش‌بینی‌ها: {'neutral': 0.85, 'sexy': 0.08, 'porn': 0.04, ...}
```

---

## 🌐 راه‌اندازی سرور API

### اجرای سرور

```bash
# روش اول - با run.py
python run.py

# روش دوم - با uvicorn
uvicorn devip_guard.api.app:create_app --host 0.0.0.0 --port 8000 --reload
```

### دسترسی به رابط کاربری

پس از اجرا، به آدرس زیر بروید:
```
http://localhost:8000
```

### اندپوینت‌های API

| متد | مسیر | توضیحات |
|:---:|------|---------|
| `POST` | `/api/v1/classify-img` | تشخیص تصویر |
| `POST` | `/api/v1/classify-gif` | تشخیص گیف |
| `POST` | `/api/v1/classify-video` | تشخیص ویدیو |
| `POST` | `/api/v1/classify-url` | تشخیص از لینک |
| `GET` | `/api/v1/health` | بررسی سلامت |

### تست با curl

```bash
# تشخیص تصویر
curl -X POST http://localhost:8000/api/v1/classify-img -F "image=@image.jpg"

# تشخیص از لینک
curl -X POST http://localhost:8000/api/v1/classify-url -H "Content-Type: application/json" -d '{"url": "https://example.com/image.jpg"}'

# بررسی سلامت
curl http://localhost:8000/api/v1/health
```

---

## 🖥️ ابزار خط فرمان

```bash
# تشخیص تصویر
python -m devip_guard.cli.main -i image.jpg

# تشخیص با خروجی JSON
python -m devip_guard.cli.main -i image.jpg --format json

# تشخیص ویدیو
python -m devip_guard.cli.main -i video.mp4 -s 0.05 -f 200

# ذخیره خروجی
python -m devip_guard.cli.main -i image.jpg -o result.json
```

---

## 📁 ساختار پروژه

```
devip-guard/
│
├── devip_guard/                 # 📦 کد اصلی
│   ├── api/                     # 🌐 API و اندپوینت‌ها
│   │   ├── app.py              # برنامه FastAPI
│   │   ├── routes.py           # مسیرهای API
│   │   └── models.py           # مدل‌های داده
│   │
│   ├── core/                    # ⚙️ هسته تشخیص
│   │   ├── detector.py         # موتور اصلی
│   │   ├── config.py           # تنظیمات
│   │   └── models.py           # مدیریت مدل
│   │
│   ├── processors/              # 🖼️ پردازشگرها
│   │   ├── image.py            # پردازش تصویر
│   │   ├── gif.py              # پردازش گیف
│   │   └── video.py            # پردازش ویدیو
│   │
│   └── cli/                     # 💻 ابزار خط فرمان
│       └── main.py
│
├── devip_guard_model/           # 📁 مدل‌ها (اینجا قرار دهید)
│   ├── devip_guard_model.onnx
│   ├── devip_guard_m2model.onnx
│   └── devip_guard_i3model.onnx
│
├── static/                      # 🎨 فایل‌های استاتیک
├── templates/                   # 📄 قالب‌های HTML
├── run.py                       # 🚀 اجرای سرور
├── requirements.txt             # 📋 وابستگی‌ها
└── README.md                    # 📖 این فایل
```

---

## 🔧 وابستگی‌ها

```txt
Python >= 3.8
FastAPI >= 0.100.0
ONNX Runtime >= 1.12.0
OpenCV >= 4.5.0
Pillow >= 9.0.0
NumPy >= 1.21.0
Uvicorn >= 0.20.0
```

---

## 📊 دسته‌بندی‌ها

| دسته | توضیحات | رنگ |
|------|---------|:----:|
| 🟢 **neutral** | محتوای ایمن و معمولی | سبز |
| 🟡 **sexy** | محتوای تحریک‌کننده | زرد |
| 🔴 **porn** | محتوای صریح بزرگسالان | قرمز |
| 🟣 **hentai** | محتوای صریح انیمه | بنفش |
| 🔵 **drawing** | نقاشی‌ها و تصاویر هنری | آبی |

---

## 📄 مجوز

این پروژه تحت مجوز **MIT** منتشر شده است.  
برای اطلاعات بیشتر به فایل [LICENSE](LICENSE) مراجعه کنید.

---

## 👨‍💻 توسعه‌دهنده

<div dir="rtl" align="center">

**ابوالفضل زارعی**

</div>

| پلتفرم | لینک |
|---------|------|
| 🐙 **گیت‌هاب** | [@AbolfazlZarei-dev](https://github.com/AbolfazlZarei-dev) |
| 📱 **تلگرام** | [@Abolfazl_PGR](https://t.me/Abolfazl_PGR) |
| 🌐 **وب‌سایت** | [abolfazlzarei.sbs](https://abolfazlzarei.sbs) |
| 📧 **ایمیل** | [ninjacode.ir@gmail.com](mailto:ninjacode.ir@gmail.com) |

---

## ⭐ حمایت

اگر این پروژه برای شما مفید بود:

- ⭐ به پروژه **ستاره** دهید
- 📢 آن را با دیگران **به اشتراک** بگذارید
- 🐛 **مشکلات** را گزارش دهید
- 🔧 در توسعه **مشارکت** کنید

---

<div align="center">

**ساخته شده با ❤️ توسط ابوالفضل زارعی**

[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?logo=github)](https://github.com/AbolfazlZarei-dev)
[![Telegram](https://img.shields.io/badge/Telegram-Follow-2CA5E0?logo=telegram)](https://t.me/Abolfazl_PGR)
[![Website](https://img.shields.io/badge/Website-Visit-4285F4)](https://abolfazlzarei.sbs)

</div>
