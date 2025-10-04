#!/usr/bin/env python3
"""
AMAS - Advanced Multi-Agent Intelligence System
Setup configuration for pip installation
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

# Read requirements
def read_requirements(filename):
    """Read requirements from file"""
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Core requirements
install_requires = read_requirements('requirements.txt')

# Development requirements
dev_requires = [
    'pytest>=7.4.0',
    'pytest-cov>=4.1.0',
    'pytest-asyncio>=0.21.0',
    'black>=23.0.0',
    'isort>=5.12.0',
    'flake8>=6.0.0',
    'mypy>=1.5.0',
    'bandit>=1.7.5',
    'safety>=2.3.5',
    'pre-commit>=3.3.0',
    'locust>=2.15.0',
]

# Documentation requirements
docs_requires = [
    'sphinx>=7.0.0',
    'sphinx-rtd-theme>=1.3.0',
    'myst-parser>=2.0.0',
    'autodoc-pydantic>=2.0.0',
]

setup(
    name="amas",
    version="1.0.0",
    author="AMAS Team",
    author_email="team@amas.ai",
    description="Advanced Multi-Agent Intelligence System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=install_requires,
    extras_require={
        "dev": dev_requires,
        "docs": docs_requires,
        "all": dev_requires + docs_requires,
    },
    entry_points={
        "console_scripts": [
            "amas=amas.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "amas": ["config/*.yaml", "config/*.yml"],
    },
)