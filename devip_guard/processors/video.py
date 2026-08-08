# -*- coding: utf-8 -*-
"""
DEVIP Guard - پردازشگر ویدیو
"""

import os
import gc
from typing import Optional, Dict, Callable, List
import cv2
import numpy as np
from PIL import Image

from ..core.config import Config


class VideoProcessor:
    """
    پردازش فایل‌های ویدیو برای تشخیص محتوای نامناسب
    
    پشتیبانی از: MP4, AVI, MOV, MKV, WMV, FLV, WEBM
    """
    
    def __init__(self, config: Config, predict_fn: Callable):
        self.config = config
        self.image_dim = config.image_dim
        self.predict_fn = predict_fn
        self.max_frames = 500  # محدودیت فریم برای بهبود عملکرد
    
    def process(self, video_path: str, 
                sample_rate: float = 0.1,
                max_frames: Optional[int] = None) -> Optional[Dict]:
        """
        پردازش فایل ویدیو
        
        Args:
            video_path: مسیر فایل ویدیو
            sample_rate: نرخ نمونه‌برداری فریم (۰ تا ۱)
            max_frames: حداکثر فریم‌های قابل پردازش
        
        Returns:
            دیکشنری شامل میانگین پیش‌بینی‌ها و جزئیات فریم‌ها
        """
        cap = None
        try:
            # بررسی حجم فایل
            if os.path.getsize(video_path) > 100 * 1024 * 1024:
                raise ValueError("حجم ویدیو بسیار زیاد است: حداکثر ۱۰۰ مگابایت")
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"باز کردن ویدیو امکان‌پذیر نیست: {video_path}")
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            if total_frames <= 0:
                raise ValueError("ویدیو فاقد فریم است")
            
            # محاسبه فاصله فریم‌ها
            if sample_rate <= 0 or sample_rate > 1:
                sample_rate = 0.1
            frame_interval = max(1, int(1 / sample_rate))
            
            # محدود کردن فریم‌ها
            max_allowed = min(max_frames or self.max_frames, self.max_frames)
            frames_to_process = min(total_frames, max_allowed * frame_interval)
            
            all_predictions = []
            frame_scores = []
            
            print(f"📹 پردازش ویدیو: {total_frames} فریم، نمونه‌برداری هر {frame_interval} فریم")
            
            processed_count = 0
            for frame_idx in range(0, int(frames_to_process), frame_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if not ret:
                    break
                
                # تبدیل به RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                
                # تغییر اندازه
                resized = pil_image.resize(
                    (self.image_dim, self.image_dim),
                    Image.BICUBIC
                )
                
                # تبدیل به آرایه
                img_array = np.array(resized, dtype=np.float32) / 255.0
                img_array = np.expand_dims(img_array, axis=0)
                
                # تشخیص
                predictions = self.predict_fn(img_array)
                all_predictions.append(predictions)
                
                # ثبت امتیاز فریم
                timestamp = frame_idx / fps if fps > 0 else frame_idx
                frame_scores.append({
                    'time': round(timestamp, 2),
                    'predictions': self._format_predictions(predictions)
                })
                
                processed_count += 1
                
                # نمایش پیشرفت
                if processed_count % 10 == 0:
                    print(f"\r   پردازش شده: {processed_count} فریم", end="")
                
                # پاکسازی حافظه
                del frame, frame_rgb, pil_image, resized, img_array
                
                # پاکسازی دوره‌ای
                if processed_count % 50 == 0:
                    gc.collect()
            
            print()  # خط جدید بعد از نمایش پیشرفت
            
            cap.release()
            
            if not all_predictions:
                return None
            
            # میانگین پیش‌بینی‌ها
            avg_predictions = np.mean(all_predictions, axis=0)
            
            return {
                'average': self._format_predictions(avg_predictions),
                'frames': frame_scores,
                'metadata': {
                    'total_frames': total_frames,
                    'processed_frames': len(all_predictions),
                    'fps': fps,
                    'duration': total_frames / fps if fps > 0 else 0,
                    'sample_rate': sample_rate,
                    'resolution': f"{width}x{height}"
                }
            }
        
        except Exception as e:
            print(f"خطا در پردازش ویدیو: {e}")
            if cap:
                cap.release()
            return None
    
    def _format_predictions(self, predictions: np.ndarray) -> Dict[str, float]:
        """
        تبدیل پیش‌بینی‌ها به دیکشنری
        
        Args:
            predictions: آرایه پیش‌بینی‌ها
        
        Returns:
            دیکشنری دسته‌بندی‌ها با مقادیر گرد شده
        """
        categories = ['drawing', 'hentai', 'neutral', 'porn', 'sexy']
        return {
            category: round(float(predictions[i]), 8)
            for i, category in enumerate(categories)
        }