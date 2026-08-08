# دیویپ گارد (DEVIP Guard)

<div align="center">

**کتابخانه حرفه‌ای تشخیص محتوای نامناسب**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688)](https://fastapi.tiangolo.com/)
[![ONNX](https://img.shields.io/badge/ONNX-1.12%2B-005B9F)](https://onnx.ai/)
[![Downloads](https://img.shields.io/pypi/dm/devip-guard)](https://pypi.org/project/devip-guard/)
[![Version](https://img.shields.io/pypi/v/devip-guard)](https://pypi.org/project/devip-guard/)

</div>

---

## 📖 معرفی | Introduction

**دیویپ گارد** یک کتابخانه قدرتمند و سبک برای تشخیص محتوای نامناسب (NSFW) در تصاویر، گیف‌ها و ویدیوها است. این کتابخانه با استفاده از مدل‌های یادگیری عمیق و موتور اجرایی ONNX، قادر است با دقت بالایی محتوای نامناسب را شناسایی کند.

**DEVIP Guard** is a powerful and lightweight library for detecting NSFW (Not Safe For Work) content in images, GIFs, and videos. Using deep learning models and the ONNX runtime engine, it can identify inappropriate content with high accuracy.

---

## ✨ ویژگی‌ها | Features

| فارسی | English |
|-------|---------|
| ⚡ **سرعت فوق‌العاده** - تشخیص در کمتر از نیم ثانیه | ⚡ **Lightning Fast** - Detection in under 0.5 seconds |
| 🎯 **دقت بالا** - دقت بالای ۹۵٪ روی میلیون‌ها تصویر | 🎯 **High Accuracy** - 95%+ accuracy on millions of images |
| 🖼️ **پشتیبانی از فرمت‌های مختلف** - تصاویر، گیف و ویدیو | 🖼️ **Multi-format** - Images, GIFs, and Videos |
| 🔒 **حریم خصوصی** - تمام پردازش‌ها به صورت محلی انجام می‌شود | 🔒 **Privacy First** - All processing is local |
| 🌐 **API REST** - API کامل با مستندات | 🌐 **REST API** - Complete API with documentation |
| 💻 **ابزار خط فرمان** - رابط کاربری خط فرمان | 💻 **CLI Tool** - Command-line interface |
| 🧠 **تشخیص هوشمند** - ۵ دسته‌بندی با احتمالات | 🧠 **Smart Detection** - 5 categories with probabilities |
| 🎨 **رابط کاربری زیبا** - رابط وب مدرن | 🎨 **Beautiful UI** - Modern web interface |
| 💰 **کاملاً رایگان** - بدون اشتراک یا هزینه پنهان | 💰 **100% Free** - No subscriptions or hidden fees |
| 🕊️ **تشخیص حجاب** - تشخیص خودکار حجاب برای محتوای اسلامی | 🕊️ **Veil Detection** - Automatic hijab detection for Islamic content |

---

## 📦 نصب | Installation

### با pip | Via pip
```bash
pip install devip-guard
```

### با پشتیبانی از GPU | With GPU Support
```bash
pip install devip-guard[gpu]
```

### از روی کد منبع | From Source
```bash
git clone https://github.com/AbolfazlZarei-dev/devip-guard.git
cd devip-guard
pip install -e .
```

---

## 🚀 شروع سریع | Quick Start

### کتابخانه پایتون | Python Library
```python
from devip_guard import DevipGuardDetector, Config

# راه‌اندازی تشخیص‌دهنده | Initialize detector
detector = DevipGuardDetector()

# تشخیص تصویر با تشخیص حجاب | Classify image with veil detection
result = detector.classify_with_veil("image.jpg")
print(f"آیا محتوای نامناسب است؟: {result['is_nsfw']}")
print(f"امتیاز NSFW: {result['adjusted_nsfw_score']:.3f}")
print(f"پیش‌بینی‌ها: {result['predictions']}")

# تشخیص ساده | Simple prediction
predictions = detector.predict_image("photo.png")
print(predictions)
```

### سرور API | REST API Server
```bash
# اجرای سرور | Start the server
python -m devip_guard.api.app

# یا با یوویکورن | Or using uvicorn
uvicorn devip_guard.api.app:create_app --host 0.0.0.0 --port 8000
```

### استفاده از خط فرمان | CLI Usage
```bash
# تشخیص تصویر | Classify image
devip-guard --input image.jpg --format pretty

# تشخیص ویدیو | Classify video
devip-guard --input video.mp4 --sample-rate 0.05 --max-frames 200

# خروجی JSON | JSON output
devip-guard --input image.jpg --format json --output result.json
```

---

## 🌐 API عمومی | Public API

**همه اندپوینت‌ها عمومی هستند - نیازی به احراز هویت نیست!**

**All endpoints are public - No authentication required!**

| متد | اندپوینت | توضیحات |
|-----|----------|---------|
| `POST` | `/api/v1/classify-img` | آپلود تصویر (JPG, PNG, WEBP, BMP) |
| `POST` | `/api/v1/classify-gif` | آپلود گیف |
| `POST` | `/api/v1/classify-video` | آپلود ویدیو (MP4, AVI, MOV, MKV) |
| `POST` | `/api/v1/classify-url` | تحلیل از طریق لینک |
| `GET` | `/api/v1/health` | بررسی سلامت سرویس |
| `POST` | `/api/v1/cleanup` | پاکسازی حافظه کش |

### مثال: تشخیص تصویر | Example: Classify Image
```bash
curl -X POST http://localhost:8000/api/v1/classify-img \
  -F "image=@photo.jpg"
```

### مثال: تشخیص از طریق لینک | Example: Classify from URL
```bash
curl -X POST http://localhost:8000/api/v1/classify-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/image.jpg"}'
```

---

## 📊 ساختار پاسخ | Response Format

```json
{
  "DEVIP_Guard": {
    "model": "DEVIP Guard-1",
    "ok": true,
    "channel": "devip.ir",
    "writer": " @NinjaCode ",
    "result": {
      "filename": "image.jpg",
      "type": "image",
      "predictions": {
        "neutral": 0.8500,
        "sexy": 0.0800,
        "porn": 0.0400,
        "hentai": 0.0200,
        "drawing": 0.0100
      },
      "dominant_category": "neutral",
      "raw_nsfw_score": 0.1400,
      "adjusted_nsfw_score": 0.1400,
      "is_nsfw": false,
      "is_safe": true,
      "is_suspicious": false,
      "veil": {
        "has_veil": false,
        "confidence": 0.0,
        "method": "none"
      },
      "thresholds": {
        "nsfw": 0.85,
        "safe": 0.25,
        "suspicious": 0.60
      }
    }
  }
}
```

---

## 🧠 دسته‌بندی‌ها | Detection Categories

| فارسی | English | رنگ | Color |
|-------|---------|-----|-------|
| 🟢 **خنثی** | **Neutral** | محتوای سالم و عادی | Safe and normal content |
| 🟡 **سکسی** | **Sexy** | محتوای تحریک‌آمیز | Sexually suggestive content |
| 🔴 **پورن** | **Porn** | محتوای صریح بزرگسالان | Explicit pornographic content |
| 🟣 **هنتای** | **Hentai** | محتوای صریح انیمه | Anime explicit content |
| 🔵 **نقاشی** | **Drawing** | نقاشی‌ها و تصاویر هنری | Artistic drawings |

---

## 🕊️ تشخیص حجاب | Veil Detection

دیویپ گارد قابلیت تشخیص خودکار حجاب در تصاویر را دارد:

**DEVIP Guard includes automatic veil (hijab) detection:**

- 🔍 **تشخیص خودکار** - شناسایی خودکار محتوای دارای حجاب
- 📊 **کاهش خطا** - کاهش تا ۳۰٪ خطاهای مثبت کاذب
- 🎯 **امتیاز اطمینان** - ارائه سطح اطمینان تشخیص حجاب
- 🎨 **روش‌های چندگانه** - استفاده از تحلیل رنگ برای تشخیص دقیق

```python
result = detector.classify_with_veil("image.jpg")
print(f"حجاب تشخیص داده شد: {result['veil']['has_veil']}")
print(f"سطح اطمینان: {result['veil']['confidence']}")
```

---

## 🎨 رابط کاربری وب | Web UI

کتابخانه شامل یک رابط کاربری وب زیبا و مدرن است:

**The library includes a beautiful and modern web interface:**

- ✨ **طراحی مدرن** - رابط کاربری تمیز و واکنش‌گرا
- 📤 **کشیدن و رها کردن** - آپلود آسان فایل
- ⚡ **نتایج لحظه‌ای** - بازخورد فوری
- 📱 **سازگار با موبایل** - کار بر روی تمام دستگاه‌ها
- 🌓 **حالت تاریک/روشن** - تشخیص خودکار تم

**آدرس دسترسی:** `http://localhost:8000`

---

## 💻 ابزار خط فرمان | Command Line Interface

### استفاده پایه | Basic Usage
```bash
devip-guard -i image.jpg
```

### گزینه‌های پیشرفته | Advanced Options
```bash
devip-guard --input video.mp4 --sample-rate 0.05 --max-frames 200 --format json --output result.json
```

### گزینه‌ها | Options

| گزینه | توضیحات |
|-------|---------|
| `-i, --input` | مسیر فایل ورودی (اجباری) |
| `-t, --type` | نوع مدل: d, m2, i3 |
| `-d, --device` | دستگاه: cpu, cuda, tensorrt |
| `-s, --sample-rate` | نرخ نمونه‌برداری ویدیو (۰ تا ۱) |
| `-f, --max-frames` | حداکثر فریم ویدیو |
| `--format` | فرمت خروجی: json, pretty, simple |
| `-o, --output` | ذخیره خروجی در فایل |
| `-v, --verbose` | خروجی مفصل |

---

## 📁 ساختار پروژه | Project Structure

```
devip_guard/
├── api/                    # API REST
│   ├── app.py             # برنامه FastAPI
│   ├── routes.py          # اندپوینت‌های API
│   └── models.py          # مدل‌های Pydantic
├── core/                   # هسته اصلی
│   ├── detector.py        # موتور تشخیص اصلی
│   ├── config.py          # تنظیمات
│   └── models.py          # مدیریت مدل
├── processors/            # پردازشگرهای رسانه
│   ├── image.py          # پردازش تصویر
│   ├── gif.py            # پردازش گیف
│   └── video.py          # پردازش ویدیو
├── cli/                   # رابط خط فرمان
│   └── main.py           # نقطه ورود CLI
├── static/                # فایل‌های استاتیک
├── templates/             # قالب‌های HTML
└── __init__.py           # معرفی پکیج
```

---

## ⚙️ تنظیمات | Configuration

### متغیرهای محیطی | Environment Variables

```bash
# تنظیمات مدل | Model Settings
DEVIP_GUARD_MODEL_TYPE=d          # d, m2, i3
DEVIP_GUARD_DEVICE=cpu            # cpu, cuda, tensorrt, dml

# تنظیمات سرور | Server Settings
DEVIP_GUARD_HOST=0.0.0.0
DEVIP_GUARD_PORT=8000
DEVIP_GUARD_DEBUG=false

# آستانه‌ها | Thresholds
DEVIP_GUARD_NSFW_THRESHOLD=0.85
DEVIP_GUARD_SAFE_THRESHOLD=0.25
DEVIP_GUARD_SUSPICIOUS_THRESHOLD=0.60

# کارایی | Performance
DEVIP_GUARD_INTRA_THREADS=2
DEVIP_GUARD_INTER_THREADS=1
DEVIP_GUARD_CLEANUP_INTERVAL=100

# محدودیت فایل | File Limits
DEVIP_GUARD_MAX_FILE_SIZE=20     # مگابایت (تصویر)
DEVIP_GUARD_MAX_VIDEO_SIZE=100   # مگابایت (ویدیو)
```

---

## 🔧 پیش‌نیازها | Requirements

- Python 3.8+
- ONNX Runtime
- OpenCV
- PIL/Pillow
- NumPy
- FastAPI (اختیاری)
- Uvicorn (اختیاری)

---

## 📈 عملکرد | Performance

| فرمت | زمان متوسط | حداکثر حجم |
|------|------------|------------|
| تصویر (CPU) | ۰.۳-۰.۵ ثانیه | ۲۰ مگابایت |
| تصویر (GPU) | ۰.۱-۰.۲ ثانیه | ۲۰ مگابایت |
| گیف (۱۰۰ فریم) | ۲-۳ ثانیه | ۲۰ مگابایت |
| ویدیو (۱۰۰ فریم) | ۳-۵ ثانیه | ۱۰۰ مگابایت |
| ویدیو (GPU) | ۱-۲ ثانیه | ۱۰۰ مگابایت |

---

## 🤝 مشارکت | Contributing

از مشارکت شما استقبال می‌شود! لطفاً مراحل زیر را دنبال کنید:

**Contributions are welcome! Please follow these steps:**

1. فورک کردن مخزن | Fork the repository
2. ایجاد شاخه ویژگی | Create a feature branch
3. اعمال تغییرات | Make your changes
4. اجرای تست‌ها | Run tests
5. ارسال درخواست Pull | Submit a pull request

```bash
# راه‌اندازی محیط توسعه | Development setup
pip install -e ".[dev]"

# اجرای تست‌ها | Run tests
pytest tests/

# فرمت کد | Format code
black devip_guard/
isort devip_guard/

# بررسی نوع | Type checking
mypy devip_guard/
```

---

## 📄 مجوز | License

این پروژه تحت مجوز MIT منتشر شده است - برای جزئیات بیشتر فایل [LICENSE](LICENSE) را ببینید.

**This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.**

---

## 👨‍💻 توسعه‌دهنده | Developer

**ابوالفضل زارعی | Abolfazl Zarei**

[![GitHub](https://img.shields.io/badge/GitHub-AbolfazlZarei--dev-181717?style=for-the-badge&logo=github)](https://github.com/AbolfazlZarei-dev)
[![Website](https://img.shields.io/badge/وب‌سایت-abolfazlzarei.sbs-4285F4?style=for-the-badge&logo=google-chrome)](https://abolfazlzarei.sbs)
[![Telegram](https://img.shields.io/badge/تلگرام-@Abolfazl_PGR-2CA5E0?style=for-the-badge&logo=telegram)](https://t.me/Abolfazl_PGR)
[![Rubika](https://img.shields.io/badge/روبیکا-@NinjaCode-FF6B6B?style=for-the-badge)](https://rubika.ir/NinjaCode)
[![کانال](https://img.shields.io/badge/کانال-@Ninja_Code-2CA5E0?style=for-the-badge&logo=telegram)](https://t.me/Ninja_Code)
[![ایمیل](https://img.shields.io/badge/ایمیل-ninjacode.ir%40gmail.com-EA4335?style=for-the-badge&logo=gmail)](mailto:ninjacode.ir@gmail.com)

---

## 📱 شبکه‌های اجتماعی | Social Media

### تلگرام | Telegram
- **آیدی شخصی:** [@Abolfazl_PGR](https://t.me/Abolfazl_PGR)
- **کانال:** [@Ninja_Code](https://t.me/Ninja_Code)

### روبیکا | Rubika
- **آیدی شخصی:** [@NinjaCode](https://rubika.ir/NinjaCode)
- **کانال:** [@Ninja_Code](https://rubika.ir/Ninja_Code)

### گیت‌هاب | GitHub
- **پروفایل:** [AbolfazlZarei-dev](https://github.com/AbolfazlZarei-dev)
- **مخزن:** [devip-guard](https://github.com/AbolfazlZarei-dev/devip-guard)

### وب‌سایت | Website
- **سایت شخصی:** [abolfazlzarei.sbs](https://abolfazlzarei.sbs)
- **ایمیل:** [info@abolfazlzarei.sbs](mailto:info@abolfazlzarei.sbs)

### ایمیل | Email
- **پشتیبانی:** [ninjacode.ir@gmail.com](mailto:ninjacode.ir@gmail.com)

---

## ⭐ حمایت | Support

اگر این پروژه برای شما مفید است، لطفاً در نظر بگیرید:

**If you find this project useful, please consider:**

- ⭐ ستاره دادن به مخزن در گیت‌هاب | Starring the repository on GitHub
- 📢 به اشتراک گذاشتن با دیگران | Sharing with others
- 🐛 گزارش مشکلات | Reporting issues
- 🔧 مشارکت در کد | Contributing to the code
- 💬 پیوستن به جامعه ما | Joining our community

---

## 📝 تاریخچه تغییرات | Changelog

### نسخه ۱.۰.۰ (۲۰۲۴) | v1.0.0 (2024)
- 🎉 انتشار اولیه | Initial release
- 🖼️ تشخیص تصویر | Image classification
- 🎞️ پشتیبانی از گیف | GIF support
- 🎬 پشتیبانی از ویدیو | Video support
- 🌐 API REST | REST API
- 🎨 رابط کاربری وب | Web UI
- 💻 ابزار خط فرمان | CLI tool
- 🕊️ تشخیص حجاب | Veil detection
- 🔌 پشتیبانی از چند مدل | Multi-model support
- ⚡ شتاب‌دهی GPU | GPU acceleration
- 🔓 API عمومی (بدون احراز هویت) | Public API (No authentication)

---

## 🙏 قدردانی | Acknowledgments

- [ONNX Runtime](https://onnxruntime.ai/) - موتور اجرایی | Inference engine
- [FastAPI](https://fastapi.tiangolo.com/) - چارچوب وب | Web framework
- [OpenCV](https://opencv.org/) - پردازش ویدیو | Video processing
- [Pillow](https://python-pillow.org/) - پردازش تصویر | Image processing

---

## 🌟 تاریخچه ستاره‌ها | Star History

[![Star History Chart](https://api.star-history.com/svg?repos=AbolfazlZarei-dev/devip-guard&type=Date)](https://star-history.com/#AbolfazlZarei-dev/devip-guard&Date)

---

<div align="center">

**ساخته شده با ❤️ توسط [ابوالفضل زارعی](https://abolfazlzarei.sbs)**

**Made with ❤️ by [Abolfazl Zarei](https://abolfazlzarei.sbs)**

[![GitHub](https://img.shields.io/badge/GitHub-دنبال_کنید-181717?logo=github)](https://github.com/AbolfazlZarei-dev)
[![Telegram](https://img.shields.io/badge/تلگرام-دنبال_کنید-2CA5E0?logo=telegram)](https://t.me/Abolfazl_PGR)
[![Rubika](https://img.shields.io/badge/روبیکا-دنبال_کنید-FF6B6B)](https://rubika.ir/NinjaCode)
[![Website](https://img.shields.io/badge/وب‌سایت-مشاهده-4285F4)](https://abolfazlzarei.sbs)

*ساخته شده با اشتیاق برای جامعه متن‌باز* | *Built with passion for the open-source community*

</div>