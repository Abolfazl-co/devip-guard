# -*- coding: utf-8 -*-
"""
DEVIP Guard - مسیرهای API (عمومی - بدون احراز هویت)
"""

import os
import gc
import tempfile
from typing import Dict, Any
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Depends
from fastapi.responses import JSONResponse
import requests
import cv2
import numpy as np

from ..core.detector import DevipGuardDetector
from ..core.config import Config


def get_detector() -> DevipGuardDetector:
    """دریافت نمونه تشخیص‌دهنده"""
    config = Config.from_env()
    return DevipGuardDetector(config)


router = APIRouter(prefix="/api/v1", tags=["DEVIP Guard"])


#  توابع کمکی 

def convert_numpy_to_python(obj):
    """
    تبدیل تمام مقادیر numpy به Python native برای JSON
    
    Args:
        obj: شیء ورودی (می‌تواند numpy یا Python native باشد)
    
    Returns:
        شیء تبدیل شده به Python native
    """
    if isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_to_python(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_to_python(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_to_python(item) for item in obj)
    return obj


def clean_response(data: dict) -> dict:
    """
    پاکسازی دیکشنری پاسخ از مقادیر numpy
    
    Args:
        data: دیکشنری پاسخ
    
    Returns:
        دیکشنری پاکسازی شده
    """
    return convert_numpy_to_python(data)


#  تشخیص تصویر 

@router.post("/classify-img")
async def classify_image(
    image: UploadFile = File(...),
    detector: DevipGuardDetector = Depends(get_detector)
):
    """
    تشخیص محتوای نامناسب در تصویر آپلود شده
    
    ویژگی‌ها:
        - دسترسی عمومی - بدون نیاز به احراز هویت
        - پشتیبانی از: JPG, PNG, WEBP, BMP
        - حداکثر حجم: ۲۰ مگابایت
    """
    temp_path = None
    try:
        # بررسی نوع فایل
        valid_types = ['image/jpeg', 'image/png', 'image/webp', 'image/bmp']
        if image.content_type not in valid_types:
            raise HTTPException(
                status_code=415,
                detail=f"نوع فایل پشتیبانی نمی‌شود: {image.content_type}. فرمت‌های مجاز: JPG, PNG, WEBP, BMP"
            )
        
        # ایجاد پوشه آپلود
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # ذخیره فایل موقت
        temp_path = upload_dir / image.filename
        content = await image.read()
        
        # بررسی حجم فایل
        if len(content) > 20 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="حجم فایل بسیار زیاد است: حداکثر ۲۰ مگابایت"
            )
        
        with open(temp_path, "wb") as f:
            f.write(content)
        
        # تشخیص با در نظر گرفتن حجاب
        result = detector.classify_with_veil(str(temp_path))
        
        if not result:
            raise HTTPException(status_code=500, detail="تشخیص ناموفق بود")
        
        # ساخت پاسخ
        response_data = {
            "DEVIP_Guard": {
                "model": "DEVIP Guard-1",
                "ok": not result["is_nsfw"],
                "channel": "devip.ir",
                "writer": " @NingaCode ",
                "result": {
                    "filename": image.filename,
                    "type": "image",
                    "predictions": result["predictions"],
                    "dominant_category": result.get("dominant_category", ""),
                    "raw_nsfw_score": float(result["raw_nsfw_score"]),
                    "adjusted_nsfw_score": float(result["adjusted_nsfw_score"]),
                    "is_nsfw": bool(result["is_nsfw"]),
                    "is_safe": bool(result["is_safe"]),
                    "is_suspicious": bool(result["is_suspicious"]),
                    "veil": {
                        "has_veil": bool(result["veil"]["has_veil"]),
                        "confidence": float(result["veil"]["confidence"]),
                        "dark_ratio": float(result["veil"].get("dark_ratio", 0)),
                        "light_ratio": float(result["veil"].get("light_ratio", 0)),
                        "black_ratio": float(result["veil"].get("black_ratio", 0)),
                        "method": str(result["veil"].get("method", "none"))
                    },
                    "thresholds": {
                        "nsfw": float(result["thresholds"]["nsfw"]),
                        "safe": float(result["thresholds"]["safe"]),
                        "suspicious": float(result["thresholds"]["suspicious"])
                    }
                }
            }
        }
        
        return clean_response(response_data)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ خطا: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # حذف فایل موقت
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink()
            except:
                pass
        gc.collect()


#  تشخیص گیف 

@router.post("/classify-gif")
async def classify_gif(
    gif: UploadFile = File(...),
    detector: DevipGuardDetector = Depends(get_detector)
):
    """
    تشخیص محتوای نامناسب در گیف آپلود شده
    
    ویژگی‌ها:
        - دسترسی عمومی - بدون نیاز به احراز هویت
        - پشتیبانی از: GIF
        - حداکثر حجم: ۲۰ مگابایت
    """
    temp_path = None
    try:
        content_type = gif.content_type or ""
        filename = gif.filename or "file.gif"
        
        # اطمینان از پسوند صحیح
        if not filename.lower().endswith('.gif'):
            filename += '.gif'
        
        print(f"📁 دریافت گیف: {filename}, نوع محتوا: {content_type}")
        
        # ایجاد پوشه آپلود
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # ذخیره فایل موقت
        temp_path = upload_dir / filename
        content = await gif.read()
        
        if len(content) > 20 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="حجم فایل بسیار زیاد است: حداکثر ۲۰ مگابایت"
            )
        
        with open(temp_path, "wb") as f:
            f.write(content)
        
        print(f"📁 گیف ذخیره شد: {temp_path}, حجم: {len(content)} بایت")
        
        # تشخیص گیف
        try:
            gif_result = detector.predict_gif(str(temp_path))
            
            if gif_result:
                raw_score = detector._calculate_nsfw_score(gif_result)
                veil_info = detector._detect_veil(str(temp_path))
                
                adjusted_score = raw_score
                if veil_info.get("has_veil", False):
                    reduction = 0.3 * veil_info.get("confidence", 0.0)
                    adjusted_score = max(0.0, raw_score - reduction)
                
                is_nsfw = adjusted_score >= detector.NSFW_THRESHOLD
                is_safe = adjusted_score <= detector.SAFE_THRESHOLD
                is_suspicious = detector.SAFE_THRESHOLD < adjusted_score < detector.NSFW_THRESHOLD
                
                result = {
                    "predictions": gif_result,
                    "raw_nsfw_score": raw_score,
                    "adjusted_nsfw_score": adjusted_score,
                    "is_nsfw": is_nsfw,
                    "is_safe": is_safe,
                    "is_suspicious": is_suspicious,
                    "veil": veil_info,
                    "thresholds": {
                        "nsfw": detector.NSFW_THRESHOLD,
                        "safe": detector.SAFE_THRESHOLD,
                        "suspicious": detector.SUSPICIOUS_THRESHOLD
                    },
                    "dominant_category": max(gif_result, key=gif_result.get)
                }
            else:
                raise ValueError("پردازش گیف مقداری برنگرداند")
                
        except Exception as e:
            print(f"⚠️ پردازش گیف ناموفق: {e}، تلاش با روش‌های جایگزین...")
            
            result = None
            try:
                # روش جایگزین: استخراج فریم با OpenCV
                cap = cv2.VideoCapture(str(temp_path))
                frames_data = []
                
                while len(frames_data) < 10:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    temp_frame_path = temp_path.parent / f"temp_frame_{len(frames_data)}.jpg"
                    cv2.imwrite(str(temp_frame_path), frame)
                    
                    frame_result = detector.predict_image(str(temp_frame_path))
                    if frame_result:
                        frames_data.append(frame_result)
                    
                    if temp_frame_path.exists():
                        temp_frame_path.unlink()
                
                cap.release()
                
                if frames_data:
                    avg_predictions = {}
                    for cat in frames_data[0].keys():
                        avg_predictions[cat] = np.mean([f[cat] for f in frames_data])
                    
                    raw_score = detector._calculate_nsfw_score(avg_predictions)
                    veil_info = detector._detect_veil(str(temp_path))
                    
                    adjusted_score = raw_score
                    if veil_info.get("has_veil", False):
                        reduction = 0.3 * veil_info.get("confidence", 0.0)
                        adjusted_score = max(0.0, raw_score - reduction)
                    
                    result = {
                        "predictions": {k: float(v) for k, v in avg_predictions.items()},
                        "raw_nsfw_score": raw_score,
                        "adjusted_nsfw_score": adjusted_score,
                        "is_nsfw": adjusted_score >= detector.NSFW_THRESHOLD,
                        "is_safe": adjusted_score <= detector.SAFE_THRESHOLD,
                        "is_suspicious": detector.SAFE_THRESHOLD < adjusted_score < detector.NSFW_THRESHOLD,
                        "veil": veil_info,
                        "thresholds": {
                            "nsfw": detector.NSFW_THRESHOLD,
                            "safe": detector.SAFE_THRESHOLD,
                            "suspicious": detector.SUSPICIOUS_THRESHOLD
                        },
                        "dominant_category": max(avg_predictions, key=avg_predictions.get)
                    }
            except Exception as e2:
                print(f"⚠️ روش جایگزین OpenCV نیز ناموفق بود: {e2}")
            
            if not result:
                raise HTTPException(status_code=500, detail="پردازش گیف با تمام روش‌ها ناموفق بود")
        
        print(f"📊 نتایج گیف:")
        print(f"   دسته غالب: {result.get('dominant_category')}")
        print(f"   امتیاز خام: {result['raw_nsfw_score']:.3f}")
        print(f"   امتیاز نهایی: {result['adjusted_nsfw_score']:.3f}")
        print(f"   نامناسب: {result['is_nsfw']}")
        
        response_data = {
            "DEVIP_Guard": {
                "model": "DEVIP Guard-1",
                "ok": not result["is_nsfw"],
                "channel": "devip.ir",
                "writer": " @NingaCode ",
                "result": {
                    "filename": filename,
                    "type": "gif",
                    "predictions": result["predictions"],
                    "dominant_category": result.get("dominant_category", ""),
                    "raw_nsfw_score": float(result["raw_nsfw_score"]),
                    "adjusted_nsfw_score": float(result["adjusted_nsfw_score"]),
                    "is_nsfw": bool(result["is_nsfw"]),
                    "is_safe": bool(result["is_safe"]),
                    "is_suspicious": bool(result["is_suspicious"]),
                    "veil": {
                        "has_veil": bool(result["veil"]["has_veil"]),
                        "confidence": float(result["veil"]["confidence"]),
                        "dark_ratio": float(result["veil"].get("dark_ratio", 0)),
                        "light_ratio": float(result["veil"].get("light_ratio", 0)),
                        "black_ratio": float(result["veil"].get("black_ratio", 0)),
                        "method": str(result["veil"].get("method", "none"))
                    },
                    "thresholds": {
                        "nsfw": float(result["thresholds"]["nsfw"]),
                        "safe": float(result["thresholds"]["safe"]),
                        "suspicious": float(result["thresholds"]["suspicious"])
                    }
                }
            }
        }
        
        return clean_response(response_data)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ خطا در تشخیص گیف: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink()
            except:
                pass
        gc.collect()


#  تشخیص ویدیو 

@router.post("/classify-video")
async def classify_video(
    video: UploadFile = File(...),
    sample_rate: float = Form(0.1),
    max_frames: int = Form(None),
    detector: DevipGuardDetector = Depends(get_detector)
):
    """
    تشخیص محتوای نامناسب در ویدیو آپلود شده
    
    ویژگی‌ها:
        - دسترسی عمومی - بدون نیاز به احراز هویت
        - پشتیبانی از: MP4, AVI, MOV, MKV, WMV, FLV, WEBM
        - حداکثر حجم: ۱۰۰ مگابایت
    """
    temp_path = None
    try:
        # بررسی فرمت ویدیو
        video_exts = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
        ext = os.path.splitext(video.filename)[1].lower()
        if ext not in video_exts:
            raise HTTPException(
                status_code=415,
                detail=f"فرمت ویدیو پشتیبانی نمی‌شود: {ext}. فرمت‌های مجاز: MP4, AVI, MOV, MKV, WMV, FLV, WEBM"
            )
        
        # ایجاد پوشه آپلود
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # ذخیره فایل موقت
        temp_path = upload_dir / video.filename
        content = await video.read()
        
        if len(content) > 100 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="حجم ویدیو بسیار زیاد است: حداکثر ۱۰۰ مگابایت"
            )
        
        with open(temp_path, "wb") as f:
            f.write(content)
        
        # پردازش ویدیو
        video_result = await detector.predict_video_async(
            str(temp_path),
            sample_rate=sample_rate,
            max_frames=max_frames
        )
        
        if not video_result:
            raise HTTPException(status_code=500, detail="پردازش ویدیو ناموفق بود")
        
        avg_predictions = video_result.get("average", {})
        raw_score = detector._calculate_nsfw_score(avg_predictions)
        
        # تشخیص حجاب در فریم اول
        veil_info = {"has_veil": False, "confidence": 0.0}
        try:
            cap = cv2.VideoCapture(str(temp_path))
            ret, frame = cap.read()
            cap.release()
            if ret:
                temp_frame = temp_path.parent / f"temp_frame_{video.filename}.jpg"
                cv2.imwrite(str(temp_frame), frame)
                veil_info = detector._detect_veil(str(temp_frame))
                if temp_frame.exists():
                    temp_frame.unlink()
        except Exception as e:
            print(f"⚠️ تشخیص حجاب در ویدیو ناموفق: {e}")
        
        # تنظیم امتیاز با توجه به حجاب
        adjusted_score = raw_score
        if veil_info.get("has_veil", False):
            reduction = 0.3 * veil_info.get("confidence", 0.0)
            adjusted_score = max(0.0, raw_score - reduction)
            print(f"🕊️ حجاب در ویدیو: کاهش امتیاز از {raw_score:.3f} به {adjusted_score:.3f}")
        
        # اعمال آستانه‌ها
        is_nsfw = adjusted_score >= detector.NSFW_THRESHOLD
        is_safe = adjusted_score <= detector.SAFE_THRESHOLD
        is_suspicious = detector.SAFE_THRESHOLD < adjusted_score < detector.NSFW_THRESHOLD
        
        print(f"📊 نتایج ویدیو:")
        print(f"   دسته غالب: {max(avg_predictions, key=avg_predictions.get)}")
        print(f"   امتیاز خام: {raw_score:.3f}")
        print(f"   امتیاز نهایی: {adjusted_score:.3f}")
        print(f"   نامناسب: {is_nsfw}")
        
        # ساخت لیست فریم‌ها
        frames_list = []
        for frame in video_result.get("frames", [])[:10]:
            frames_list.append({
                "time": float(frame.get("time", 0)),
                "predictions": {
                    k: float(v) for k, v in frame.get("predictions", {}).items()
                }
            })
        
        response_data = {
            "DEVIP_Guard": {
                "model": "DEVIP Guard-1",
                "ok": not bool(is_nsfw),
                "channel": "devip.ir",
                "writer": " @NingaCode ",
                "result": {
                    "filename": video.filename,
                    "type": "video",
                    "predictions": {k: float(v) for k, v in avg_predictions.items()},
                    "dominant_category": str(max(avg_predictions, key=avg_predictions.get)),
                    "raw_nsfw_score": float(raw_score),
                    "adjusted_nsfw_score": float(adjusted_score),
                    "is_nsfw": bool(is_nsfw),
                    "is_safe": bool(is_safe),
                    "is_suspicious": bool(is_suspicious),
                    "veil": {
                        "has_veil": bool(veil_info.get("has_veil", False)),
                        "confidence": float(veil_info.get("confidence", 0.0)),
                        "dark_ratio": float(veil_info.get("dark_ratio", 0)),
                        "light_ratio": float(veil_info.get("light_ratio", 0)),
                        "black_ratio": float(veil_info.get("black_ratio", 0)),
                        "method": str(veil_info.get("method", "none"))
                    },
                    "frames": frames_list,
                    "metadata": {
                        "total_frames": int(video_result.get("metadata", {}).get("total_frames", 0)),
                        "processed_frames": int(video_result.get("metadata", {}).get("processed_frames", 0)),
                        "fps": float(video_result.get("metadata", {}).get("fps", 0)),
                        "duration": float(video_result.get("metadata", {}).get("duration", 0)),
                        "sample_rate": float(video_result.get("metadata", {}).get("sample_rate", 0)),
                        "resolution": str(video_result.get("metadata", {}).get("resolution", ""))
                    },
                    "thresholds": {
                        "nsfw": float(detector.NSFW_THRESHOLD),
                        "safe": float(detector.SAFE_THRESHOLD),
                        "suspicious": float(detector.SUSPICIOUS_THRESHOLD)
                    }
                }
            }
        }
        
        return clean_response(response_data)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ خطا در ویدیو: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink()
            except:
                pass
        gc.collect()


#  تشخیص از طریق لینک 

@router.post("/classify-url")
async def classify_url(
    request: dict,
    detector: DevipGuardDetector = Depends(get_detector)
):
    """
    تشخیص محتوای نامناسب از طریق لینک
    
    ویژگی‌ها:
        - دسترسی عمومی - بدون نیاز به احراز هویت
        - پشتیبانی از: JPG, PNG, GIF, WEBP, BMP, MP4, AVI, MOV, MKV, WEBM
    """
    temp_file = None
    try:
        url = request.get("url")
        if not url:
            raise HTTPException(status_code=400, detail="لینک الزامی است")
        
        # دانلود فایل
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail="دانلود فایل ناموفق بود"
            )
        
        if len(response.content) > 100 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="حجم فایل بسیار زیاد است: حداکثر ۱۰۰ مگابایت"
            )
        
        # تشخیص نوع فایل
        url_lower = url.lower()
        is_gif = 'gif' in url_lower
        is_video = any(ext in url_lower for ext in ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'])
        
        if is_gif:
            ext = 'gif'
            file_type = 'gif'
        elif is_video:
            ext = 'mp4'
            file_type = 'video'
        else:
            ext = 'jpg'
            file_type = 'image'
        
        # ذخیره فایل موقت
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{ext}')
        temp_file.write(response.content)
        temp_file.close()
        
        result_data = None
        
        # پردازش بر اساس نوع فایل
        if file_type == 'gif':
            gif_result = detector.predict_gif(temp_file.name)
            if gif_result:
                raw_score = detector._calculate_nsfw_score(gif_result)
                veil_info = detector._detect_veil(temp_file.name)
                
                adjusted_score = raw_score
                if veil_info.get("has_veil", False):
                    reduction = 0.3 * veil_info.get("confidence", 0.0)
                    adjusted_score = max(0.0, raw_score - reduction)
                
                result_data = {
                    "predictions": gif_result,
                    "dominant_category": max(gif_result, key=gif_result.get),
                    "raw_nsfw_score": float(raw_score),
                    "adjusted_nsfw_score": float(adjusted_score),
                    "is_nsfw": bool(adjusted_score >= detector.NSFW_THRESHOLD),
                    "is_safe": bool(adjusted_score <= detector.SAFE_THRESHOLD),
                    "is_suspicious": bool(detector.SAFE_THRESHOLD < adjusted_score < detector.NSFW_THRESHOLD),
                    "veil": {
                        "has_veil": bool(veil_info.get("has_veil", False)),
                        "confidence": float(veil_info.get("confidence", 0.0)),
                        "method": str(veil_info.get("method", "none"))
                    },
                    "thresholds": {
                        "nsfw": float(detector.NSFW_THRESHOLD),
                        "safe": float(detector.SAFE_THRESHOLD),
                        "suspicious": float(detector.SUSPICIOUS_THRESHOLD)
                    }
                }
                
        elif file_type == 'video':
            video_result = detector.predict_video(temp_file.name, sample_rate=0.1, max_frames=100)
            if video_result:
                avg_predictions = video_result.get("average", {})
                raw_score = detector._calculate_nsfw_score(avg_predictions)
                
                veil_info = {"has_veil": False, "confidence": 0.0}
                try:
                    cap = cv2.VideoCapture(temp_file.name)
                    ret, frame = cap.read()
                    cap.release()
                    if ret:
                        temp_frame = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                        cv2.imwrite(temp_frame.name, frame)
                        veil_info = detector._detect_veil(temp_frame.name)
                        temp_frame.close()
                        os.unlink(temp_frame.name)
                except:
                    pass
                
                adjusted_score = raw_score
                if veil_info.get("has_veil", False):
                    reduction = 0.3 * veil_info.get("confidence", 0.0)
                    adjusted_score = max(0.0, raw_score - reduction)
                
                result_data = {
                    "predictions": {k: float(v) for k, v in avg_predictions.items()},
                    "dominant_category": max(avg_predictions, key=avg_predictions.get),
                    "raw_nsfw_score": float(raw_score),
                    "adjusted_nsfw_score": float(adjusted_score),
                    "is_nsfw": bool(adjusted_score >= detector.NSFW_THRESHOLD),
                    "is_safe": bool(adjusted_score <= detector.SAFE_THRESHOLD),
                    "is_suspicious": bool(detector.SAFE_THRESHOLD < adjusted_score < detector.NSFW_THRESHOLD),
                    "veil": {
                        "has_veil": bool(veil_info.get("has_veil", False)),
                        "confidence": float(veil_info.get("confidence", 0.0)),
                        "method": str(veil_info.get("method", "none"))
                    },
                    "thresholds": {
                        "nsfw": float(detector.NSFW_THRESHOLD),
                        "safe": float(detector.SAFE_THRESHOLD),
                        "suspicious": float(detector.SUSPICIOUS_THRESHOLD)
                    }
                }
        else:
            result = detector.classify_with_veil(temp_file.name)
            if result:
                result_data = {
                    "predictions": result["predictions"],
                    "dominant_category": result.get("dominant_category", ""),
                    "raw_nsfw_score": float(result["raw_nsfw_score"]),
                    "adjusted_nsfw_score": float(result["adjusted_nsfw_score"]),
                    "is_nsfw": bool(result["is_nsfw"]),
                    "is_safe": bool(result["is_safe"]),
                    "is_suspicious": bool(result["is_suspicious"]),
                    "veil": {
                        "has_veil": bool(result["veil"]["has_veil"]),
                        "confidence": float(result["veil"]["confidence"]),
                        "method": str(result["veil"].get("method", "none"))
                    },
                    "thresholds": {
                        "nsfw": float(result["thresholds"]["nsfw"]),
                        "safe": float(result["thresholds"]["safe"]),
                        "suspicious": float(result["thresholds"]["suspicious"])
                    }
                }
        
        if not result_data:
            raise HTTPException(status_code=500, detail="تشخیص ناموفق بود")
        
        response_data = {
            "DEVIP_Guard": {
                "model": "DEVIP Guard-1",
                "ok": not result_data.get("is_nsfw", False),
                "channel": "devip.ir",
                "writer": " @NingaCode ",
                "result": {
                    "filename": url.split('/')[-1],
                    "type": file_type,
                    **result_data
                }
            }
        }
        
        return clean_response(response_data)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ خطا در لینک: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except:
                pass
        gc.collect()


#  بررسی سلامت 

@router.get("/health")
async def health_check(
    detector: DevipGuardDetector = Depends(get_detector)
):
    """
    بررسی سلامت سرویس - عمومی (بدون نیاز به احراز هویت)
    
    Returns:
        وضعیت سرویس و آمار
    """
    stats = detector.get_stats()
    
    response_data = {
        "DEVIP_Guard": {
            "model": "DEVIP Guard-1",
            "ok": True,
            "channel": "devip.ir",
            "writer": " @NingaCode ",
            "status": "healthy",
            "model_loaded": True,
            "inference_count": int(stats.get("inference_count", 0)),
            "error_count": int(stats.get("error_count", 0)),
            "device": str(stats.get("device", "cpu")),
            "image_dim": int(stats.get("image_dim", 224)),
            "uptime_seconds": float(stats.get("uptime_seconds", 0)),
            "providers": [str(p) for p in stats.get("provider", ["CPUExecutionProvider"])],
            "thresholds": {
                "nsfw": float(stats.get("thresholds", {}).get("nsfw", 0.85)),
                "safe": float(stats.get("thresholds", {}).get("safe", 0.25)),
                "suspicious": float(stats.get("thresholds", {}).get("suspicious", 0.60))
            }
        }
    }
    
    return clean_response(response_data)


#  پاکسازی کش 

@router.post("/cleanup")
async def cleanup_cache(
    detector: DevipGuardDetector = Depends(get_detector)
):
    """
    پاکسازی حافظه کش
    
    ویژگی‌ها:
        - دسترسی عمومی
        - پاکسازی منابع و حافظه
    """
    detector.cleanup()
    response_data = {
        "DEVIP_Guard": {
            "model": "DEVIP Guard-1",
            "ok": True,
            "channel": "devip.ir",
            "writer": " @NingaCode ",
            "status": "success",
            "message": "حافظه کش پاکسازی شد"
        }
    }
    
    return clean_response(response_data)