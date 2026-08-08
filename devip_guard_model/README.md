# 🛡️ DEVIP Guard

<div dir="rtl" align="center">

**کتابخانه حرفه‌ای تشخیص محتوای نامناسب**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blueviolet)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-brightgreen)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-teal)](https://fastapi.tiangolo.com/)
[![Release](https://img.shields.io/github/v/release/AbolfazlZarei-dev/devip-guard?color=orange)](https://github.com/AbolfazlZarei-dev/devip-guard/releases)
[![Downloads](https://img.shields.io/github/downloads/AbolfazlZarei-dev/devip-guard/total?color=blue)](https://github.com/AbolfazlZarei-dev/devip-guard/releases)

</div>

---

## ✨ ویژگی‌ها

| ویژگی | توضیحات |
|-------|---------|
| ⚡ **سرعت بالا** | تشخیص در کمتر از نیم ثانیه |
| 🎯 **دقت ۹۵٪** | آموزش دیده روی میلیون‌ها تصویر |
| 🖼️ **فرمت‌های مختلف** | تصویر، گیف و ویدیو |
| 🔒 **حریم خصوصی** | پردازش کاملاً محلی |
| 🌐 **API عمومی** | بدون نیاز به احراز هویت |
| 🕊️ **تشخیص حجاب** | تشخیص خودکار حجاب اسلامی |
| 💰 **رایگان** | کاملاً رایگان برای همه |

---

## 📥 دانلود مدل‌ها

> ⚠️ **توجه**: فایل‌های مدل به دلیل حجم بالا در [GitHub Releases](https://github.com/AbolfazlZarei-dev/devip-guard/releases) قرار گرفته‌اند.

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

**با wget (لینوکس/مک):**
```bash
wget https://github.com/AbolfazlZarei-dev/devip-guard/releases/download/v1.0.0/devip_guard_model.onnx -O devip_guard_model/devip_guard_model.onnx
wget https://github.com/AbolfazlZarei-dev/devip-guard/releases/download/v1.0.0/devip_guard_m2model.onnx -O devip_guard_model/devip_guard_m2model.onnx
wget https://github.com/AbolfazlZarei-dev/devip-guard/releases/download/v1.0.0/devip_guard_i3model.onnx -O devip_guard_model/devip_guard_i3model.onnx
```

**با curl (ویندوز/لینوکس/مک):**
```bash
curl -L https://github.com/AbolfazlZarei-dev/devip-guard/releases/download/v1.0.0/devip_guard_model.onnx -o devip_guard_model/devip_guard_model.onnx
curl -L https://github.com/AbolfazlZarei-dev/devip-guard/releases/download/v1.0.0/devip_guard_m2model.onnx -o devip_guard_model/devip_guard_m2model.onnx
curl -L https://github.com/AbolfazlZarei-dev/devip-guard/releases/download/v1.0.0/devip_guard_i3model.onnx -o devip_guard_model/devip_guard_i3model.onnx
```

**یا دانلود دستی:**  
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

```bash
# اجرای سرور
python run.py

# یا با uvicorn
uvicorn devip_guard.api.app:create_app --host 0.0.0.0 --port 8000
```

پس از اجرا، به آدرس زیر بروید:
```
http://localhost:8000
```

### اندپوینت‌های API

| متد | مسیر | توضیحات |
|-----|------|---------|
| `POST` | `/api/v1/classify-img` | تشخیص تصویر |
| `POST` | `/api/v1/classify-gif` | تشخیص گیف |
| `POST` | `/api/v1/classify-video` | تشخیص ویدیو |
| `POST` | `/api/v1/classify-url` | تشخیص از لینک |
| `GET` | `/api/v1/health` | بررسی سلامت |

---

## 📁 ساختار پروژه

```
devip-guard/
│
├── devip_guard/                 # کد اصلی
│   ├── api/                     # API و اندپوینت‌ها
│   │   ├── app.py              # برنامه FastAPI
│   │   ├── routes.py           # مسیرهای API
│   │   └── models.py           # مدل‌های داده
│   │
│   ├── core/                    # هسته تشخیص
│   │   ├── detector.py         # موتور اصلی
│   │   ├── config.py           # تنظیمات
│   │   └── models.py           # مدیریت مدل
│   │
│   ├── processors/              # پردازشگرها
│   │   ├── image.py            # پردازش تصویر
│   │   ├── gif.py              # پردازش گیف
│   │   └── video.py            # پردازش ویدیو
│   │
│   └── cli/                     # ابزار خط فرمان
│       └── main.py
│
├── devip_guard_model/           # 📁 مدل‌ها (اینجا قرار دهید)
│   ├── devip_guard_model.onnx
│   ├── devip_guard_m2model.onnx
│   └── devip_guard_i3model.onnx
│
├── static/                      # فایل‌های استاتیک
├── templates/                   # قالب‌های HTML
├── run.py                       # اجرای سرور
├── requirements.txt             # وابستگی‌ها
└── README.md                    # این فایل
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
```

---

## 📄 مجوز

این پروژه تحت مجوز **MIT** منتشر شده است.  
برای اطلاعات بیشتر به فایل [LICENSE](LICENSE) مراجعه کنید.

---

## 👨‍💻 توسعه‌دهنده

**ابوالفضل زارعی**

| پلتفرم | لینک |
|---------|------|
| 🐙 **گیت‌هاب** | [@AbolfazlZarei-dev](https://github.com/AbolfazlZarei-dev) |
| 📱 **تلگرام** | [@Abolfazl_PGR](https://t.me/Abolfazl_PGR) |
| 🌐 **وب‌سایت** | [abolfazlzarei.sbs](https://abolfazlzarei.sbs) |
| 📧 **ایمیل** | [ninjacode.ir@gmail.com](mailto:ninjacode.ir@gmail.com) |

---

<div align="center">

**⭐ اگر این پروژه برای شما مفید بود، به آن ستاره دهید!**  

**ساخته شده با ❤️ توسط ابوالفضل زارعی**

</div>
