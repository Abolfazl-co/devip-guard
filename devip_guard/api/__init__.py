# -*- coding: utf-8 -*-
"""API module - FastAPI application and routes (Public)"""

from .app import create_app, run_server
from .routes import router
from .models import (
    ClassifyRequest,
    ClassifyResponse,
    ClassifyURLRequest,
    HealthResponse,
    ErrorResponse
)

__all__ = [
    'create_app',
    'run_server',
    'router',
    'ClassifyRequest',
    'ClassifyResponse',
    'ClassifyURLRequest',
    'HealthResponse',
    'ErrorResponse'
]