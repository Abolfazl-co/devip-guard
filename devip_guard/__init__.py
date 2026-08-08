# -*- coding: utf-8 -*-
"""
DEVIP Guard - Professional NSFW Content Detection Library

A lightweight, high-performance NSFW content detection library
for images, GIFs, and videos using ONNX Runtime.

Example:
    >>> from devip_guard import DevipGuardDetector
    >>> detector = DevipGuardDetector()
    >>> result = detector.predict_image("image.jpg")
    >>> print(result)
    {'neutral': 0.85, 'sexy': 0.08, 'porn': 0.04, 'hentai': 0.02, 'drawing': 0.01}
"""

from .core.detector import DevipGuardDetector
from .core.config import Config, CATEGORIES
from .api.app import create_app, run_server

__version__ = "1.0.0"
__author__ = "DEVIP"
__all__ = [
    'DevipGuardDetector',
    'Config',
    'CATEGORIES',
    'create_app',
    'run_server'
]