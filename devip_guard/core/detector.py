# -*- coding: utf-8 -*-
"""
DEVIP Guard - Core Detection Engine
"""

import os
import gc
import time
from typing import Dict, Optional, List, Any
import threading

import numpy as np
import onnxruntime as ort

from .config import Config, CATEGORIES, MODEL_TYPES, NSFW_WEIGHTS
from .models import ModelManager
from ..processors.image import ImageProcessor
from ..processors.gif import GIFProcessor
from ..processors.video import VideoProcessor


class DevipGuardDetector:
    """
    موتور اصلی تشخیص محتوای نامناسب دیویپ گارد
    
    قابلیت‌ها:
        - تشخیص در تصاویر، گیف و ویدیو
        - پشتیبانی از ONNX Runtime با GPU
        - مدیریت خودکار مدل
        - پشتیبانی از پردازش همزمان
        - اجرای ایمن در محیط چندنخی
        - تشخیص حجاب برای محتوای اسلامی
        - بهبود تشخیص خطاهای مثبت کاذب
    
    مثال:
        >>> detector = DevipGuardDetector()
        >>> result = detector.classify_with_veil("image.jpg")
        >>> print(result)
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        مقداردهی اولیه موتور تشخیص
        
        Args:
            config: شیء تنظیمات، در صورت None از Config.from_env() استفاده می‌شود
        """
        self.config = config or Config.from_env()
        self.model_manager = ModelManager(self.config)
        self._lock = threading.Lock()
        
        # دریافت آستانه‌ها از تنظیمات
        self.NSFW_THRESHOLD = self.config.nsfw_threshold
        self.SAFE_THRESHOLD = self.config.safe_threshold
        self.SUSPICIOUS_THRESHOLD = self.config.suspicious_threshold
        
        # راه‌اندازی پردازشگرها
        self.image_processor = ImageProcessor(self.config)
        self.gif_processor = GIFProcessor(self.config, self._predict_single)
        self.video_processor = VideoProcessor(self.config, self._predict_single)
        
        # بارگذاری مدل
        self._load_model()
        
        # آمار
        self.inference_count = 0
        self.error_count = 0
        self.start_time = time.time()
    
    def _load_model(self):
        """بارگذاری مدل ONNX"""
        model_path = self.model_manager.get_model_path(self.config.model_type)
        model_config = MODEL_TYPES.get(self.config.model_type)
        
        if model_config:
            self.image_dim = model_config.dim
        else:
            self.image_dim = 224
        
        self.categories = CATEGORIES
        
        # دریافت providers
        providers = self._get_providers()
        
        # تنظیمات نشست
        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        sess_options.enable_mem_pattern = True
        sess_options.enable_cpu_mem_arena = True
        sess_options.enable_mem_reuse = True
        sess_options.intra_op_num_threads = self.config.intra_threads
        sess_options.inter_op_num_threads = self.config.inter_threads
        
        # تنظیمات providers
        provider_options = self._get_provider_options(providers)
        
        # ایجاد نشست
        self.session = ort.InferenceSession(
            model_path,
            sess_options,
            providers=providers,
            provider_options=provider_options
        )
        
        self.input_name = self.session.get_inputs()[0].name
        self.output_names = [out.name for out in self.session.get_outputs()]
        
        print(f"✅ مدل بارگذاری شد: {model_path}")
        print(f"   ورودی: {self.input_name}, خروجی‌ها: {self.output_names}")
        print(f"   ارائه‌دهندگان: {providers}")
        print(f"   ابعاد تصویر: {self.image_dim}x{self.image_dim}")
        print(f"   آستانه‌ها: NSFW={self.NSFW_THRESHOLD}, Safe={self.SAFE_THRESHOLD}")
    
    def _get_providers(self) -> List[str]:
        """دریافت ارائه‌دهندگان اجرا"""
        available = ort.get_available_providers()
        providers = []
        
        device_map = {
            'cpu': [],
            'cuda': ['CUDAExecutionProvider'],
            'tensorrt': ['TensorrtExecutionProvider', 'CUDAExecutionProvider'],
            'dml': ['DmlExecutionProvider'],
            'coreml': ['CoreMLExecutionProvider'],
            'openvino': ['OpenVINOExecutionProvider'],
            'auto': [
                'TensorrtExecutionProvider',
                'CUDAExecutionProvider',
                'DmlExecutionProvider',
                'CoreMLExecutionProvider',
                'OpenVINOExecutionProvider'
            ]
        }
        
        device = self.config.device.lower()
        if device in device_map:
            for provider in device_map[device]:
                if provider in available:
                    providers.append(provider)
        
        if 'CPUExecutionProvider' not in providers:
            providers.append('CPUExecutionProvider')
        
        return providers
    
    def _get_provider_options(self, providers: List[str]) -> List[Dict]:
        """دریافت تنظیمات providers با محدودیت حافظه"""
        options_list = []
        
        for provider in providers:
            opts = {}
            
            if provider == 'CUDAExecutionProvider':
                gpu_limit = os.environ.get("DEVIP_GUARD_GPU_MEM_LIMIT")
                opts['gpu_mem_limit'] = int(gpu_limit) if gpu_limit else 500 * 1024 * 1024
                opts['arena_extend_strategy'] = 'kSameAsRequested'
                opts['enable_cuda_graph'] = False
                opts['cudnn_conv_algo_search'] = 'HEURISTIC'
            
            elif provider == 'TensorrtExecutionProvider':
                trt_workspace = os.environ.get("DEVIP_GUARD_TRT_MAX_WORKSPACE")
                opts['trt_max_workspace_size'] = int(trt_workspace) if trt_workspace else 1 * 1024 * 1024 * 1024
                opts['trt_max_cached_engines'] = 1
            
            options_list.append(opts)
        
        return options_list
    
    def _predict_single(self, image: np.ndarray) -> np.ndarray:
        """اجرای یک تشخیص (ایمن در محیط چندنخی)"""
        with self._lock:
            outputs = self.session.run(
                self.output_names,
                {self.input_name: image}
            )
            result = outputs[0][0].copy()
            
            self.inference_count += 1
            
            # پاکسازی دوره‌ای
            if self.config.cleanup_interval > 0 and \
               self.inference_count % self.config.cleanup_interval == 0:
                gc.collect()
            
            return result
    
    def _format_predictions(self, predictions: np.ndarray) -> Dict[str, float]:
        """تبدیل پیش‌بینی‌ها به دیکشنری"""
        return {
            category: round(float(predictions[i]), 8)
            for i, category in enumerate(self.categories)
        }
    
    def _calculate_nsfw_score(self, predictions: Dict[str, float]) -> float:
        """
        محاسبه امتیاز NSFW با وزن‌دهی مناسب
        
        وزن‌ها از NSFW_WEIGHTS:
        - porn: 1.0 (کاملاً غیراخلاقی)
        - hentai: 0.85 (انیمه غیراخلاقی)
        - sexy: 0.25 (تحریک‌آمیز - وزن کمتر برای کاهش خطاهای مثبت)
        - drawing: 0.02 (نقاشی - معمولاً ایمن)
        - neutral: 0.0 (بی‌خطر)
        
        قاعده جدید: اگر neutral بالاترین احتمال باشد، امتیاز NSFW کاهش می‌یابد
        """
        score = 0.0
        for category, prob in predictions.items():
            score += prob * NSFW_WEIGHTS.get(category, 0.0)
        
        # اگر neutral بالاترین احتمال بود، امتیاز را کاهش بده
        max_category = max(predictions, key=predictions.get)
        max_prob = predictions[max_category]
        neutral_prob = predictions.get("neutral", 0)
        
        if max_category == "neutral":
            # مدل معتقد است محتوا سالم است
            reduction_factor = 0.3  # فقط 30% امتیاز حفظ شود
            score = score * reduction_factor
            print(f"🟢 دسته غالب neutral ({neutral_prob:.3f})، کاهش امتیاز NSFW به {int((1-reduction_factor)*100)}%")
        
        elif neutral_prob > 0.5:
            # حتی اگر neutral بالاترین نبود، اما بالای 50% بود
            reduction_factor = 0.5
            score = score * reduction_factor
            print(f"🟢 احتمال بالای neutral ({neutral_prob:.3f})، کاهش امتیاز NSFW به {int((1-reduction_factor)*100)}%")
        
        # اگر sexy بالاترین است اما neutral هم بالاست
        # ممکن است محتوای عادی با لمس باشد (مثل بغل کردن)
        if max_category == "sexy" and neutral_prob > 0.3:
            ratio = max_prob / max(neutral_prob, 0.01)
            if ratio < 2.0:  # اگر sexy خیلی بالاتر از neutral نیست
                reduction_factor = 0.6
                score = score * reduction_factor
                print(f"🟡 محتوای مبهم (sexy={max_prob:.3f}, neutral={neutral_prob:.3f})، کاهش امتیاز")
        
        # نرمال‌سازی (محدود کردن به ۰ تا ۱)
        return min(1.0, max(0.0, score))
    
    def _detect_veil(self, image_path: str) -> Dict[str, Any]:
        """
        تشخیص تقریبی حجاب با بررسی رنگ‌های تیره در ناحیه سر
        
        Returns:
            دیکشنری شامل اطلاعات تشخیص حجاب
        """
        try:
            import cv2
            
            img = cv2.imread(image_path)
            if img is None:
                return {"has_veil": False, "confidence": 0.0, "method": "none"}
            
            height, width = img.shape[:2]
            
            # ناحیه سر (یک‌سوم بالای تصویر، وسط)
            head_y1 = 0
            head_y2 = int(height * 0.35)
            head_x1 = int(width * 0.2)
            head_x2 = int(width * 0.8)
            
            head_region = img[head_y1:head_y2, head_x1:head_x2]
            
            if head_region.size == 0:
                return {"has_veil": False, "confidence": 0.0, "method": "none"}
            
            # تبدیل به HSV برای تشخیص بهتر رنگ
            hsv = cv2.cvtColor(head_region, cv2.COLOR_BGR2HSV)
            
            # تشخیص رنگ‌های تیره (مشکی، قهوه‌ای تیره، سرمه‌ای، آبی تیره)
            dark_mask1 = cv2.inRange(hsv, (0, 0, 0), (180, 255, 40))
            dark_mask2 = cv2.inRange(hsv, (0, 0, 40), (180, 255, 60))
            dark_mask = cv2.bitwise_or(dark_mask1, dark_mask2)
            
            dark_ratio = np.sum(dark_mask > 0) / dark_mask.size
            
            # تشخیص رنگ‌های روشن (برای تصاویر با روسری سفید)
            light_mask = cv2.inRange(hsv, (0, 0, 200), (180, 30, 255))
            light_ratio = np.sum(light_mask > 0) / light_mask.size
            
            # تشخیص رنگ‌های مشکی (چادر)
            black_mask = cv2.inRange(hsv, (0, 0, 0), (180, 255, 30))
            black_ratio = np.sum(black_mask > 0) / black_mask.size
            
            # ترکیب معیارها
            veil_score = 0.0
            method = "none"
            
            # اگر بیش از ۳۵٪ ناحیه سر تیره بود
            if dark_ratio > 0.35:
                veil_score += dark_ratio
                method = "dark"
            
            # اگر بیش از ۳۰٪ ناحیه سر روشن بود (روسری سفید)
            if light_ratio > 0.30:
                veil_score += light_ratio * 0.5
                method = "light" if method == "none" else "mixed"
            
            # اگر بیش از ۲۰٪ ناحیه سر کاملاً مشکی بود (چادر)
            if black_ratio > 0.20:
                veil_score += black_ratio * 1.2
                method = "black" if method == "none" else "mixed"
            
            # نرمال‌سازی
            veil_score = min(1.0, veil_score)
            
            # آستانه تشخیص حجاب
            has_veil = veil_score > 0.30
            
            return {
                "has_veil": has_veil,
                "confidence": round(veil_score, 3),
                "dark_ratio": round(dark_ratio, 3),
                "light_ratio": round(light_ratio, 3),
                "black_ratio": round(black_ratio, 3),
                "method": method
            }
        
        except Exception as e:
            print(f"⚠️ خطا در تشخیص حجاب: {e}")
            return {"has_veil": False, "confidence": 0.0, "method": "error"}
    
    def classify_with_veil(self, image_path: str) -> Optional[Dict]:
        """
        تشخیص NSFW با در نظر گرفتن حجاب
        
        Returns:
            دیکشنری کامل شامل predictions, scores و اطلاعات حجاب
        """
        predictions = self.predict_image(image_path)
        if not predictions:
            return None
        
        # محاسبه امتیاز NSFW
        raw_score = self._calculate_nsfw_score(predictions)
        
        # تشخیص حجاب
        veil_info = self._detect_veil(image_path)
        
        # تنظیم امتیاز نهایی با توجه به حجاب
        adjusted_score = raw_score
        if veil_info["has_veil"]:
            reduction = 0.3 * veil_info["confidence"]
            adjusted_score = max(0.0, raw_score - reduction)
            print(f"🕊️ حجاب تشخیص داده شد: کاهش امتیاز از {raw_score:.3f} به {adjusted_score:.3f}")
        
        # اعمال آستانه‌ها
        is_nsfw = adjusted_score >= self.NSFW_THRESHOLD
        is_safe = adjusted_score <= self.SAFE_THRESHOLD
        is_suspicious = self.SAFE_THRESHOLD < adjusted_score < self.NSFW_THRESHOLD
        
        print(f"📊 تحلیل امتیاز:")
        print(f"   پیش‌بینی‌ها: {predictions}")
        print(f"   دسته غالب: {max(predictions, key=predictions.get)}")
        print(f"   امتیاز خام NSFW: {raw_score:.4f}")
        print(f"   امتیاز نهایی: {adjusted_score:.4f}")
        print(f"   آستانه‌ها: NSFW≥{self.NSFW_THRESHOLD}, Safe≤{self.SAFE_THRESHOLD}")
        print(f"   نتیجه: {'NSFW' if is_nsfw else 'SAFE' if is_safe else 'SUSPICIOUS'}")
        
        return {
            "predictions": predictions,
            "raw_nsfw_score": raw_score,
            "adjusted_nsfw_score": adjusted_score,
            "is_nsfw": is_nsfw,
            "is_safe": is_safe,
            "is_suspicious": is_suspicious,
            "veil": veil_info,
            "thresholds": {
                "nsfw": self.NSFW_THRESHOLD,
                "safe": self.SAFE_THRESHOLD,
                "suspicious": self.SUSPICIOUS_THRESHOLD
            },
            "dominant_category": max(predictions, key=predictions.get)
        }
    
    # ========== متدهای عمومی ==========
    
    def predict_image(self, image_path: str) -> Optional[Dict[str, float]]:
        """
        تشخیص محتوای NSFW در تصویر
        
        Args:
            image_path: مسیر فایل تصویر (JPG, PNG, WEBP, BMP)
        
        Returns:
            دیکشنری احتمالات دسته‌بندی‌ها
        """
        if not os.path.exists(image_path):
            raise ValueError(f"تصویر یافت نشد: {image_path}")
        
        try:
            print(f"🔍 پردازش تصویر: {image_path}")
            result = self.image_processor.process(image_path)
            if result is None:
                return None
            
            predictions = self._predict_single(result)
            return self._format_predictions(predictions)
        
        except Exception as e:
            self.error_count += 1
            print(f"❌ تشخیص تصویر ناموفق: {e}")
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"تشخیص ناموفق: {e}")
    
    def predict_gif(self, gif_path: str) -> Optional[Dict[str, float]]:
        """
        تشخیص محتوای NSFW در گیف
        
        Args:
            gif_path: مسیر فایل گیف
        
        Returns:
            دیکشنری احتمالات دسته‌بندی‌ها (میانگین گرفته شده از فریم‌ها)
        """
        if not os.path.exists(gif_path):
            raise ValueError(f"گیف یافت نشد: {gif_path}")
        
        try:
            print(f"🔍 پردازش گیف: {gif_path}")
            result = self.gif_processor.process(gif_path)
            
            if result is None:
                print("⚠️ پردازشگر گیف مقداری برنگرداند، تلاش با پردازش تصویر...")
                result = self.predict_image(gif_path)
            
            return result
        
        except Exception as e:
            self.error_count += 1
            print(f"❌ پردازش گیف ناموفق: {e}")
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"پردازش گیف ناموفق: {e}")
    
    def predict_video(self, video_path: str, 
                      sample_rate: float = 0.1,
                      max_frames: Optional[int] = None) -> Optional[Dict]:
        """
        تشخیص محتوای NSFW در ویدیو
        
        Args:
            video_path: مسیر فایل ویدیو
            sample_rate: نرخ نمونه‌برداری فریم (۰ تا ۱)، پیش‌فرض ۰.۱
            max_frames: حداکثر فریم‌های پردازش، None = بدون محدودیت
        
        Returns:
            دیکشنری شامل میانگین پیش‌بینی‌ها و جزئیات فریم‌ها
        """
        if not os.path.exists(video_path):
            raise ValueError(f"ویدیو یافت نشد: {video_path}")
        
        try:
            return self.video_processor.process(
                video_path,
                sample_rate=sample_rate,
                max_frames=max_frames
            )
        
        except Exception as e:
            self.error_count += 1
            raise RuntimeError(f"پردازش ویدیو ناموفق: {e}")
    
    def predict_bytes(self, image_bytes: bytes) -> Optional[Dict[str, float]]:
        """
        تشخیص محتوای NSFW از داده باینری تصویر
        
        Args:
            image_bytes: داده تصویر به صورت بایت
        
        Returns:
            دیکشنری احتمالات دسته‌بندی‌ها
        """
        try:
            result = self.image_processor.process_bytes(image_bytes)
            if result is None:
                return None
            
            predictions = self._predict_single(result)
            return self._format_predictions(predictions)
        
        except Exception as e:
            self.error_count += 1
            raise RuntimeError(f"پردازش بایت ناموفق: {e}")
    
    def predict_with_score(self, image_path: str) -> Optional[Dict]:
        """
        تشخیص محتوای NSFW با امتیاز اضافی (قدیمی - از classify_with_veil استفاده کنید)
        
        Args:
            image_path: مسیر فایل تصویر
        
        Returns:
            دیکشنری شامل پیش‌بینی‌ها، امتیاز NSFW و دسته‌بندی
        """
        return self.classify_with_veil(image_path)
    
    def get_stats(self) -> Dict:
        """دریافت آمار تشخیص"""
        uptime = time.time() - self.start_time
        return {
            "inference_count": self.inference_count,
            "error_count": self.error_count,
            "device": self.config.device,
            "image_dim": self.image_dim,
            "cleanup_interval": self.config.cleanup_interval,
            "uptime_seconds": round(uptime, 2),
            "provider": str(self.session.get_providers()),
            "model_type": self.config.model_type,
            "thresholds": {
                "nsfw": self.NSFW_THRESHOLD,
                "safe": self.SAFE_THRESHOLD,
                "suspicious": self.SUSPICIOUS_THRESHOLD
            }
        }
    
    def cleanup(self):
        """پاکسازی منابع"""
        gc.collect()
        if hasattr(self, 'session'):
            del self.session
        gc.collect()
    
    # ========== متدهای همزمان ==========
    
    async def predict_image_async(self, image_path: str) -> Optional[Dict[str, float]]:
        """نسخه همزمان predict_image"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(
                pool, self.predict_image, image_path
            )
    
    async def predict_gif_async(self, gif_path: str) -> Optional[Dict[str, float]]:
        """نسخه همزمان predict_gif"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(
                pool, self.predict_gif, gif_path
            )
    
    async def predict_video_async(self, video_path: str,
                                   sample_rate: float = 0.1,
                                   max_frames: Optional[int] = None) -> Optional[Dict]:
        """نسخه همزمان predict_video"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(
                pool, self.predict_video, video_path, sample_rate, max_frames
            )
    
    async def predict_bytes_async(self, image_bytes: bytes) -> Optional[Dict[str, float]]:
        """نسخه همزمان predict_bytes"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(
                pool, self.predict_bytes, image_bytes
            )
    
    async def classify_with_veil_async(self, image_path: str) -> Optional[Dict]:
        """نسخه همزمان classify_with_veil"""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(
                pool, self.classify_with_veil, image_path
            )