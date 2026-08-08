# -*- coding: utf-8 -*-
"""
DEVIP Guard - رابط خط فرمان
"""

import os
import sys
import json
import argparse
from pathlib import Path

# اضافه کردن مسیر پروژه به sys.path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from devip_guard.core.config import Config
from devip_guard.core.detector import DevipGuardDetector


def main():
    """
    نقطه ورود اصلی رابط خط فرمان
    
    این تابع پارامترهای خط فرمان را پردازش کرده و تشخیص را اجرا می‌کند
    """
    parser = argparse.ArgumentParser(
        description="DEVIP Guard - رابط خط فرمان تشخیص محتوای نامناسب",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
مثال‌ها:
  python -m devip_guard.cli.main --input image.jpg
  python -m devip_guard.cli.main --input image.gif --format json
  python -m devip_guard.cli.main --input video.mp4 --sample-rate 0.05 --max-frames 200
  python -m devip_guard.cli.main --input image.jpg --output result.json
        """
    )
    
    # پارامترهای اجباری
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="مسیر فایل تصویر، گیف یا ویدیو"
    )
    
    # گزینه‌های مدل
    parser.add_argument(
        "-t", "--type",
        choices=["d", "m2", "i3"],
        default="d",
        help="نوع مدل: d (پیش‌فرض), m2, i3"
    )
    parser.add_argument(
        "-m", "--model",
        help="مسیر سفارشی مدل"
    )
    parser.add_argument(
        "-d", "--device",
        choices=["cpu", "cuda", "tensorrt", "dml", "coreml", "openvino"],
        default="cpu",
        help="دستگاه اجرا (پیش‌فرض: cpu)"
    )
    
    # گزینه‌های ویدیو
    parser.add_argument(
        "-s", "--sample-rate",
        type=float,
        default=0.1,
        help="نرخ نمونه‌برداری ویدیو (۰ تا ۱)، پیش‌فرض: ۰.۱"
    )
    parser.add_argument(
        "-f", "--max-frames",
        type=int,
        default=100,
        help="حداکثر فریم‌های ویدیو برای پردازش، پیش‌فرض: ۱۰۰"
    )
    
    # گزینه‌های خروجی
    parser.add_argument(
        "--format",
        choices=["json", "pretty", "simple"],
        default="pretty",
        help="فرمت خروجی (پیش‌فرض: pretty)"
    )
    parser.add_argument(
        "-o", "--output",
        help="ذخیره خروجی در فایل"
    )
    
    # سایر گزینه‌ها
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="غیرفعال کردن خروجی رنگی"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="نمایش خروجی مفصل"
    )
    
    args = parser.parse_args()
    
    # بررسی وجود فایل ورودی
    if not os.path.exists(args.input):
        print(f"❌ خطا: فایل یافت نشد: {args.input}")
        sys.exit(1)
    
    try:
        # تنظیمات
        config = Config()
        config.model_type = args.type
        config.model_path = args.model
        config.device = args.device
        
        # راه‌اندازی تشخیص‌دهنده
        if args.verbose:
            print("🔧 در حال راه‌اندازی DEVIP Guard...")
        
        detector = DevipGuardDetector(config)
        
        if args.verbose:
            print(f"✅ مدل بارگذاری شد: {args.type}")
            print(f"   دستگاه: {args.device}")
            print(f"   ابعاد تصویر: {detector.image_dim}x{detector.image_dim}")
            print()
        
        # پردازش فایل بر اساس نوع
        file_ext = Path(args.input).suffix.lower()
        video_exts = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
        gif_ext = ['.gif']
        
        if file_ext in video_exts:
            if args.verbose:
                print(f"🎬 پردازش ویدیو: {args.input}")
            result = detector.predict_video(
                args.input,
                sample_rate=args.sample_rate,
                max_frames=args.max_frames
            )
        elif file_ext in gif_ext:
            if args.verbose:
                print(f"🎞️ پردازش گیف: {args.input}")
            result = detector.predict_gif(args.input)
        else:
            if args.verbose:
                print(f"🖼️ پردازش تصویر: {args.input}")
            result = detector.predict_image(args.input)
        
        if not result:
            print("❌ پردازش ناموفق بود")
            sys.exit(1)
        
        # فرمت‌دهی خروجی
        output = format_output(result, args.format, args.no_color)
        
        # ذخیره یا چاپ
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                if args.format == "json":
                    json.dump(result, f, indent=2)
                else:
                    f.write(output)
            print(f"✅ ذخیره شد در: {args.output}")
        else:
            print(output)
    
    except KeyboardInterrupt:
        print("\n⚠️ توسط کاربر متوقف شد")
        sys.exit(1)
    except Exception as e:
        print(f"❌ خطا: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def format_output(result: dict, format_type: str, no_color: bool) -> str:
    """
    فرمت‌دهی خروجی برای نمایش
    
    Args:
        result: دیکشنری نتیجه تشخیص
        format_type: نوع فرمت (json, pretty, simple)
        no_color: غیرفعال کردن رنگ‌ها
    
    Returns:
        رشته فرمت‌شده برای نمایش
    """
    if format_type == "json":
        return json.dumps(result, indent=2)
    
    if format_type == "simple":
        if "average" in result:
            return json.dumps(result.get("average", {}), indent=2)
        return json.dumps(result, indent=2)
    
    # خروجی زیبا با رنگ
    colors = {
        'green': '\033[92m' if not no_color else '',
        'yellow': '\033[93m' if not no_color else '',
        'red': '\033[91m' if not no_color else '',
        'blue': '\033[94m' if not no_color else '',
        'purple': '\033[95m' if not no_color else '',
        'reset': '\033[0m' if not no_color else ''
    }
    
    lines = []
    lines.append("=" * 50)
    lines.append("DEVIP Guard - نتیجه تشخیص")
    lines.append("=" * 50)
    
    if "average" in result:
        # نتیجه ویدیو
        avg = result.get("average", {})
        meta = result.get("metadata", {})
        
        lines.append(f"📹 تحلیل ویدیو")
        lines.append(f"   تعداد کل فریم‌ها: {meta.get('total_frames', 0)}")
        lines.append(f"   فریم‌های پردازش شده: {meta.get('processed_frames', 0)}")
        lines.append(f"   مدت زمان: {meta.get('duration', 0):.2f} ثانیه")
        lines.append("")
        lines.append("میانگین پیش‌بینی‌ها:")
        for cat, prob in avg.items():
            color = get_color(cat, colors)
            bar = "█" * int(prob * 40)
            lines.append(f"   {color}{cat:10}{colors['reset']} {prob*100:5.1f}% {bar}")
    
    elif "predictions" in result:
        # نتیجه تصویر با امتیاز
        preds = result.get("predictions", {})
        score = result.get("nsfw_score", 0)
        is_nsfw = result.get("is_nsfw", False)
        
        lines.append(f"📄 فایل: {result.get('filename', 'ناشناخته')}")
        lines.append(f"📊 امتیاز NSFW: {score*100:.1f}% {'⚠️ نامناسب' if is_nsfw else '✅ ایمن'}")
        lines.append("")
        lines.append("پیش‌بینی‌ها:")
        for cat, prob in preds.items():
            color = get_color(cat, colors)
            bar = "█" * int(prob * 40)
            lines.append(f"   {color}{cat:10}{colors['reset']} {prob*100:5.1f}% {bar}")
    
    else:
        # نتیجه ساده
        for cat, prob in result.items():
            color = get_color(cat, colors)
            bar = "█" * int(prob * 40)
            lines.append(f"   {color}{cat:10}{colors['reset']} {prob*100:5.1f}% {bar}")
    
    lines.append("=" * 50)
    return "\n".join(lines)


def get_color(category: str, colors: dict) -> str:
    """
    دریافت رنگ مربوط به هر دسته‌بندی
    
    Args:
        category: نام دسته‌بندی
        colors: دیکشنری رنگ‌ها
    
    Returns:
        کد رنگ ANSI
    """
    color_map = {
        'neutral': colors['green'],
        'sexy': colors['yellow'],
        'porn': colors['red'],
        'hentai': colors['purple'],
        'drawing': colors['blue']
    }
    return color_map.get(category, colors['reset'])


if __name__ == "__main__":
    main()