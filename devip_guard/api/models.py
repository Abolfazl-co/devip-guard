# -*- coding: utf-8 -*-
"""
DEVIP Guard - مدل‌های API (Pydantic V2)
"""

from typing import Dict, Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict


class ClassifyRequest(BaseModel):
    """مدل درخواست برای تشخیص تصویر"""
    image: bytes = Field(..., description="داده تصویر به صورت بایت")


class ClassifyResponse(BaseModel):
    """مدل پاسخ برای تشخیص تصویر"""
    filename: str = Field(..., description="نام اصلی فایل")
    predictions: Dict[str, float] = Field(..., description="احتمالات دسته‌بندی‌ها")
    nsfw_score: float = Field(..., description="امتیاز NSFW (۰ تا ۱)")
    is_nsfw: bool = Field(..., description="آیا محتوا نامناسب است")
    is_safe: bool = Field(..., description="آیا محتوا ایمن است")
    is_suspicious: bool = Field(..., description="آیا محتوا مشکوک است")
    
    # استفاده از ConfigDict به جای کلاس Config
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "filename": "image.jpg",
                "predictions": {
                    "neutral": 0.85,
                    "sexy": 0.08,
                    "porn": 0.04,
                    "hentai": 0.02,
                    "drawing": 0.01
                },
                "nsfw_score": 0.14,
                "is_nsfw": False,
                "is_safe": True,
                "is_suspicious": False
            }
        }
    )


class ClassifyURLRequest(BaseModel):
    """مدل درخواست برای تشخیص از طریق لینک"""
    url: str = Field(
        ..., 
        description="لینک تصویر",
        json_schema_extra={"example": "https://example.com/image.jpg"}
    )


class VideoClassifyRequest(BaseModel):
    """مدل درخواست برای تشخیص ویدیو"""
    sample_rate: float = Field(
        0.1, 
        description="نرخ نمونه‌برداری فریم (۰ تا ۱)", 
        ge=0.01, 
        le=1.0
    )
    max_frames: Optional[int] = Field(
        None, 
        description="حداکثر فریم‌های قابل پردازش", 
        ge=1, 
        le=1000
    )


class FrameScore(BaseModel):
    """مدل امتیاز فریم"""
    time: float = Field(..., description="زمان به ثانیه")
    predictions: Dict[str, float] = Field(..., description="احتمالات دسته‌بندی‌ها")


class VideoMetadata(BaseModel):
    """مدل متادیتای ویدیو"""
    total_frames: int = Field(..., description="تعداد کل فریم‌های ویدیو")
    processed_frames: int = Field(..., description="تعداد فریم‌های پردازش شده")
    fps: float = Field(..., description="فریم بر ثانیه")
    duration: float = Field(..., description="مدت زمان ویدیو به ثانیه")
    sample_rate: float = Field(..., description="نرخ نمونه‌برداری فریم")
    resolution: Optional[str] = Field(None, description="رزولوشن ویدیو")


class VideoClassifyResponse(BaseModel):
    """مدل پاسخ برای تشخیص ویدیو"""
    average: Dict[str, float] = Field(..., description="میانگین پیش‌بینی‌ها")
    frames: List[FrameScore] = Field(..., description="امتیازات هر فریم")
    metadata: VideoMetadata = Field(..., description="متادیتای ویدیو")


class HealthResponse(BaseModel):
    """مدل پاسخ بررسی سلامت"""
    status: str = Field(..., description="وضعیت سرویس")
    model_loaded: bool = Field(..., description="آیا مدل بارگذاری شده است")
    inference_count: int = Field(..., description="تعداد کل تشخیص‌ها")
    error_count: int = Field(..., description="تعداد کل خطاها")
    device: str = Field(..., description="دستگاه اجرا")
    image_dim: int = Field(..., description="ابعاد ورودی مدل")
    uptime_seconds: float = Field(..., description="مدت زمان اجرای سرویس به ثانیه")
    providers: List[str] = Field(..., description="ارائه‌دهندگان ONNX")


class ErrorResponse(BaseModel):
    """مدل پاسخ خطا"""
    error: str = Field(..., description="پیام خطا")
    detail: Optional[str] = Field(None, description="جزئیات خطا")
    status_code: int = Field(..., description="کد وضعیت HTTP")