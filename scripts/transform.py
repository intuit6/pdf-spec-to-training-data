#!/usr/bin/env python3
"""
数据转换脚本 - 将已解析的 JSON 数据转换为训练格式

用法：
  python scripts/transform.py --input <已解析的JSON文件或目录> --output <输出目录>

示例：
  python scripts/transform.py --input ./parsed/ --output ./dataset/ --format jsonl
"""

import argparse
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src import (
    DataTransformer,
    DatasetBuilder,
    TextChunk,
    load_config,
    ensure_dir,
    setup_logging
)
import logging

logger = logging.getLogger("transform")


def load_parsed_data(json_path: Path) -> list:
    """加载已解析的 JSON 数据"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if isinstance(data, dict) and "pages" in data:
        return data["pages"]
    elif isinstance(data, list):
        return data
    else:
        raise ValueError(f"意外的 JSON 结构: {json_path}")


def pages_to_chunks(pages_data: list, transformer: DataTransformer) -> list:
    """将页面数据转换为 TextChunk 对象"""
    chunks = []

    for page_data in pages_data:
        # 重建文本
        text = page_data.get("text", "")

        # 使用 transformer 清洗和分块
        cleaned_text = transformer.cleaner.clean(text)
        lines = cleaned_text.split('\n')
        filtered_lines = transformer.hf_remover.remove(lines)
        final_text = '\n'.join(filtered_lines)

        # 分块
        page_chunks = transformer.chunker.chunk_text(
            final_text,
            page_num=page_data.get("page_num"),
            source_file=page_data.get("source_file", "")
        )

        chunks.extend(page_chunks)

    return chunks


def main():
    parser = argparse.ArgumentParser(
        description="数据转换工具 - 将已解析的 PDF JSON 转换为训练格式"
    )

    parser.add_argument(
        "--input", "-i",
        required=True,
        help="输入：已解析的 JSON 文件或包含这些文件的目录"
    )
    parser.add_argument(
        "--output", "-o",
        default="./output/dataset",
        help="输出目录（默认: ./output/dataset）"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["jsonl", "json", "csv", "txt", "parquet"],
        default="jsonl",
        help="输出格式（默认: jsonl）"
    )
    parser.add_argument(
        "--chunk-strategy",
        choices=["fixed", "paragraph", "chapter", "page", "none"],
        default="paragraph",
        help="分块策略（默认: paragraph）"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="分块大小（字符，默认: 1000）"
    )
    parser.add_argument(
        "--dataset-format",
        choices=["text", "qa", "instruction"],
        default="text",
        help="数据集格式类型（默认: text）"
    )
    parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        help="递归搜索输入目录"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细输出"
    )

    args = parser.parse_args()

    # 日志
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(level=log_level, console=True)
    logger = logging.getLogger("transform")

    # 确保输出目录
    output_dir = Path(args.output)
    ensure_dir(output_dir)

    # 查找输入文件
    input_path = Path(args.input)

    if input_path.is_file():
        json_files = [input_path]
    elif input_path.is_dir():
        pattern = "**/*.json" if args.recursive else "*.json"
        json_files = list(input_path.glob(pattern))
    else:
        logger.error(f"输入路径不存在: {input_path}")
        return 1

    if not json_files:
        logger.error("未找到 JSON 文件")
        return 1

    logger.info(f"找到 {len(json_files)} 个 JSON 文件")

    # 初始化组件
    cleaner = TextCleaner()
    hf_remover = HeaderFooterRemover()
    chunker = TextChunker(
        strategy=args.chunk_strategy,
        max_chunk_size=args.chunk_size,
        overlap=100
    )
    transformer = DataTransformer(cleaner, chunker, hf_remover)
    dataset_builder = DatasetBuilder(output_format=args.format)

    # 处理每个文件
    all_datasets = []

    for json_file in json_files:
        try:
            logger.info(f"处理: {json_file.name}")

            # 加载数据
            pages_data = load_parsed_data(json_file)
            logger.debug(f"  加载 {len(pages_data)} 页")

            # 转换为 chunks
            chunks = pages_to_chunks(pages_data, transformer)
            logger.info(f"  生成 {len(chunks)} 个文本块")

            # 构建数据集
            dataset = dataset_builder.build_from_chunks(
                chunks,
                format_type=args.dataset_format
            )

            # 保存
            prefix = json_file.stem
            output_file = dataset_builder.save(dataset, output_dir, prefix)
            logger.info(f"  ✓ 保存: {output_file.name}")

            all_datasets.append(output_file)

        except Exception as e:
            logger.error(f"  ✗ 失败: {e}", exc_info=args.verbose)

    logger.info("=" * 50)
    logger.info(f"转换完成！处理了 {len(all_datasets)} 个文件")
    logger.info(f"输出目录: {output_dir}")

    return 0


if __name__ == "__main__":
    import logging
    sys.exit(main())
