"""
安装配置模块
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取 README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="pdf-spec-to-training-data",
    version="1.0.0",
    author="OpenClaw Agent",
    description="将 PDF 规范文档转换为可用于训练的数据集",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/intuit6/pdf-spec-to-training-data",
    project_urls={
        "Bug Tracker": "https://github.com/intuit6/pdf-spec-to-training-data/issues",
        "Documentation": "https://github.com/intuit6/pdf-spec-to-training-data#readme",
        "Source Code": "https://github.com/intuit6/pdf-spec-to-training-data",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "pdfplumber>=0.10.3",
        "PyPDF2>=3.0.1",
        "pymupdf>=1.23.8",
        "pandas>=2.0.3",
        "numpy>=1.24.3",
        "pillow>=10.0.1",
        "pyyaml>=6.0",
        "tqdm>=4.66.1",
    ],
    extras_require={
        "ocr": [
            "pytesseract>=0.3.10",
            "opencv-python>=4.8.0",
        ],
        "paddle": [
            "paddleocr>=2.7.0",
        ],
        "dev": [
            "pytest>=7.4.2",
            "pytest-cov>=4.1.0",
            "black>=23.9.1",
            "flake8>=6.1.0",
            "mypy>=1.5.1",
            "isort>=5.12.0",
            "bandit>=1.7.5",
        ],
        "all": [
            "pytesseract>=0.3.10",
            "opencv-python>=4.8.0",
            "paddleocr>=2.7.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "pdf2dataset=scripts.generate_dataset:main",
            "pdfparse=scripts.parse:main",
            "pdftransform=scripts.transform:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: General",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    keywords="pdf training dataset llm machine-learning nlp data-preprocessing document-parsing table-extraction",
    license="MIT",
)
