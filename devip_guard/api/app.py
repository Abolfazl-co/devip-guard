# -*- coding: utf-8 -*-
"""
DEVIP Guard - برنامه FastAPI (عمومی)
"""

import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from ..core.config import Config
from .routes import router


def create_app(config: Config = None) -> FastAPI:
    """
    ایجاد برنامه FastAPI با تمام مسیرها و میان‌افزارها
    
    Args:
        config: شیء تنظیمات، در صورت None از Config.from_env() استفاده می‌شود
    
    Returns:
        نمونه برنامه FastAPI
    """
    config = config or Config.from_env()
    
    # غیرفعال کردن مستندات خودکار
    app = FastAPI(
        title="DEVIP Guard",
        description="API حرفه‌ای تشخیص محتوای نامناسب - دسترسی عمومی",
        version="1.0.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None
    )
    
    # تنظیمات CORS - اجازه همه دامنه‌ها برای API عمومی
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    #  تنظیم مسیرهای استاتیک 
    # مسیر ریشه پروژه (محل قرارگیری پوشه‌های static و templates)
    base_dir = Path(__file__).parent.parent.parent
    
    # تعیین مسیرهای استاتیک و قالب‌ها
    static_dir = base_dir / "static"
    templates_dir = base_dir / "templates"
    
    # ایجاد پوشه‌ها در صورت عدم وجود
    static_dir.mkdir(parents=True, exist_ok=True)
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    # ایجاد پوشه تصاویر در صورت عدم وجود
    img_dir = static_dir / "img"
    img_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 مسیر فایل‌های استاتیک: {static_dir}")
    print(f"📁 مسیر قالب‌ها: {templates_dir}")
    print(f"📁 مسیر تصاویر: {img_dir}")
    
    # اتصال فایل‌های استاتیک
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # تنظیمات قالب‌ها
    templates = Jinja2Templates(directory=str(templates_dir))
    
    # افزودن مسیرهای API
    app.include_router(router)
    
    # مسیر اصلی با رابط کاربری
    @app.get("/")
    async def root(request: Request):
        """نمایش صفحه اصلی رابط کاربری"""
        return templates.TemplateResponse("index.html", {"request": request})
    
    return app


def run_server(config: Config = None):
    """
    اجرای سرور FastAPI (عمومی - بدون نیاز به احراز هویت)
    
    Args:
        config: شیء تنظیمات
    """
    config = config or Config.from_env()
    app = create_app(config)
    
    print("=" * 60)
    print("🚀 DEVIP Guard - تشخیص محتوای نامناسب (API عمومی)")
    print("=" * 60)
    print(f"🌐 رابط کاربری وب: http://localhost:{config.port}")
    print(f"🏥 بررسی سلامت: http://localhost:{config.port}/api/v1/health")
    print("=" * 60)
    print("📤 POST /api/v1/classify-img    - آپلود تصویر (JPG, PNG, WEBP, BMP)")
    print("🎞️ POST /api/v1/classify-gif    - آپلود انیمیشن گیف")
    print("🎬 POST /api/v1/classify-video  - آپلود ویدیو (MP4, AVI, MOV, MKV)")
    print("🔗 POST /api/v1/classify-url    - تحلیل از طریق لینک")
    print("🧹 POST /api/v1/cleanup         - پاکسازی حافظه")
    print("=" * 60)
    print("🔓 بدون نیاز به احراز هویت - API عمومی")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=config.port,
        log_level="info" if config.debug else "warning"
    )


if __name__ == "__main__":
    run_server()