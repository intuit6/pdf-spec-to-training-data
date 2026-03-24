#!/usr/bin/env python3
"""
PDF 解析脚本

用法：
  python scripts/parse.py --input <pdf文件或目录> [--output <输出目录>] [--config <配置文件>]

示例：
  python scripts/parse.py --input ./docs/ --output ./parsed/
  python scripts/parse.py --input document.pdf --output ./output/
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径，以便导入 src 包
script_file = Path(__file__).resolve()
project_root = script_file.parent.parent
sys.path.insert(0, str(project_root))

from src.pdf_parser import PDFParser, list_pdf_files
from src.utils import load_config, ensure_dir, setup_logging


def main():
    parser = argparse.ArgumentParser(
        description="PDF 规范解析工具 - 提取文本、表格等信息",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --input ./pdfs/ --output ./json/
  %(prog)s --input spec.pdf --output ./out/ --config config.yaml
  %(prog)s --input ./pdfs/ --output ./out/ --recursive
        """
    )

    parser.add_argument(
        "--input", "-i",
        required=True,
        help="输入 PDF 文件或目录路径"
    )
    parser.add_argument(
        "--output", "-o",
        default="./output/parsed",
        help="输出目录（默认: ./output/parsed）"
    )
    parser.add_argument(
        "--config", "-c",
        help="配置文件路径（如 config/config.yaml）"
    )
    parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        help="递归搜索子目录（当输入为目录时）"
    )
    parser.add_argument(
        "--parser",
        choices=["pdfplumber", "pymupdf"],
        default="pdfplumber",
        help="PDF 解析器（默认: pdfplumber）"
    )
    parser.add_argument(
        "--ocr",
        action="store_true",
        help="启用 OCR（用于扫描件）"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细输出"
    )

    args = parser.parse_args()

    # 配置日志
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(level=log_level, console=True)

    logger = logging.getLogger("parse")

    # 加载配置（如果提供）
    config = {}
    if args.config:
        try:
            config = load_config(args.config)
            logger.info(f"已加载配置文件: {args.config}")
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return 1

    # 确保输出目录存在
    output_dir = Path(args.output)
    ensure_dir(output_dir)

    # 查找 PDF 文件
    pdf_files = list_pdf_files(
        args.input,
        recursive=args.recursive or config.get("input", {}).get("recursive", False)
    )

    if not pdf_files:
        logger.error(f"未找到 PDF 文件: {args.input}")
        return 1

    logger.info(f"找到 {len(pdf_files)} 个 PDF 文件")

    # 初始化解析器
    parser_obj = PDFParser(
        parser=args.parser or config.get("extraction", {}).get("parser", "pdfplumber"),
        ocr_enabled=args.ocr or config.get("extraction", {}).get("ocr", {}).get("enabled", False),
        ocr_languages=config.get("extraction", {}).get("ocr", {}).get("languages", "chi_sim+eng")
    )

    # 处理每个 PDF
    total_pages = 0
    total_tables = 0
    successful = 0
    failed = []

    for pdf_file in pdf_files:
        try:
            logger.info(f"处理: {pdf_file.name}")

            # 解析 PDF
            metadata, pages = parser_obj.parse(pdf_file)

            total_pages += len(pages)
            total_tables += sum(len(page.tables) for page in pages)

            # 构建输出数据结构
            result = {
                "metadata": {
                    "filename": metadata.filename,
                    "total_pages": metadata.total_pages,
                    "title": metadata.title,
                    "author": metadata.author,
                    "creation_date": metadata.creation_date,
                    "custom": metadata.custom_metadata
                },
                "pages": []
            }

            for page in pages:
                page_data = {
                    "page_num": page.page_num,
                    "text": page.text,
                    "width": page.width,
                    "height": page.height,
                    "tables": page.tables,
                    "images_count": len(page.images)
                }
                result["pages"].append(page_data)

            # 保存到文件
            output_file = output_dir / f"{pdf_file.stem}_parsed.json"
            import json
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            logger.info(f"  ✓ 保存到: {output_file.name}")
            logger.info(f"  页数: {len(pages)}, 表格: {sum(len(p.tables) for p in pages)}")
            successful += 1

        except Exception as e:
            logger.error(f"  ✗ 处理失败: {e}")
            failed.append((pdf_file.name, str(e)))

    # 输出统计
    logger.info("=" * 50)
    logger.info("处理完成！")
    logger.info(f"成功: {successful}/{len(pdf_files)}")
    logger.info(f"总页数: {total_pages}")
    logger.info(f"总表格: {total_tables}")

    if failed:
        logger.warning(f"失败: {len(failed)}")
        for name, error in failed:
            logger.warning(f"  - {name}: {error}")

    return 0


if __name__ == "__main__":
    import logging
    sys.exit(main())
