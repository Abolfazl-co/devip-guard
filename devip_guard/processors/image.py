# -*- coding: utf-8 -*-
"""
DEVIP Guard - پردازشگر تصویر
"""

import os
import io
from typing import Optional, Union, Tuple
from PIL import Image
import numpy as np

from ..core.config import Config


class ImageProcessor:
    """
    پردازش تصاویر تکی برای تشخیص محتوای نامناسب
    
    پشتیبانی از: JPG, PNG, WEBP, BMP, TIFF, GIF (فریم اول)
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.image_dim = config.image_dim
        self.max_file_size = config.max_file_size * 1024 * 1024
    
    def process(self, image_path: str) -> Optional[np.ndarray]:
        """
        پردازش تصویر از مسیر فایل
        
        Args:
            image_path: مسیر فایل تصویر
        
        Returns:
            تصویر پیش‌پردازش شده به صورت آرایه numpy (N, H, W, C)
        """
        try:
            # بررسی حجم فایل
            if os.path.getsize(image_path) > self.max_file_size:
                print(f"⚠️ حجم فایل بسیار زیاد است: {os.path.getsize(image_path)} بایت، اما تلاش برای پردازش ادامه دارد")
            
            image = Image.open(image_path)
            
            # اگر گیف است، فریم اول را بگیر
            if image.format == 'GIF':
                try:
                    image.seek(0)
                except:
                    pass
            
            return self._process_image(image)
        
        except Exception as e:
            print(f"خطا در پردازش تصویر {image_path}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def process_bytes(self, image_bytes: bytes) -> Optional[np.ndarray]:
        """
        پردازش تصویر از داده باینری
        
        Args:
            image_bytes: داده تصویر به صورت بایت
        
        Returns:
            تصویر پیش‌پردازش شده به صورت آرایه numpy
        """
        try:
            if len(image_bytes) > self.max_file_size:
                print(f"⚠️ حجم داده بسیار زیاد است: {len(image_bytes)} بایت، اما تلاش برای پردازش ادامه دارد")
            
            image = Image.open(io.BytesIO(image_bytes))
            
            # اگر گیف است، فریم اول را بگیر
            if image.format == 'GIF':
                try:
                    image.seek(0)
                except:
                    pass
            
            return self._process_image(image)
        
        except Exception as e:
            print(f"خطا در پردازش داده باینری: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _process_image(self, image: Image.Image) -> np.ndarray:
        """
        پردازش داخلی تصویر
        
        Args:
            image: شیء تصویر PIL
        
        Returns:
            تصویر پیش‌پردازش شده به صورت آرایه numpy
        """
        try:
            # تبدیل به RGB
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # تغییر اندازه
            resized = image.resize((self.image_dim, self.image_dim), Image.BICUBIC)
            
            # تبدیل به آرایه numpy و نرمال‌سازی
            img_array = np.array(resized, dtype=np.float32) / 255.0
            
            # افزودن بعد دسته (batch)
            img_array = np.expand_dims(img_array, axis=0)
            
            return img_array
        
        except Exception as e:
            print(f"خطا در پردازش داخلی تصویر: {e}")
            raise