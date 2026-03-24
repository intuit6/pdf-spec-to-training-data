#!/usr/bin/env python3
"""
数据集生成脚本 - 完整的 PDF 到训练数据转换流程

用法：
  python scripts/generate_dataset.py --config <配置文件路径>

示例：
  python scripts/generate_dataset.py --config config/config.yaml
"""

import argparse
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.pdf_parser import PDFParser, list_pdf_files
from src.data_transformer import DataTransformer, TextCleaner, TextChunker, HeaderFooterRemover
from src.dataset_builder import DatasetBuilder
from src.utils import load_config, ensure_dir, setup_logging
import logging

logger = logging.getLogger("dataset_generator")


def process_pdf_file(
    pdf_path: Path,
    parser: PDFParser,
    transformer: DataTransformer,
    dataset_builder: DatasetBuilder,
    config: Dict[str, Any],
    output_dir: Path
) -> Optional[Path]:
    """处理单个 PDF 文件并生成数据集"""

    logger.info(f"处理 PDF: {pdf_path.name}")

    try:
        # 1. 解析 PDF
        metadata, pages = parser.parse(pdf_path)

        logger.info(f"  解析完成: {len(pages)} 页, {sum(len(p.tables) for p in pages)} 个表格")

        # 2. 转换数据（清洗、分块）
        chunks = transformer.transform_pages(
            pages,
            include_metadata=True,
            min_text_length=config.get("filtering", {}).get("min_text_length", 10)
        )

        logger.info(f"  生成 {len(chunks)} 个文本块")

        # 3. 合并表格（如果启用）
        if config.get("extraction", {}).get("extract_tables", True):
            tables_by_page = {}
            for page in pages:
                if page.tables:
                    tables_by_page[page.page_num] = page.tables

            if tables_by_page:
                chunks = transformer.merge_with_tables(chunks, tables_by_page)
                logger.info(f"  合并了表格数据")

        # 4. 构建数据集
        dataset_format = config.get("dataset", {}).get("format", "text")
        dataset = dataset_builder.build_from_chunks(
            chunks,
            format_type=dataset_format,
            dataset_config=config.get("dataset", {})
        )

        logger.info(f"  构建数据集: {len(dataset)} 条记录")

        # 5. 保存数据集
        output_format = config.get("output", {}).get("format", "jsonl")
        dataset_builder.output_format = output_format

        prefix = pdf_path.stem
        output_file = dataset_builder.save(
            dataset,
            output_dir,
            filename_prefix=prefix
        )

        logger.info(f"  ✓ 保存到: {output_file}")

        # 6. 保存统计信息
        stats = {
            "source_file": pdf_path.name,
            "pages_count": len(pages),
            "tables_count": sum(len(p.tables) for p in pages),
            "chunks_count": len(chunks),
            "dataset_records": len(dataset),
            "total_chars": sum(len(chunk.content) for chunk in chunks),
            "output_file": str(output_file.name)
        }

        stats_file = output_dir / f"{prefix}_stats.json"
        import json
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

        return output_file

    except Exception as e:
        logger.error(f"处理失败: {e}", exc_info=True)
        return None


def main():
    parser = argparse.ArgumentParser(
        description="PDF 规范转训练数据 - 完整处理流程",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
完整流程：
  1. 解析 PDF（提取文本、表格）
  2. 清洗和分块处理
  3. 合并结构化数据
  4. 转换为训练格式
  5. 保存数据集和统计信息

输出格式：
  - jsonl: 每行一个 JSON 记录（推荐用于大语言模型训练）
  - json: 单一 JSON 文件
  - csv: 表格格式（适用于结构化数据）
  - txt: 纯文本（每记录间有分隔符）
  - parquet: 列式存储（高效，支持压缩）
        """
    )

    parser.add_argument(
        "--config", "-c",
        required=True,
        help="配置文件路径（如 config/config.yaml）"
    )
    parser.add_argument(
        "--input", "-i",
        help="覆盖配置文件中的输入路径"
    )
    parser.add_argument(
        "--output", "-o",
        help="覆盖配置文件中的输出路径"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["jsonl", "json", "csv", "txt", "parquet"],
        help="覆盖配置文件中的输出格式"
    )
    parser.add_argument(
        "--workers", "-w",
        type=int,
        help="并行处理进程数"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细输出（DEBUG 级别日志）"
    )

    args = parser.parse_args()

    # 配置日志
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(level=log_level, console=True, log_file="./logs/dataset_generator.log")

    logger = logging.getLogger("main")

    # 加载配置
    try:
        config = load_config(args.config)
        logger.info(f"加载配置: {args.config}")
    except Exception as e:
        logger.error(f"加载配置失败: {e}")
        return 1

    # 覆盖配置（如果命令行参数提供）
    if args.input:
        config["input"]["path"] = args.input
    if args.output:
        config["output"]["path"] = args.output
    if args.format:
        config["output"]["format"] = args.format
    if args.workers:
        config["performance"]["workers"] = args.workers

    # 确保目录存在
    input_path = Path(config["input"]["path"])
    output_dir = Path(config["output"]["path"])
    ensure_dir(output_dir)
    ensure_dir("./logs")

    logger.info(f"输入: {input_path}")
    logger.info(f"输出: {output_dir}")
    logger.info(f"格式: {config['output']['format']}")

    # 查找 PDF 文件
    pdf_files = list_pdf_files(
        input_path,
        recursive=config["input"].get("recursive", False),
        extensions=config["input"].get("extensions", [".pdf"])
    )

    if not pdf_files:
        logger.error("未找到 PDF 文件，退出")
        return 1

    logger.info(f"找到 {len(pdf_files)} 个 PDF 文件")

    # 初始化组件
    parser = PDFParser(
        parser=config.get("advanced", {}).get("parser", "pdfplumber"),
        ocr_enabled=config.get("extraction", {}).get("ocr", {}).get("enabled", False),
        ocr_languages=config.get("extraction", {}).get("ocr", {}).get("languages", "chi_sim+eng")
    )

    cleaner = TextCleaner(
        normalize_whitespace=config.get("filtering", {}).get("text_cleaning", {}).get("normalize_whitespace", True),
        remove_control_chars=config.get("filtering", {}).get("text_cleaning", {}).get("remove_control_chars", True),
        normalize_punctuation=config.get("filtering", {}).get("text_cleaning", {}).get("normalize_punctuation", True),
        remove_patterns=config.get("filtering", {}).get("text_cleaning", {}).get("remove_patterns", [])
    )

    hf_remover = HeaderFooterRemover(
        keywords=config.get("filtering", {}).get("remove_headers_footers", {}).get("keywords", ["第", "页", "Page"]),
        margin_ratio=config.get("filtering", {}).get("remove_headers_footers", {}).get("margin_ratio", 0.15)
    )

    chunker = TextChunker(
        strategy=config["output"].get("chunk_strategy", "paragraph"),
        max_chunk_size=config["output"].get("max_chunk_size", 1000),
        overlap=config["output"].get("chunk_overlap", 100),
        chapter_patterns=config.get("structuring", {}).get("detect_headings", {}).get("patterns", [])
    )

    transformer = DataTransformer(
        cleaner=cleaner,
        chunker=chunker,
        header_footer_remover=hf_remover
    )

    dataset_builder = DatasetBuilder(
        output_format=config["output"]["format"],
        add_special_tokens=config["dataset"].get("add_special_tokens", False),
        special_tokens=config["dataset"].get("special_tokens", {})
    )

    # 批量处理
    successful = 0
    failed = []
    output_files = []

    for pdf_file in pdf_files:
        output_file = process_pdf_file(
            pdf_file,
            parser,
            transformer,
            dataset_builder,
            config,
            output_dir
        )
        if output_file:
            successful += 1
            output_files.append(output_file)
        else:
            failed.append(pdf_file.name)

    # 汇总统计
    logger.info("=" * 60)
    logger.info("数据集生成完成！")
    logger.info(f"成功处理: {successful}/{len(pdf_files)}")
    logger.info(f"输出目录: {output_dir}")

    if failed:
        logger.warning(f"失败文件 ({len(failed)}):")
        for name in failed:
            logger.warning(f"  - {name}")

    # 如果有多个输出文件，创建合并版本
    if len(output_files) > 1 and config.get("dataset", {}).get("merge_outputs", True):
        logger.info("合并数据集...")
        merged = dataset_builder.merge_datasets(
            output_files,
            output_dir,
            deduplicate=True
        )
        logger.info(f"合并数据集: {merged}")

    logger.info("全部完成！")
    return 0


if __name__ == "__main__":
    import logging
    sys.exit(main())
