"""
AMAS - Advanced Multi-Agent Intelligence System
Setup script for installation and development
"""

from pathlib import Path

from setuptools import find_packages, setup

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = (
    readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
)

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = requirements_path.read_text(encoding="utf-8").strip().split("\n")
    requirements = [
        req.strip() for req in requirements if req.strip() and not req.startswith("#")
    ]

# Development requirements
dev_requirements = [
    "pytest>=7.4.3",
    "pytest-asyncio>=0.21.1",
    "pytest-cov>=4.1.0",
    "black>=23.11.0",
    "flake8>=6.1.0",
    "mypy>=1.7.1",
    "pre-commit>=3.5.0",
    "sphinx>=7.2.6",
    "sphinx-rtd-theme>=1.3.0",
]

setup(
    name="amas",
    version="1.0.0",
    author="AMAS Development Team",
    author_email="team@amas.ai",
    description="Advanced Multi-Agent Intelligence System - Sophisticated autonomous AI system for offline operation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
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
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "docs": ["sphinx>=7.2.6", "sphinx-rtd-theme>=1.3.0"],
        "gpu": ["torch[cu121]", "faiss-gpu"],
        "cpu": ["torch", "faiss-cpu"],
    },
    entry_points={
        "console_scripts": [
            "amas=amas.main:main",
            "amas-cli=amas.cli:main",
            "amas-setup=amas.setup:main",
        ],
    },
    include_package_data=True,
    package_data={
        "amas": [
            "config/*.yaml",
            "config/*.json",
            "assets/*",
        ],
    },
    zip_safe=False,
    project_urls={
        "Source": "https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System",
        "Documentation": "https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System/docs",
    },
)
