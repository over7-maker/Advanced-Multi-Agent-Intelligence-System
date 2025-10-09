#!/usr/bin/env python3
"""
AMAS - Advanced Multi-Agent Intelligence System
Setup script for development and installation
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements = []
with open("requirements.txt", "r") as f:
    requirements = [
        line.strip() for line in f if line.strip() and not line.startswith("#")
    ]

setup(
    name="amas",
    version="1.0.0",
    description="Advanced Multi-Agent Intelligence System - Sophisticated autonomous AI system for offline operation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AMAS Development Team",
    author_email="team@amas.ai",
    url="https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
            "pre-commit>=3.5.0",
        ],
        "gpu": [
            "torch[cu121]>=2.2.0,<3.0",
            "faiss-gpu>=1.7.4",
        ],
    },
    entry_points={
        "console_scripts": [
            "amas=amas.cli:main",
            "amas-setup=amas.setup:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
        "Topic :: Security",
    ],
    keywords="ai multi-agent intelligence autonomous offline llm vector-search knowledge-graph security",
    project_urls={
        "Homepage": "https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System",
        "Documentation": "https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/docs",
        "Repository": "https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System",
        "Issues": "https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/issues",
    },
)
