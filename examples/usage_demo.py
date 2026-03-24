#!/usr/bin/env python3
"""
使用示例：PDF 规范转训练数据

这个脚本展示了如何以编程方式使用本项目的各个组件。
"""

import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src import (
    PDFParser,
    DataTransformer,
    DatasetBuilder,
    TextCleaner,
    TextChunker,
    HeaderFooterRemover,
    ensure_dir
)
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("example")


def example_basic_parsing():
    """示例 1：基础 PDF 解析"""
    print("\n" + "="*60)
    print("示例 1：基础 PDF 解析")
    print("="*60)

    # 初始化解析器
    parser = PDFParser(parser="pdfplumber")

    # 解析文件
    pdf_path = "pdfs/example.pdf"  # 替换为你的文件路径
    try:
        metadata, pages = parser.parse(pdf_path)

        print(f"文档: {metadata.filename}")
        print(f"总页数: {metadata.total_pages}")
        print(f"标题: {metadata.title or '无'}")
        print(f"作者: {metadata.author or '未知'}")

        print(f"\n前 3 页内容预览:")
        for i, page in enumerate(pages[:3], 1):
            preview = page.text[:200] + "..." if len(page.text) > 200 else page.text
            print(f"\n第 {page.page_num} 页 ({len(page.text)} 字符):")
            print(f"  {preview}")
            if page.tables:
                print(f"  发现 {len(page.tables)} 个表格")

    except FileNotFoundError:
        print(f"文件不存在: {pdf_path}")
        print("请先将 PDF 文件放入 pdfs/ 目录")


def example_custom_transformation():
    """示例 2：自定义数据转换"""
    print("\n" + "="*60)
    print("示例 2：自定义数据转换")
    print("="*60)

    # 自定义清洗规则
    cleaner = TextCleaner(
        normalize_whitespace=True,
        remove_control_chars=True,
        remove_patterns=[
            r"页码\s*\d+",           # 移除页码
            r"电子版.*pdf",           # 移除电子版声明
            r"©\s*\d{4}",            # 移除版权声明
        ]
    )

    # 自定义分块策略
    chunker = TextChunker(
        strategy="chapter",         # 按章节分块
        max_chunk_size=1500,        # 最大 1500 字符
        overlap=100,                # 重叠 100 字符
        chapter_patterns=[
            r'^第[零一二三四五六七八九十百千万\d]+章',
            r'^\d+\.\d+\s+',
            r'^[A-Z]\.\s+'
        ]
    )

    # 页眉页脚移除器
    hf_remover = HeaderFooterRemover(
        keywords=["第", "页", "Page", "Copyright", "©", "密级"],
        margin_ratio=0.1            # 顶部和底部 10% 视为边距
    )

    # 组装转换器
    transformer = DataTransformer(cleaner, chunker, hf_remover)

    print("转换器配置:")
    print(f"  分块策略: {chunker.strategy}")
    print(f"  最大块大小: {chunker.max_chunk_size}")
    print(f"  启用页眉页脚移除: {hf_remover.keywords}")


def example_build_dataset():
    """示例 3：构建完整数据集"""
    print("\n" + "="*60)
    print("示例 3：构建完整数据集")
    print("="*60)

    output_dir = Path("./output/example")
    ensure_dir(output_dir)

    # 初始化组件
    parser = PDFParser()
    cleaner = TextCleaner()
    hf_remover = HeaderFooterRemover()
    chunker = TextChunker(strategy="paragraph", max_chunk_size=1000)
    transformer = DataTransformer(cleaner, chunker, hf_remover)
    builder = DatasetBuilder(
        output_format="jsonl",
        add_special_tokens=False
    )

    pdf_path = "pdfs/example.pdf"
    try:
        # 1. 解析
        print("步骤 1: 解析 PDF...")
        metadata, pages = parser.parse(pdf_path)
        print(f"  解析了 {len(pages)} 页")

        # 2. 转换
        print("步骤 2: 数据转换...")
        chunks = transformer.transform_pages(pages, min_text_length=10)
        print(f"  生成了 {len(chunks)} 个文本块")

        # 3. 合并表格
        print("步骤 3: 合并表格数据...")
        tables_by_page = {}
        for page in pages:
            if page.tables:
                tables_by_page[page.page_num] = page.tables

        if tables_by_page:
            chunks = transformer.merge_with_tables(chunks, tables_by_page)
            print(f"  合并了 {sum(len(t) for t in tables_by_page.values())} 个表格")

        # 4. 构建数据集
        print("步骤 4: 构建数据集...")
        dataset = builder.build_from_chunks(chunks, format_type="text")
        print(f"  数据集大小: {len(dataset)} 条记录")

        # 5. 保存
        print("步骤 5: 保存...")
        output_file = builder.save(dataset, output_dir, "example")
        print(f"  保存到: {output_file}")

        # 6. 查看示例
        print("\n数据集示例（第 1 条记录）:")
        if dataset:
            example = dataset[0]
            print(f"  ID: {example.get('id', 'N/A')}")
            print(f"  内容长度: {len(example.get('text', ''))} 字符")
            print(f"  前 150 字符: {example.get('text', '')[:150]}...")
            print(f"  元数据: {example.get('metadata', {})}")

    except FileNotFoundError:
        print(f"文件不存在: {pdf_path}")
        print("请先将 PDF 文件放入 pdfs/ 目录")


def example_qa_format():
    """示例 4：生成问答对格式"""
    print("\n" + "="*60)
    print("示例 4：生成问答对格式")
    print("="*60)

    # 初始化组件
    parser = PDFParser()
    cleaner = TextCleaner()
    chunker = TextChunker(strategy="paragraph", max_chunk_size=800)
    transformer = DataTransformer(cleaner, chunker)
    builder = DatasetBuilder(output_format="jsonl")

    pdf_path = "pdfs/example.pdf"
    try:
        # 解析并转换
        metadata, pages = parser.parse(pdf_path)
        chunks = transformer.transform_pages(pages)

        # 构建问答对格式
        qa_dataset = builder.build_from_chunks(
            chunks,
            format_type="qa",
            dataset_config={
                "question_templates": [
                    "请总结以下内容：",
                    "请提取以下文档的关键信息：",
                    "根据以下内容回答问题："
                ]
            }
        )

        print(f"生成了 {len(qa_dataset)} 条问答对")

        # 显示示例
        if qa_dataset:
            example = qa_dataset[0]
            print("\n问答对示例:")
            print(f"指令: {example.get('instruction', '')[:100]}...")
            print(f"输出: {example.get('output', '')[:200]}...")

    except FileNotFoundError:
        print(f"文件不存在: {pdf_path}")


def example_merge_datasets():
    """示例 5：合并多个数据集"""
    print("\n" + "="*60)
    print("示例 5：合并多个数据集")
    print("="*60)

    # 假设我们已经有多个数据集文件
    dataset_files = [
        "output/dataset/doc1.jsonl",
        "output/dataset/doc2.jsonl",
        "output/dataset/doc3.jsonl"
    ]

    builder = DatasetBuilder(output_format="jsonl")

    existing_files = [f for f in dataset_files if Path(f).exists()]

    if len(existing_files) >= 2:
        print(f"合并 {len(existing_files)} 个数据集文件...")
        merged = builder.merge_datasets(
            [Path(f) for f in existing_files],
            output_path=Path("./output/merged"),
            deduplicate=True
        )
        print(f"合并完成: {merged}")

        # 检查去重效果
        import json
        with open(merged, 'r', encoding='utf-8') as f:
            records = [json.loads(line) for line in f]
        print(f"合并后记录数: {len(records)}")
    else:
        print("需要至少 2 个已存在的数据集文件才能演示合并功能")
        print("请先运行完整流程生成多个数据集")


def main():
    print("PDF 规范转训练数据 - 使用示例")
    print("="*60)

    examples = [
        ("基础解析", example_basic_parsing),
        ("自定义转换", example_custom_transformation),
        ("构建数据集", example_build_dataset),
        ("问答对格式", example_qa_format),
        ("合并数据集", example_merge_datasets),
    ]

    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n❌ 示例 '{name}' 执行出错: {e}")
            import traceback
            if logging.getLogger().level <= logging.DEBUG:
                traceback.print_exc()

    print("\n" + "="*60)
    print("示例运行完成！")
    print("="*60)
    print("""
下一步：

1. 根据你的 PDF 文档类型调整配置
   - 技术规范：使用 chapter 分块，启用表格提取
   - 产品手册：使用 paragraph 分块，保持文本连贯
   - 扫描件：启用 OCR，安装 Tesseract 中文包

2. 运行完整流程
   python scripts/generate_dataset.py --config config/config.yaml

3. 根据需要调整输出格式
   - LLM 训练：使用 jsonl 格式
   - 数据分析：使用 csv 或 parquet 格式
   - 人工审核：使用 txt 格式

4. 查看统计数据
   检查生成的 *_stats.json 文件了解处理质量
    """)

    return 0


if __name__ == "__main__":
    sys.exit(main())
