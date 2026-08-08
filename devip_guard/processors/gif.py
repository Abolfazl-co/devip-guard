# -*- coding: utf-8 -*-
"""
DEVIP Guard - پردازشگر گیف
"""

import os
import gc
from typing import Optional, Dict, Callable, List
from PIL import Image
import numpy as np

from ..core.config import Config


class GIFProcessor:
    """
    پردازش انیمیشن‌های گیف برای تشخیص محتوای نامناسب
    
    دارای روش‌های جایگزین متعدد برای پشتیبانی از فایل‌های گیف خراب یا غیرمعمول
    """
    
    def __init__(self, config: Config, predict_fn: Callable):
        self.config = config
        self.image_dim = config.image_dim
        self.predict_fn = predict_fn
        self.max_frames = 100
    
    def process(self, gif_path: str) -> Optional[Dict[str, float]]:
        """
        پردازش فایل گیف با روش‌های جایگزین متعدد
        
        Args:
            gif_path: مسیر فایل گیف
        
        Returns:
            میانگین پیش‌بینی‌ها از تمام فریم‌ها
        """
        try:
            # بررسی حجم فایل
            file_size = os.path.getsize(gif_path)
            if file_size > self.config.max_file_size * 1024 * 1024:
                print(f"⚠️ حجم فایل گیف بسیار زیاد است: {file_size} بایت")
            
            # روش ۱: تلاش با PIL
            result = self._try_pil_method(gif_path)
            if result is not None:
                return result
            
            # روش ۲: تلاش با OpenCV
            result = self._try_opencv_method(gif_path)
            if result is not None:
                return result
            
            # روش ۳: تلاش با imageio
            result = self._try_imageio_method(gif_path)
            if result is not None:
                return result
            
            # روش ۴: تلاش با خواندن به صورت بایت
            result = self._try_bytes_method(gif_path)
            if result is not None:
                return result
            
            print(f"❌ تمام روش‌های پردازش گیف برای فایل ناموفق بود: {gif_path}")
            return None
        
        except Exception as e:
            print(f"❌ خطا در پردازش گیف {gif_path}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _try_pil_method(self, gif_path: str) -> Optional[Dict[str, float]]:
        """روش ۱: PIL با مدیریت خطا"""
        try:
            # بررسی هدر فایل
            with open(gif_path, 'rb') as f:
                header = f.read(6)
            
            # بررسی هدر GIF
            if not (header[:3] == b'GIF' or header[:4] == b'\x00\x00\x00\x00'):
                print(f"⚠️ فایل گیف معتبر نیست (هدر: {header[:6]})")
                return None
            
            # تلاش برای باز کردن با PIL
            image = Image.open(gif_path)
            
            # بررسی اینکه آیا انیمیشن است
            is_animated = False
            try:
                is_animated = getattr(image, 'is_animated', False) or \
                             (image.format == 'GIF' and getattr(image, 'n_frames', 1) > 1)
            except:
                pass
            
            if not is_animated:
                # پردازش به عنوان تصویر معمولی
                print("ℹ️ گیف انیمیشن نیست، به عنوان یک فریم پردازش می‌شود")
                image.seek(0)
                frame = image.convert('RGB')
                resized = frame.resize((self.image_dim, self.image_dim), Image.BICUBIC)
                img_array = np.array(resized, dtype=np.float32) / 255.0
                img_array = np.expand_dims(img_array, axis=0)
                predictions = self.predict_fn(img_array)
                return self._format_predictions(predictions)
            
            # پردازش انیمیشن
            return self._process_animated_pil(image)
            
        except Exception as e:
            print(f"⚠️ روش PIL ناموفق: {e}")
            return None
    
    def _process_animated_pil(self, gif: Image.Image) -> Optional[Dict[str, float]]:
        """پردازش گیف انیمیشنی با استفاده از PIL"""
        try:
            frame_count = min(gif.n_frames, self.max_frames)
            print(f"ℹ️ پردازش گیف انیمیشنی با {frame_count} فریم (PIL)")
            
            all_predictions = []
            
            for frame_idx in range(frame_count):
                try:
                    gif.seek(frame_idx)
                    frame = gif.convert('RGB')
                    
                    resized = frame.resize(
                        (self.image_dim, self.image_dim),
                        Image.BICUBIC
                    )
                    
                    img_array = np.array(resized, dtype=np.float32) / 255.0
                    img_array = np.expand_dims(img_array, axis=0)
                    
                    predictions = self.predict_fn(img_array)
                    all_predictions.append(predictions)
                    
                    del frame, resized, img_array
                    
                    if frame_idx % 10 == 0:
                        gc.collect()
                        
                except Exception as e:
                    print(f"⚠️ خطا در پردازش فریم {frame_idx}: {e}")
                    continue
            
            if not all_predictions:
                return None
            
            avg_predictions = np.mean(all_predictions, axis=0)
            print(f"✅ پردازش گیف با PIL کامل شد: {len(all_predictions)} فریم میانگین گرفته شد")
            return self._format_predictions(avg_predictions)
            
        except Exception as e:
            print(f"⚠️ پردازش انیمیشنی با PIL ناموفق: {e}")
            return None
    
    def _try_opencv_method(self, gif_path: str) -> Optional[Dict[str, float]]:
        """روش ۲: OpenCV به عنوان روش جایگزین"""
        try:
            import cv2
            
            print("🔄 تلاش با روش OpenCV برای گیف...")
            cap = cv2.VideoCapture(gif_path)
            
            if not cap.isOpened():
                print("⚠️ OpenCV نمی‌تواند گیف را باز کند")
                cap.release()
                return None
            
            frames = []
            frame_count = 0
            
            while frame_count < self.max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(Image.fromarray(frame_rgb))
                frame_count += 1
            
            cap.release()
            
            if not frames:
                print("⚠️ OpenCV: هیچ فریمی استخراج نشد")
                return None
            
            print(f"ℹ️ پردازش {len(frames)} فریم (OpenCV)")
            
            all_predictions = []
            for frame in frames:
                resized = frame.resize((self.image_dim, self.image_dim), Image.BICUBIC)
                img_array = np.array(resized, dtype=np.float32) / 255.0
                img_array = np.expand_dims(img_array, axis=0)
                predictions = self.predict_fn(img_array)
                all_predictions.append(predictions)
                del frame, resized, img_array
                gc.collect()
            
            if not all_predictions:
                return None
            
            avg_predictions = np.mean(all_predictions, axis=0)
            print(f"✅ پردازش گیف با OpenCV کامل شد: {len(all_predictions)} فریم میانگین گرفته شد")
            return self._format_predictions(avg_predictions)
            
        except ImportError:
            print("⚠️ OpenCV نصب نیست")
            return None
        except Exception as e:
            print(f"⚠️ روش OpenCV ناموفق: {e}")
            return None
    
    def _try_imageio_method(self, gif_path: str) -> Optional[Dict[str, float]]:
        """روش ۳: imageio به عنوان روش جایگزین"""
        try:
            import imageio.v2 as imageio
            
            print("🔄 تلاش با روش imageio برای گیف...")
            frames = imageio.mimread(gif_path, memtest=False)
            
            if not frames:
                print("⚠️ imageio: هیچ فریمی استخراج نشد")
                return None
            
            frames = frames[:self.max_frames]
            print(f"ℹ️ پردازش {len(frames)} فریم (imageio)")
            
            all_predictions = []
            for frame in frames:
                # تبدیل به RGB در صورت نیاز
                if len(frame.shape) == 2:
                    frame = np.stack([frame]*3, axis=-1)
                elif frame.shape[2] == 4:
                    frame = frame[:, :, :3]
                
                pil_image = Image.fromarray(frame)
                resized = pil_image.resize((self.image_dim, self.image_dim), Image.BICUBIC)
                img_array = np.array(resized, dtype=np.float32) / 255.0
                img_array = np.expand_dims(img_array, axis=0)
                predictions = self.predict_fn(img_array)
                all_predictions.append(predictions)
                del frame, pil_image, resized, img_array
                gc.collect()
            
            if not all_predictions:
                return None
            
            avg_predictions = np.mean(all_predictions, axis=0)
            print(f"✅ پردازش گیف با imageio کامل شد: {len(all_predictions)} فریم میانگین گرفته شد")
            return self._format_predictions(avg_predictions)
            
        except ImportError:
            print("⚠️ imageio نصب نیست")
            return None
        except Exception as e:
            print(f"⚠️ روش imageio ناموفق: {e}")
            return None
    
    def _try_bytes_method(self, gif_path: str) -> Optional[Dict[str, float]]:
        """روش ۴: خواندن به صورت بایت و پردازش"""
        try:
            print("🔄 تلاش با روش بایت برای گیف...")
            
            with open(gif_path, 'rb') as f:
                content = f.read()
            
            from PIL import Image
            import io
            
            image = Image.open(io.BytesIO(content))
            image.seek(0)
            frame = image.convert('RGB')
            
            resized = frame.resize((self.image_dim, self.image_dim), Image.BICUBIC)
            img_array = np.array(resized, dtype=np.float32) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            predictions = self.predict_fn(img_array)
            
            print("✅ پردازش گیف با روش بایت کامل شد: یک فریم")
            return self._format_predictions(predictions)
            
        except Exception as e:
            print(f"⚠️ روش بایت ناموفق: {e}")
            return None
    
    def _format_predictions(self, predictions: np.ndarray) -> Dict[str, float]:
        """تبدیل پیش‌بینی‌ها به دیکشنری"""
        categories = ['drawing', 'hentai', 'neutral', 'porn', 'sexy']
        return {
            category: round(float(predictions[i]), 8)
            for i, category in enumerate(categories)
        }