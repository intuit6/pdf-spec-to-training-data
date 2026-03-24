"""PDF 解析器模块

负责从 PDF 文件中提取文本、表格、图片等资源。
支持多种 PDF 类型（文字型、扫描型）和提取策略。
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class PageContent:
    """页面内容数据结构"""
    page_num: int
    text: str
    tables: List[Dict[str, Any]] = field(default_factory=list)
    images: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    width: float = 0
    height: float = 0


@dataclass
class PDFMetadata:
    """PDF 文档元数据"""
    filename: str
    total_pages: int
    title: Optional[str] = None
    author: Optional[str] = None
    creator: Optional[str] = None
    producer: Optional[str] = None
    creation_date: Optional[str] = None
    modification_date: Optional[str] = None
    custom_metadata: Dict[str, Any] = field(default_factory=dict)


class PDFParser:
    """PDF 解析器

    支持多种解析后端，提供统一的接口来提取：
    - 文本（保留或丢弃布局）
    - 表格（有线表、无线表）
    - 图片
    - 元数据
    """

    def __init__(
        self,
        parser: str = "pdfplumber",
        ocr_enabled: bool = False,
        ocr_languages: str = "chi_sim+eng",
        ocr_engine: str = "tesseract"
    ):
        """初始化 PDF 解析器

        Args:
            parser: 解析器类型，可选 "pdfplumber", "pymupdf"
            ocr_enabled: 是否启用 OCR（用于扫描件）
            ocr_languages: OCR 语言，如 "chi_sim+eng"
            ocr_engine: OCR 引擎，"tesseract" 或 "paddle"
        """
        self.parser_type = parser
        self.ocr_enabled = ocr_enabled
        self.ocr_languages = ocr_languages
        self.ocr_engine = ocr_engine

        # 检查可用性
        if parser == "pdfplumber" and not PDFPLUMBER_AVAILABLE:
            raise ImportError("pdfplumber 未安装，请运行: pip install pdfplumber")
        if parser == "pymupdf" and not PYMUPDF_AVAILABLE:
            raise ImportError("pymupdf 未安装，请运行: pip install pymupdf")

        if ocr_enabled:
            self._init_ocr()

    def _init_ocr(self):
        """初始化 OCR 引擎"""
        if self.ocr_engine == "tesseract":
            try:
                import pytesseract
                self.tesseract_cmd = pytesseract.pytesseract.tesseract_cmd
                logger.info("Tesseract OCR 初始化成功")
            except ImportError:
                logger.error("pytesseract 未安装，请运行: pip install pytesseract")
                raise
        elif self.ocr_engine == "paddle":
            try:
                from paddleocr import PaddleOCR
                self.paddle_ocr = PaddleOCR(use_angle_cls=True, lang='ch')
                logger.info("PaddleOCR 初始化成功")
            except ImportError:
                logger.error("paddleocr 未安装，请运行: pip install paddleocr")
                raise

    def parse(self, file_path: Union[str, Path]) -> Tuple[PDFMetadata, List[PageContent]]:
        """解析 PDF 文件

        Args:
            file_path: PDF 文件路径

        Returns:
            (元数据, 页面内容列表)
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        logger.info(f"开始解析 PDF: {file_path.name}")

        if self.parser_type == "pdfplumber":
            return self._parse_with_pdfplumber(file_path)
        elif self.parser_type == "pymupdf":
            return self._parse_with_pymupdf(file_path)
        else:
            raise ValueError(f"不支持的解析器类型: {self.parser_type}")

    def _parse_with_pdfplumber(self, file_path: Path) -> Tuple[PDFMetadata, List[PageContent]]:
        """使用 pdfplumber 解析"""
        metadata = self._extract_metadata_pdfplumber(file_path)
        pages_content = []

        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                logger.debug(f"解析第 {page_num} 页")

                # 提取文本
                text = self._extract_text_pdfplumber(page)

                # 提取表格
                tables = self._extract_tables_pdfplumber(page)

                # 提取图片（如果启用）
                images = []
                if self.ocr_enabled:
                    images = self._extract_images_pdfplumber(page, file_path.parent)

                page_content = PageContent(
                    page_num=page_num,
                    text=text,
                    tables=tables,
                    images=images,
                    metadata={"parser": "pdfplumber"},
                    width=page.width,
                    height=page.height
                )
                pages_content.append(page_content)

        logger.info(f"解析完成，共 {len(pages_content)} 页")
        return metadata, pages_content

    def _extract_text_pdfplumber(self, page) -> str:
        """提取页面文本"""
        try:
            # 尝试保留布局
            text = page.extract_text(
                x_tolerance=3,
                y_tolerance=3,
                keep_blank_chars=True,
                use_text_flow=True,
                horizontal_ltr=True,
                vertical_ttb=True
            )
            return text if text else ""
        except Exception as e:
            logger.warning(f"提取文本失败: {e}")
            return ""

    def _extract_tables_pdfplumber(self, page) -> List[Dict[str, Any]]:
        """提取表格"""
        tables = []

        try:
            # 自动检测表格类型
            extracted_tables = page.extract_tables({
                "vertical_strategy": "lines",  # 或 "text"
                "horizontal_strategy": "lines",
                "explicit_vertical_lines": [],
                "explicit_horizontal_lines": [],
                "snap_tolerance": 3,
                "snap_x_tolerance": 3,
                "snap_y_tolerance": 3,
                "join_tolerance": 3,
                "edge_min_length": 3,
            })

            for idx, table in enumerate(extracted_tables):
                if table and len(table) >= 2 and len(table[0]) >= 2:
                    table_data = {
                        "table_id": idx + 1,
                        "page_num": page.page_number,
                        "data": table,
                        "bbox": table.bbox if hasattr(table, 'bbox') else None,
                        "rows": len(table),
                        "cols": len(table[0]) if table else 0
                    }
                    tables.append(table_data)

        except Exception as e:
            logger.warning(f"提取表格失败: {e}")

        return tables

    def _extract_images_pdfplumber(self, page, output_dir: Path) -> List[Dict[str, Any]]:
        """提取图片并可选进行 OCR"""
        images = []
        # TODO: 实现图片提取和 OCR
        return images

    def _extract_metadata_pdfplumber(self, file_path: Path) -> PDFMetadata:
        """提取 PDF 元数据"""
        try:
            with pdfplumber.open(file_path) as pdf:
                doc_metadata = pdf.metadata or {}
                return PDFMetadata(
                    filename=file_path.name,
                    total_pages=len(pdf.pages),
                    title=doc_metadata.get("Title"),
                    author=doc_metadata.get("Author"),
                    creator=doc_metadata.get("Creator"),
                    producer=doc_metadata.get("Producer"),
                    creation_date=doc_metadata.get("CreationDate"),
                    modification_date=doc_metadata.get("ModDate"),
                    custom_metadata={k: v for k, v in doc_metadata.items()
                                   if k not in ["Title", "Author", "Creator", "Producer", "CreationDate", "ModDate"]}
                )
        except Exception as e:
            logger.warning(f"提取元数据失败: {e}")
            return PDFMetadata(filename=file_path.name, total_pages=0)

    def _parse_with_pymupdf(self, file_path: Path) -> Tuple[PDFMetadata, List[PageContent]]:
        """使用 PyMuPDF 解析"""
        metadata = self._extract_metadata_pymupdf(file_path)
        pages_content = []

        doc = fitz.open(file_path)

        for page_num in range(len(doc)):
            page = doc[page_num]
            logger.debug(f"解析第 {page_num + 1} 页")

            # 提取文本
            text = page.get_text("text")  # 或 "dict", "html", "json"

            # 提取表格（需要额外处理，pymupdf 对表格支持较弱）
            tables = []  # TODO: 实现表格提取

            # 提取图片
            images = []
            if self.ocr_enabled:
                images = self._extract_images_pymupdf(page, file_path.parent)

            page_content = PageContent(
                page_num=page_num + 1,
                text=text,
                tables=tables,
                images=images,
                metadata={"parser": "pymupdf"},
                width=page.rect.width,
                height=page.rect.height
            )
            pages_content.append(page_content)

        doc.close()
        logger.info(f"解析完成，共 {len(pages_content)} 页")
        return metadata, pages_content

    def _extract_metadata_pymupdf(self, file_path: Path) -> PDFMetadata:
        """提取 PyMuPDF 元数据"""
        try:
            doc = fitz.open(file_path)
            meta = doc.metadata
            doc.close()

            return PDFMetadata(
                filename=file_path.name,
                total_pages=doc.page_count,
                title=meta.get("title"),
                author=meta.get("author"),
                creator=meta.get("creator"),
                producer=meta.get("producer"),
                creation_date=meta.get("creationDate"),
                modification_date=meta.get("modDate"),
                custom_metadata={k: v for k, v in meta.items()
                               if k not in ["title", "author", "creator", "producer", "creationDate", "modDate"]}
            )
        except Exception as e:
            logger.warning(f"提取元数据失败: {e}")
            return PDFMetadata(filename=file_path.name, total_pages=0)

    def _extract_images_pymupdf(self, page, output_dir: Path):
        """提取图片（PyMuPDF）"""
        # TODO: 实现
        return []

    def extract_text_only(self, file_path: Union[str, Path]) -> str:
        """快速提取全文文本（无需页面级细分）"""
        metadata, pages = self.parse(file_path)
        return "\n".join([page.text for page in pages])

    def get_statistics(self, pages_content: List[PageContent]) -> Dict[str, Any]:
        """获取解析统计信息"""
        total_chars = sum(len(page.text) for page in pages_content)
        total_tables = sum(len(page.tables) for page in pages_content)
        total_images = sum(len(page.images) for page in pages_content)

        return {
            "total_pages": len(pages_content),
            "total_characters": total_chars,
            "avg_chars_per_page": total_chars / len(pages_content) if pages_content else 0,
            "total_tables": total_tables,
            "avg_tables_per_page": total_tables / len(pages_content) if pages_content else 0,
            "total_images": total_images,
            "has_content": total_chars > 0
        }


def list_pdf_files(
    input_path: Union[str, Path],
    recursive: bool = False,
    extensions: List[str] = [".pdf"]
) -> List[Path]:
    """列出所有 PDF 文件

    Args:
        input_path: 输入路径（文件或目录）
        recursive: 是否递归搜索子目录
        extensions: 文件扩展名列表

    Returns:
        文件路径列表
    """
    input_path = Path(input_path)
    pdf_files = []

    if input_path.is_file():
        if input_path.suffix.lower() in extensions:
            pdf_files.append(input_path)
    elif input_path.is_dir():
        pattern = "**/*" if recursive else "*"
        for ext in extensions:
            pdf_files.extend(input_path.glob(f"{pattern}{ext}"))
            pdf_files.extend(input_path.glob(f"{pattern}{ext.upper()}"))

    # 排序确保稳定性
    pdf_files = sorted(set(pdf_files))

    logger.info(f"找到 {len(pdf_files)} 个 PDF 文件")
    return pdf_files
