# -*- coding: utf-8 -*-
"""
DEVIP Guard - مدیریت تنظیمات
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, List
from pathlib import Path


@dataclass
class Config:
    """
    تنظیمات اصلی دیویپ گارد
    
    متغیرهای محیطی:
        DEVIP_GUARD_MODEL_TYPE: نوع مدل (d/m2/i3)
        DEVIP_GUARD_MODEL: مسیر سفارشی مدل
        DEVIP_GUARD_DEVICE: دستگاه اجرا (cpu/cuda/tensorrt/dml/coreml/openvino)
        DEVIP_GUARD_CLEANUP_INTERVAL: فاصله پاکسازی حافظه (تعداد تشخیص‌ها)
        DEVIP_GUARD_INTRA_THREADS: تعداد نخ‌های درون عملیاتی ONNX
        DEVIP_GUARD_INTER_THREADS: تعداد نخ‌های بین عملیاتی ONNX
        DEVIP_GUARD_CACHE_DIR: مسیر دایرکتوری کش مدل
        DEVIP_GUARD_UPLOAD_DIR: مسیر دایرکتوری آپلود
        DEVIP_GUARD_HOST: میزبان سرور
        DEVIP_GUARD_PORT: پورت سرور
        DEVIP_GUARD_DEBUG: حالت اشکال‌زدایی
        DEVIP_GUARD_MAX_FILE_SIZE: حداکثر حجم فایل به مگابایت
        DEVIP_GUARD_USE_CHINA_MIRROR: استفاده از آینه چین
        DEVIP_GUARD_GITHUB_MIRROR: آینه سفارشی گیت‌هاب
        DEVIP_GUARD_NSFW_THRESHOLD: آستانه NSFW (پیش‌فرض: 0.85)
        DEVIP_GUARD_SAFE_THRESHOLD: آستانه ایمن (پیش‌فرض: 0.25)
    """
    
    # تنظیمات مدل
    model_type: str = "d"
    model_path: Optional[str] = None
    device: str = "cpu"
    
    # تنظیمات تصویر
    image_dim: int = 224
    max_file_size: int = 20  # مگابایت
    
    # تنظیمات عملکرد
    cleanup_interval: int = 100
    intra_threads: int = 2
    inter_threads: int = 1
    
    # تنظیمات کش
    cache_dir: str = "~/.cache/devip_guard"
    
    # دایرکتوری محلی مدل
    local_model_dir: str = "devip_guard_model"
    
    # تنظیمات آپلود
    upload_dir: str = "uploads"
    
    # تنظیمات سرور
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # تنظیمات آینه
    use_china_mirror: bool = False
    github_mirror: Optional[str] = None
    
    # آستانه‌ها - آستانه بالاتر برای کاهش خطاهای مثبت
    nsfw_threshold: float = 0.85  
    safe_threshold: float = 0.25   
    suspicious_threshold: float = 0.60 
    
    @classmethod
    def from_env(cls) -> "Config":
        """
        ایجاد تنظیمات از متغیرهای محیطی
        
        Returns:
            شیء تنظیمات با مقادیر خوانده شده از محیط
        """
        return cls(
            model_type=os.environ.get("DEVIP_GUARD_MODEL_TYPE", "d"),
            model_path=os.environ.get("DEVIP_GUARD_MODEL"),
            device=os.environ.get("DEVIP_GUARD_DEVICE", "cpu"),
            cleanup_interval=int(os.environ.get("DEVIP_GUARD_CLEANUP_INTERVAL", "100")),
            intra_threads=int(os.environ.get("DEVIP_GUARD_INTRA_THREADS", "2")),
            inter_threads=int(os.environ.get("DEVIP_GUARD_INTER_THREADS", "1")),
            cache_dir=os.environ.get("DEVIP_GUARD_CACHE_DIR", "~/.cache/devip_guard"),
            local_model_dir=os.environ.get("DEVIP_GUARD_LOCAL_MODEL_DIR", "devip_guard_model"),
            upload_dir=os.environ.get("DEVIP_GUARD_UPLOAD_DIR", "uploads"),
            host=os.environ.get("DEVIP_GUARD_HOST", "0.0.0.0"),
            port=int(os.environ.get("DEVIP_GUARD_PORT", "8000")),
            debug=os.environ.get("DEVIP_GUARD_DEBUG", "false").lower() == "true",
            use_china_mirror=os.environ.get("DEVIP_GUARD_USE_CHINA_MIRROR", "false").lower() in ("true", "1", "yes"),
            github_mirror=os.environ.get("DEVIP_GUARD_GITHUB_MIRROR"),
            nsfw_threshold=float(os.environ.get("DEVIP_GUARD_NSFW_THRESHOLD", "0.85")),
            safe_threshold=float(os.environ.get("DEVIP_GUARD_SAFE_THRESHOLD", "0.25")),
            suspicious_threshold=float(os.environ.get("DEVIP_GUARD_SUSPICIOUS_THRESHOLD", "0.60"))
        )
    
    def to_dict(self) -> Dict:
        """
        تبدیل تنظیمات به دیکشنری
        
        Returns:
            دیکشنری شامل تمام تنظیمات
        """
        return {
            "model_type": self.model_type,
            "model_path": self.model_path,
            "device": self.device,
            "image_dim": self.image_dim,
            "max_file_size": self.max_file_size,
            "cleanup_interval": self.cleanup_interval,
            "intra_threads": self.intra_threads,
            "inter_threads": self.inter_threads,
            "cache_dir": self.cache_dir,
            "local_model_dir": self.local_model_dir,
            "upload_dir": self.upload_dir,
            "host": self.host,
            "port": self.port,
            "debug": self.debug,
            "thresholds": {
                "nsfw": self.nsfw_threshold,
                "safe": self.safe_threshold,
                "suspicious": self.suspicious_threshold
            }
        }
    
    def get_cache_path(self) -> Path:
        """
        دریافت مسیر کامل دایرکتوری کش
        
        Returns:
            مسیر دایرکتوری کش با گسترش ~
        """
        return Path(os.path.expanduser(self.cache_dir))
    
    def get_upload_path(self) -> Path:
        """
        دریافت مسیر دایرکتوری آپلود
        
        Returns:
            مسیر دایرکتوری آپلود
        """
        return Path(self.upload_dir)
    
    def get_local_model_path(self) -> Path:
        """
        دریافت مسیر دایرکتوری محلی مدل
        
        Returns:
            مسیر دایرکتوری محلی مدل
        """
        return Path(self.local_model_dir)


@dataclass
class ModelConfig:
    """تنظیمات مدل"""
    url: str
    filename: str
    dim: int
    description: str = ""


# انواع مدل‌های موجود
MODEL_TYPES: Dict[str, ModelConfig] = {
    'd': ModelConfig(
        url="https://github.com/AbolfazlZarei-dev/devip-guard/devip_guard_model/devip_guard_model.onnx",
        filename="devip_guard_model.onnx",
        dim=224,
        description="مدل پیش‌فرض MobileNet V2"
    ),
    'm2': ModelConfig(
        url="https://github.com/AbolfazlZarei-dev/devip-guard/devip_guard_model/devip_guard_m2model.onnx",
        filename="devip_guard_m2model.onnx",
        dim=224,
        description="مدل بهینه‌شده MobileNet V2"
    ),
    'i3': ModelConfig(
        url="https://github.com/AbolfazlZarei-dev/devip-guard/devip_guard_model/devip_guard_i3model.onnx",
        filename="devip_guard_i3model.onnx",
        dim=299,
        description="مدل Inception V3 (دقت بالاتر)"
    )
}

# دسته‌بندی‌های تشخیص - ترتیب اهمیت دارد!
CATEGORIES: List[str] = ['drawing', 'hentai', 'neutral', 'porn', 'sexy']

# رنگ‌های دسته‌بندی برای رابط کاربری
CATEGORY_COLORS: Dict[str, str] = {
    'neutral': '#22c55e',
    'sexy': '#f59e0b',
    'porn': '#ef4444',
    'hentai': '#a855f7',
    'drawing': '#3b82f6'
}

# توضیحات دسته‌بندی‌ها
CATEGORY_DESCRIPTIONS: Dict[str, str] = {
    'neutral': 'محتوای ایمن و معمولی',
    'sexy': 'محتوای تحریک‌کننده',
    'porn': 'محتوای صریح بزرگسالان',
    'hentai': 'محتوای صریح انیمه',
    'drawing': 'نقاشی‌ها و تصاویر هنری'
}

# وزن‌های NSFW - وزن کمتر برای sexy برای کاهش خطاهای مثبت
NSFW_WEIGHTS: Dict[str, float] = {
    "porn": 1.0,      # کاملاً غیراخلاقی
    "hentai": 0.85,   # انیمه غیراخلاقی
    "sexy": 0.25,     # تحریک‌آمیز - وزن کمتر برای کاهش خطاهای مثبت
    "drawing": 0.02,  # نقاشی - معمولاً ایمن
    "neutral": 0.0    # بی‌خطر
}