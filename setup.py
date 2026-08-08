# -*- coding: utf-8 -*-
"""
DEVIP Guard - Package Setup
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="devip-guard",
    version="1.0.0",
    author="Abolfazl Zarei",
    author_email="za1386za470@gmail.com",
    description="Professional NSFW content detection for images, GIFs, and videos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AbolfazlZarei-dev/devip-guard",
    project_urls={
        "Website": "https://devip.ir",
        "Personal Site": "https://abolfazlzarei.sbs",
        "Source Code": "https://github.com/AbolfazlZarei-dev/devip-guard",
        "Bug Reports": "https://github.com/AbolfazlZarei-dev/devip-guard/issues",
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn>=0.20.0",
        "python-multipart>=0.0.6",
        "Jinja2>=3.0.0",
        "Pillow>=9.0.0",
        "numpy>=1.21.0",
        "opencv-python>=4.5.0",
        "onnxruntime>=1.12.0",
        "requests>=2.28.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
        ],
        "gpu": [
            "onnxruntime-gpu>=1.12.0",
        ],
        "all": [
            "onnxruntime-gpu>=1.12.0",
            "pytest>=7.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "devip-guard=devip_guard.cli.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)