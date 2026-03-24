"""PDF 规范转训练数据 - 主模块

提供统一的命令行接口和高级封装。
"""

__version__ = "1.0.0"
__author__ = "OpenClaw Agent"

from .pdf_parser import PDFParser, PageContent, PDFMetadata, list_pdf_files
from .data_transformer import (
    DataTransformer,
    TextChunker,
    TextCleaner,
    HeaderFooterRemover,
    TextChunk
)
from .dataset_builder import DatasetBuilder
from .utils import load_config, ensure_dir, setup_logging

__all__ = [
    "PDFParser",
    "PageContent",
    "PDFMetadata",
    "list_pdf_files",
    "DataTransformer",
    "TextChunker",
    "TextCleaner",
    "HeaderFooterRemover",
    "TextChunk",
    "DatasetBuilder",
    "load_config",
    "ensure_dir",
    "setup_logging"
]
