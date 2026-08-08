# -*- coding: utf-8 -*-
"""
DEVIP Guard - مدیریت مدل
"""

import os
import json
import platform
import urllib.request
from typing import Optional
from pathlib import Path
import hashlib

from .config import Config, MODEL_TYPES


class ModelManager:
    """
    مدیریت دانلود، کش و اعتبارسنجی مدل
    
    قابلیت‌ها:
        - دانلود خودکار مدل از گیت‌هاب
        - کش محلی با نسخه‌بندی
        - پشتیبانی از آینه برای کاربران چین
        - اعتبارسنجی یکپارچگی مدل
        - پشتیبانی از دایرکتوری محلی مدل
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.cache_dir = config.get_cache_path()
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # دایرکتوری محلی مدل
        self.local_dir = config.get_local_model_path()
    
    def get_model_path(self, model_type: Optional[str] = None) -> str:
        """
        دریافت مسیر مدل، در صورت عدم وجود دانلود می‌کند
        
        Args:
            model_type: نوع مدل (d/m2/i3)، در صورت None از تنظیمات استفاده می‌شود
        
        Returns:
            مسیر فایل مدل
        """
        model_type = model_type or self.config.model_type
        
        if model_type not in MODEL_TYPES:
            raise ValueError(f"نوع مدل ناشناخته: {model_type}. موارد موجود: {list(MODEL_TYPES.keys())}")
        
        # ۱. بررسی متغیر محیطی
        env_path = os.environ.get("DEVIP_GUARD_MODEL")
        if env_path and os.path.exists(env_path):
            print(f"✅ استفاده از مدل از متغیر محیطی: {env_path}")
            return env_path
        
        # ۲. بررسی مسیر سفارشی در تنظیمات
        if self.config.model_path and os.path.exists(self.config.model_path):
            print(f"✅ استفاده از مدل از تنظیمات: {self.config.model_path}")
            return self.config.model_path
        
        # ۳. بررسی دایرکتوری محلی مدل (اولویت)
        model_config = MODEL_TYPES[model_type]
        local_model_path = self.local_dir / model_config.filename
        
        if local_model_path.exists():
            print(f"✅ استفاده از مدل محلی: {local_model_path}")
            return str(local_model_path)
        
        # ۴. بررسی دایرکتوری کش
        cache_model_path = self.cache_dir / model_config.filename
        
        if cache_model_path.exists():
            print(f"✅ استفاده از مدل کش شده: {cache_model_path}")
            return str(cache_model_path)
        
        # ۵. دانلود مدل در صورت عدم وجود در هر مکان
        print(f"📥 مدل به صورت محلی یافت نشد. در حال دانلود...")
        print(f"   منبع: {model_config.url}")
        print(f"   مقصد: {cache_model_path}")
        self._download_model(model_config.url, cache_model_path)
        print("✅ دانلود کامل شد")
        
        return str(cache_model_path)
    
    def _download_model(self, url: str, destination: Path):
        """دانلود فایل مدل با نمایش پیشرفت"""
        url = self._get_download_url(url)
        
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'DEVIP-Guard/1.0'}
            )
            
            with urllib.request.urlopen(req) as response:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                chunk_size = 8192
                
                with open(destination, "wb") as f:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            percent = int((downloaded / total_size) * 100)
                            print(f"\r   پیشرفت: {percent}%", end="")
                
                print()
        
        except urllib.error.URLError as e:
            raise RuntimeError(f"دانلود ناموفق: {e}. لطفاً اتصال اینترنت خود را بررسی کنید.")
        except Exception as e:
            raise RuntimeError(f"دانلود ناموفق: {e}")
    
    def _get_download_url(self, original_url: str) -> str:
        """دریافت آدرس دانلود با پشتیبانی از آینه"""
        use_mirror = self.config.use_china_mirror or self._is_in_china()
        
        if use_mirror:
            mirror = self.config.github_mirror
            if mirror:
                return f"{mirror}/{original_url}"
            return original_url.replace(
                "https://github.com",
                "https://ghproxy.cn/https://github.com"
            )
        
        return original_url
    
    @staticmethod
    def _is_in_china() -> bool:
        """بررسی اینکه کاربر در چین است یا خیر"""
        use_mirror = os.environ.get("DEVIP_GUARD_USE_CHINA_MIRROR")
        if use_mirror is not None:
            return use_mirror.lower() in ('1', 'true', 'yes')
        
        try:
            import time
            tz_offset = -time.timezone / 3600
            return tz_offset == 8
        except Exception:
            return False
    
    def clear_cache(self):
        """پاکسازی کش مدل"""
        deleted = 0
        for file in self.cache_dir.glob("*.onnx"):
            try:
                file.unlink()
                deleted += 1
            except Exception:
                pass
        
        index_file = self.cache_dir / "models.json"
        if index_file.exists():
            try:
                index_file.unlink()
            except Exception:
                pass
        
        return deleted
    
    def get_cache_info(self) -> dict:
        """دریافت اطلاعات کش"""
        models = []
        total_size = 0
        
        for file in self.cache_dir.glob("*.onnx"):
            size = file.stat().st_size
            total_size += size
            models.append({
                "name": file.name,
                "size_mb": round(size / (1024 * 1024), 2),
                "modified": file.stat().st_mtime
            })
        
        return {
            "cache_dir": str(self.cache_dir),
            "total_models": len(models),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "models": models
        }