# 详细使用文档

## 目录

- [概述](#概述)
- [安装](#安装)
- [快速开始](#快速开始)
- [命令行工具](#命令行工具)
- [Python API](#python-api)
- [配置详解](#配置详解)
- [高级功能](#高级功能)
- [最佳实践](#最佳实践)
- [故障排除](#故障排除)
- [FAQ](#faq)

## 概述

### 什么是 PDF 规范转训练数据？

这是一个专门用于将 PDF 规范文档转换为机器学习训练数据的工具。支持：

- **文字型 PDF**：直接提取文本
- **扫描型 PDF**：OCR 文字识别
- **表格提取**：有线表（lattice）和无线表（stream）
- **结构化输出**：JSONL、CSV、TXT、Parquet 多种格式
- **智能分块**：按章节、段落或固定长度分块
- **批量处理**：支持目录批量处理

### 适用场景

- **大型语言模型训练**：将技术文档转换为问答对或指令格式
- **RAG 知识库构建**：将规范文档转换为向量数据库可 ingest 的格式
- **数据标注**：提取规范化文本用于人工标注
- **版本对比**：提取不同版本规范进行差异分析
- **内容分析**：统计术语、提取结构化信息

## 安装

### 前置要求

- Python 3.8+
- pip 21.0+

### 完整安装（推荐）

```bash
# 1. 克隆或下载项目
cd pdf-spec-to-training-data

# 2. 运行安装脚本
python install_and_run.py
```

### 最小安装

```bash
# 仅安装核心依赖（无 OCR）
pip install -r requirements.txt
pip install -e .
```

### 安装 OCR 支持

#### Tesseract（推荐，跨平台）

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-chi-sim  # 简体中文
sudo apt-get install tesseract-ocr-chi-tra  # 繁体中文
sudo apt-get install tesseract-ocr-eng     # 英文

# macOS
brew install tesseract
brew install tesseract-lang

# Windows
# 从 https://github.com/UB-Mannheim/tesseract/wiki 下载安装器
# 安装时选中中文语言包
```

配置环境变量（如果 Tesseract 不在 PATH 中）：

```bash
# Linux/macOS
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata/

# Windows
# 在系统环境变量中添加 TESSDATA_PREFIX
```

#### PaddleOCR（中文效果更好，但占用资源多）

```bash
pip install paddleocr
# 首次运行会自动下载模型（约 100MB）
```

## 快速开始

### 5 分钟上手

```bash
# 1. 准备 PDF
mkdir -p pdfs
cp your_spec.pdf pdfs/

# 2. 编辑配置（可选）
# 编辑 config/config.yaml 调整参数

# 3. 运行处理
python scripts/generate_dataset.py --config config/config.yaml

# 4. 查看结果
ls output/dataset/
```

### 一条命令搞定

```bash
python scripts/generate_dataset.py \
  --config config/config.yaml \
  --verbose
```

## 命令行工具

### 1. pdfparse - 解析 PDF

**用途：** 仅提取 PDF 内容，保存为中间 JSON 格式

```bash
# 解析单个文件
python scripts/parse.py --input document.pdf --output parsed/

# 解析目录（递归）
python scripts/parse.py --input ./pdfs/ --output parsed/ --recursive

# 使用特定解析器
python scripts/parse.py --input spec.pdf --output out/ --parser pymupdf

# 启用 OCR（扫描件）
python scripts/parse.py --input scanned.pdf --output out/ --ocr --verbose
```

**输出文件：** `{文件名}_parsed.json`

结构：
```json
{
  "metadata": {
    "filename": "spec.pdf",
    "total_pages": 50,
    "title": "技术规范"
  },
  "pages": [
    {
      "page_num": 1,
      "text": "页面文本内容...",
      "width": 612,
      "height": 792,
      "tables": [...],
      "images_count": 0
    }
  ]
}
```

### 2. generate_dataset - 生成数据集（推荐）

**用途：** 完整流程，从 PDF 直接生成训练数据集

```bash
# 基本用法（使用默认配置）
python scripts/generate_dataset.py --config config/config.yaml

# 指定输入目录
python scripts/generate_dataset.py \
  --config config/config.yaml \
  --input ./my_pdfs/

# 指定输出格式
python scripts/generate_dataset.py \
  --config config/config.yaml \
  --format parquet

# 调整并行数
python scripts/generate_dataset.py \
  --config config/config.yaml \
  --workers 8

# 详细信息输出
python scripts/generate_dataset.py \
  --config config/config.yaml \
  --verbose
```

### 3. transform - 转换已解析数据

**用途：** 将已解析的 JSON 数据转换为不同格式

```bash
# 转换目录中的所有 JSON
python scripts/transform.py \
  --input ./parsed/ \
  --output ./dataset/ \
  --format jsonl

# 递归处理子目录
python scripts/transform.py \
  --input ./parsed/ \
  --output ./dataset/ \
  --recursive \
  --format csv

# 使用固定长度分块
python scripts/transform.py \
  --input ./parsed/ \
  --output ./dataset/ \
  --chunk-strategy fixed \
  --chunk-size 2000

# 生成问答对格式
python scripts/transform.py \
  --input ./parsed/ \
  --output ./dataset/ \
  --dataset-format qa
```

## Python API

### 基础用法

```python
from src import PDFParser, DataTransformer, DatasetBuilder
from pathlib import Path

# 1. 解析 PDF
parser = PDFParser(parser="pdfplumber")
metadata, pages = parser.parse("spec.pdf")
print(f"解析了 {len(pages)} 页")

# 2. 转换数据
transformer = DataTransformer()
chunks = transformer.transform_pages(pages, min_text_length=10)
print(f"生成了 {len(chunks)} 个文本块")

# 3. 构建数据集
builder = DatasetBuilder(output_format="jsonl")
dataset = builder.build_from_chunks(chunks, format_type="text")

# 4. 保存
output_file = builder.save(dataset, "./output", "my_dataset")
print(f"保存到: {output_file}")
```

### 高级 API

```python
from src import PDFParser, TextCleaner, TextChunker, HeaderFooterRemover, DataTransformer, DatasetBuilder

# 自定义清洗规则
cleaner = TextCleaner(
    normalize_whitespace=True,
    remove_patterns=[
        r"页码\s*\d+",
        r"电子版.*pdf"
    ]
)

# 自定义分块策略
chunker = TextChunker(
    strategy="chapter",
    max_chunk_size=1500,
    overlap=100,
    chapter_patterns=[
        r'^第[零一二三四五六七八九十\d]+章',
        r'^\d+\.\d+\s+'
    ]
)

# 页眉页脚移除
hf_remover = HeaderFooterRemover(
    keywords=["第", "页", "Copyright", "©", "密级"],
    margin_ratio=0.15
)

# 组装
transformer = DataTransformer(cleaner, chunker, hf_remover)
builder = DatasetBuilder(output_format="jsonl")

# 处理
metadata, pages = parser.parse("spec.pdf")
chunks = transformer.transform_pages(pages)
chunks = transformer.merge_with_tables(chunks, {p.page_num: p.tables for p in pages if p.tables})
dataset = builder.build_from_chunks(chunks, format_type="text")
builder.save(dataset, "./output", "custom")
```

### 批量处理

```python
from src import list_pdf_files, PDFParser, DataTransformer, DatasetBuilder
import logging

logging.basicConfig(level=logging.INFO)

# 初始化
parser = PDFParser()
transformer = DataTransformer()
builder = DatasetBuilder(output_format="jsonl")

# 批量查找
pdf_files = list_pdf_files("./pdfs/", recursive=True)

# 批量处理
for pdf_file in pdf_files:
    try:
        metadata, pages = parser.parse(pdf_file)
        chunks = transformer.transform_pages(pages)
        dataset = builder.build_from_chunks(chunks)
        builder.save(dataset, "./output", pdf_file.stem)
    except Exception as e:
        print(f"处理 {pdf_file.name} 失败: {e}")
```

## 配置详解

### 配置文件结构

`config/config.yaml` 完整选项说明：

```yaml
# ==================== 输入配置 ====================
input:
  path: "./pdfs/"              # 输入路径（文件或目录）
  recursive: true              # 是否递归搜索子目录
  extensions: [".pdf"]         # 文件扩展名列表
  page_range: null            # 指定页面范围 [0, 5]（可选）
  filename_pattern: null      # 文件名正则过滤（可选）

# ==================== 输出配置 ====================
output:
  path: "./output/"            # 输出目录
  format: "jsonl"              # 格式: jsonl, json, csv, txt, parquet
  split_by_page: false         # 是否按页拆分
  chunk_strategy: "paragraph"  # 分块策略: fixed, paragraph, chapter, page, none
  max_chunk_size: 1000         # 最大块字符数
  chunk_overlap: 100           # 块重叠字符数
  filename_prefix: "dataset"   # 输出文件名前缀

# ==================== 提取配置 ====================
extraction:
  extract_text: true           # 是否提取文本
  extract_tables: true         # 是否提取表格

  table:
    strategy: "auto"           # 表格检测策略: auto, lattice, stream
    edge_tol: 5                # 表格边缘容差（像素）
    min_size: [2, 2]           # 最小表格尺寸 [行, 列]

  extract_images: false        # 是否提取图片
  ocr:
    enabled: false             # 启用 OCR（扫描件）
    languages: "chi_sim+eng"   # OCR 语言
    engine: "tesseract"        # OCR 引擎: tesseract, paddle

  preserve_layout:
    enabled: true              # 保留排版
    keep_blank_lines: true    # 保留空行
    indent_handling: "preserve"  # 缩进处理

# ==================== 过滤配置 ====================
filtering:
  min_text_length: 10         # 最小文本长度
  max_text_length: 0          # 最大文本长度（0=无限制）

  remove_headers_footers:
    enabled: true              # 移除页眉页脚
    keywords: ["第", "页", "Page", "Copyright"]  # 页眉页脚关键词
    margin_ratio: 0.15         # 边距比例（页眉页脚可能出现的区域）

  remove_duplicates:
    enabled: true              # 去重
    similarity_threshold: 0.95 # 相似度阈值（Jaccard）

  text_cleaning:
    normalize_whitespace: true # 规范化空白
    remove_control_chars: true # 移除控制字符
    normalize_punctuation: true # 规范化标点
    remove_patterns: []        # 正则删除模式列表

# ==================== 结构化解析 ====================
structuring:
  detect_headings:
    enabled: true              # 检测章节标题
    patterns:                  # 标题识别正则
      - "^第[\\d一二三四五六七八九十百千]+章\\s+.+"
      - "^\\d+\\.\\d+\\s+.+"
    level_inference: "auto"    # 级别推断

  detect_lists:
    enabled: true
    markers: ["•", "◎", "○", "▪"]  # 列表标记

  extract_metadata:
    enabled: true
    patterns:                  # 从文本提取元数据
      title: "^(.*?规范|.*?标准)"
      version: "版本[：:]\s*([A-Za-z0-9\\.-]+)"

# ==================== 数据集构建 ====================
dataset:
  format: "text"               # 数据集格式: text, qa, instruction
  add_special_tokens: false    # 添加 BOS/EOS 标记

  special_tokens:
    bos: "<s>"
    eos: "</s>"
    sep: "<sep>"

  qa_generation:
    auto_generate_questions: false  # 自动生成问题
    question_templates:             # 问题模板
      - "什么是{entity}？"
      - "{entity}的作用是什么？"

  instruction:
    templates:
      - "请阅读以下技术规范，{task}："
    task_types: ["summarize", "explain", "list"]

# ==================== 日志配置 ====================
logging:
  level: "INFO"                # DEBUG, INFO, WARNING, ERROR
  file: "./logs/app.log"
  console: true

# ==================== 性能配置 ====================
performance:
  workers: 4                   # 并行处理进程数（CPU 核心数）
  batch_size: 10               # 批处理大小
  memory_limit: 0              # 内存限制（MB，0=无限制）

# ==================== 高级选项 ====================
advanced:
  parser: "pdfplumber"         # 解析器: pdfplumber, pymupdf
  table_coordinate_system: "original"
  keep_coordinates: false
  debug: false                 # 调试模式
```

## 高级功能

### 1. 差异化处理不同 PDF 类型

**方案：** 使用不同的配置文件

```bash
# 处理技术规范（注重表格和章节）
python scripts/generate_dataset.py --config config/technical_spec.yaml

# 处理产品手册（注重文本连贯性）
python scripts/generate_dataset.py --config config/product_manual.yaml

# 处理扫描件（启用 OCR）
python scripts/generate_dataset.py --config config/scanned_docs.yaml
```

**技术规范配置示例** (`config/technical_spec.yaml`):

```yaml
input:
  path: "./technical_specs/"
  recursive: true

extraction:
  extract_tables: true
  table:
    strategy: "lattice"        # 有线表

filtering:
  remove_headers_footers: true
  min_text_length: 20

output:
  chunk_strategy: "chapter"    # 按章节分块，保持结构
  max_chunk_size: 2000

dataset:
  format: "qa"                 # 生成问答对
  qa_generation:
    auto_generate_questions: true
```

### 2. 多格式输出

```bash
# 同时输出多种格式（运行多次或修改脚本）

# JSONL（用于 LLM 训练）
python scripts/generate_dataset.py --config config.yaml

# Parquet（用于大数据处理）
python scripts/gtransform.py --input parsed/ --output out/ --format parquet

# CSV（用于 Excel 分析）
python scripts/transform.py --input parsed/ --output out/ --format csv
```

### 3. 增量处理

**场景：** 有新 PDF 文件需要加入已有数据集

```bash
# 1. 仅解析新文件
python scripts/parse.py --input new_pdfs/ --output parsed_new/

# 2. 转换新数据
python scripts/transform.py --input parsed_new/ --output dataset_new/ --format jsonl

# 3. 合并数据集
python -c "
from src.dataset_builder import DatasetBuilder
builder = DatasetBuilder('jsonl')
merged = builder.merge_datasets(
    ['output/dataset/old.jsonl', 'output/dataset_new/new.jsonl'],
    Path('output/final'),
    deduplicate=True
)
print(f'合并完成: {merged}')
"
```

### 4. 自定义输出格式

```python
# 在 src/dataset_builder.py 的 DatasetBuilder 类中添加

def _save_custom(self, dataset, path):
    """自定义格式示例：每行保存为纯文本，用特殊分隔符"""
    with open(path, 'w', encoding='utf-8') as f:
        for record in dataset:
            text = record.get('text', '')
            meta = record.get('metadata', {})
            # 自定义格式
            line = f"<doc>{meta.get('document', '')}</doc>\n<content>{text}</content>\n"
            f.write(line + '\n---\n')
```

### 5. 处理超大 PDF 文件

```yaml
performance:
  workers: 2                    # 减少并行数，避免内存峰值
  batch_size: 1                 # 逐个处理

output:
  max_chunk_size: 500           # 减小块大小
  split_by_page: true           # 按页拆分

extraction:
  extract_tables: false         # 如非必要，不提取表格
  extract_images: false         # 不提取图片

filtering:
  min_text_length: 50           # 过滤碎片，减少数据量
```

### 6. 质量评估

```python
from src import PDFParser

parser = PDFParser()

# 解析
metadata, pages = parser.parse("spec.pdf")

# 获取统计
stats = parser.get_statistics(pages)

print(f"文档: {metadata.filename}")
print(f"总页数: {stats['total_pages']}")
print(f"总字符: {stats['total_characters']:,}")
print(f"平均每页: {stats['avg_chars_per_page']:.0f} 字符")
print(f"总表格: {stats['total_tables']}")
print(f"表格密度: {stats['avg_tables_per_page']:.2f} 个/页")

# 评估提取率（简单估算）
text_ratio = stats['total_characters'] / (metadata.total_pages * 2000)  # 假设每页 2000 字符
print(f"文本提取率（估计）: {text_ratio:.1%}")
```

## 最佳实践

### 1. 配置文件管理

```
project/
├── config/
│   ├── base.yaml           # 基础配置
│   ├── technical_spec.yaml # 技术规范
│   ├── scanned.yaml        # 扫描件
│   └── production.yaml     # 生产环境（性能优化）
```

**base.yaml**:

```yaml
input:
  recursive: true
  extensions: [".pdf"]

filtering:
  remove_headers_footers:
    enabled: true
  min_text_length: 10
```

**technical_spec.yaml**:

```yaml
# 基础配置
 extends: base.yaml

# 覆盖
extraction:
  extract_tables: true
  table:
    strategy: "lattice"

output:
  chunk_strategy: "chapter"

dataset:
  format: "qa"
```

### 2. 目录组织

```
project/
├── pdfs/                   # 原始 PDF 文件
│   ├── technical/
│   ├── manuals/
│   └── standards/
├── output/
│   ├── parsed/            # 解析结果（中间文件）
│   ├── dataset/           # 训练数据集
│   └── logs/              # 日志文件
├── config/                # 配置文件
└── scripts/              # 脚本
```

### 3. 性能优化

- **并行处理**：`performance.workers` 设置为 CPU 核心数
- **内存优化**：大文件启用 `split_by_page: true`
- **缓存**：已解析文件会跳过，避免重复处理
- **增量处理**：只处理新增文件

### 4. 质量控制

1. **查看统计信息**：检查每个生成的 `*_stats.json`
2. **抽样检查**：随机打开几个输出文件查看内容
3. **验证格式**：确保输出格式符合训练工具的要求
4. **去重检查**：启用去重功能，避免重复数据

```python
# 快速抽样检查
import json, random

with open("output/dataset/yourfile.jsonl", 'r') as f:
    lines = f.readlines()
    sample = random.choice(lines)
    record = json.loads(sample)
    print(f"文本长度: {len(record['text'])}")
    print(f"元数据: {record.get('metadata', {})}")
```

### 5. 存储优化

```bash
# 使用 Parquet 格式（压缩，节省空间）
python scripts/transform.py --format parquet --compress

# 定期清理中间文件
rm -rf output/parsed/*

# 只保留最终数据集
```

## 故障排除

### 常见问题

#### 1. 表格提取为空白

**原因：**
- PDF 是扫描件，文本不可选
- 表格是无线表，检测策略不匹配
- 表格边界识别失败

**解决方案：**
```yaml
extraction:
  table:
    strategy: "stream"      # 尝试 stream 策略（无线表）
    edge_tol: 10            # 增加容差
    min_size: [2, 2]        # 降低最小尺寸要求

# 或使用自动检测
extraction:
  table:
    strategy: "auto"
```

#### 2. OCR 识别率低

**原因：**
- 扫描质量差（模糊、倾斜）
- 缺少对应语言包
- 未进行图像预处理

**解决方案：**
```bash
# 1. 确保语言包安装
tesseract --list-langs

# 2. 调整 OCR 配置
extraction:
  ocr:
    enabled: true
    languages: "chi_sim+eng"
    engine: "paddle"         # 尝试 PaddleOCR（中文更好）
    preprocessing: ["denoise", "binarize", "deskew"]  # 增加预处理
    confidence_threshold: 50  # 降低置信度阈值
```

#### 3. 内存不足

**症状：** 处理大文件时崩溃

**解决方案：**
```yaml
performance:
  workers: 1               # 单进程
  batch_size: 1            # 一次一个文件

output:
  max_chunk_size: 500      # 减小块大小
  split_by_page: true      # 按页拆分

extraction:
  extract_tables: false    # 禁用表格提取（如果不需要）
  extract_images: false    # 禁用图片提取
```

#### 4. 分块不合理

**问题：** 块太大或太小，内容被切断在关键位置

**解决方案：**
```yaml
# 尝试不同的分块策略
output:
  chunk_strategy: "chapter"   # 推荐：按章节分块，保持语义完整

# 调整块大小
output:
  max_chunk_size: 1500        # 增大
  chunk_overlap: 200          # 增加重叠，保留上下文
```

#### 5. 编码问题 / 乱码

**解决方案：**
```python
# 确保所有文件以 UTF-8 读写
import sys
sys.stdout.reconfigure(encoding='utf-8')  # Python 3.7+

# 或设置环境变量
export PYTHONIOENCODING=utf-8
```

### 调试模式

```bash
# 启用详细日志
python scripts/generate_dataset.py --config config.yaml --verbose

# 调试模式（保存中间结果）
# 编辑 config.yaml:
advanced:
  debug: true
```

调试输出会包含：
- 每个页面的文本长度
- 检测到的表格数量
- 文本块详细统计
- 错误堆栈

## FAQ

### Q: 支持哪些 PDF 类型？

**A:** 支持标准的 PDF 1.0-1.7 规范，包括：
- 文字型 PDF（可直接选中文本）
- 扫描型 PDF（需启用 OCR）
- 混合型（部分页面是图片，部分是文字）
- 加密 PDF（需提供密码，目前使用 pdfplumber 处理）

注意：某些特殊加密或损坏的 PDF 可能无法处理。

### Q: 处理速度如何？

**A:** 取决于：
- PDF 类型：文字型 > 扫描型（OCR 慢 10-100 倍）
- 文件大小：通常 1-5 秒/页（文字型），30-60 秒/页（扫描型）
- 线程数：更多 workers 加快处理，但受 CPU 限制

示例：100 页文字型 PDF，4 workers，约 30-60 秒。

### Q: 是否支持批量处理？

**A:** 完全支持！所有脚本都支持目录输入，可递归处理子目录。

### Q: 输出格式哪种最好？

**A:**
- **JSONL**: 最通用，推荐用于 LLM 训练（ChatGLM、Llama 等）
- **Parquet**: 最高效，适合大数据分析（Spark、Dask）
- **CSV**: 兼容性好，适合 Excel 查看
- **TXT**: 最简格式，适合词频分析

### Q: 如何处理表格 spanning 多个页面？

**A:** 当前版本不自动合并跨页表格。建议：

1. **预处理**：使用 Adobe Acrobat 等工具先修复 PDF
2. **手动合并**：处理后将相邻表格手动合并
3. **自定义规则**：修改 `table_extractor.py` 添加跨页检测逻辑

### Q: 能否提取图片并保存？

**A:** 当前版本主要关注文本。图片提取功能可通过以下方式实现：

```python
# 在 pdf_parser.py 的 _extract_images_pdfplumber 中实现
# 然后配置：
extraction:
  extract_images: true
  images_path: "images/"
```

### Q: 如何处理加密 PDF？

**A:** 如果知道密码：

```python
parser = PDFParser()
metadata, pages = parser.parse("encrypted.pdf", password="your_password")
```

（当前 API 未暴露 password 参数，需要修改 `pdf_parser.py`）

### Q: 能否只处理特定章节或页面？

**A:** 可以：

```bash
# 命令行指定页范围（需修改 parse.py 支持）
# 或使用 Python API:
metadata, pages = parser.parse("spec.pdf")
selected_pages = [p for p in pages if 10 <= p.page_num <= 20]
```

### Q: 支持哪些语言？

**A:** 理论上支持所有 PDF 可读语言。OCR 支持通过 Tesseract 或 PaddleOCR 支持 100+ 语言，包括：
- 中文（简体、繁体）
- 英文
- 日文、韩文
- 欧洲主要语言

### Q: 如何验证输出质量？

**A:**
1. 检查统计文件：`*_stats.json`
2. 抽样查看：`head -n 1 output/dataset/*.jsonl | python -m json.tool`
3. 计算提取率：`总字符数 / (页数 × 2000)`，正常应 >60%
4. 表格检查：确保重要表格都被提取

### Q: 可以集成到 CI/CD 吗？

**A:** 完全可以！所有脚本都有退出码，支持自动化：

```yaml
# GitHub Actions 示例
- name: 生成训练数据
  run: |
    python -m pip install -r requirements.txt
    python scripts/generate_dataset.py --config config/prod.yaml
- name: 验证数据集
  run: |
    python scripts/validate_dataset.py output/dataset/
```

### Q: 项目架构是怎样的？

**A:**
- `src/pdf_parser.py`: PDF 解析（pdfplumber/pymupdf）
- `src/data_transformer.py`: 清洗、分块、转换
- `src/dataset_builder.py`: 输出格式化和保存
- `src/utils.py`: 辅助函数
- `scripts/`: 命令行入口
- `config/`: 配置文件

### Q: 如何贡献代码或报告问题？

**A:** 欢迎贡献！
- 报告问题：提供 PDF 样本（或部分）、配置文件、错误日志
- 功能建议：说明使用场景和需求
- 代码贡献：遵循现有代码风格，添加测试

---

## 更多资源

- **项目 README**: 项目概述和功能列表
- **快速开始**: QUICKSTART.md - 5 分钟上手指南
- **示例代码**: examples/usage_demo.py - 完整 API 示例
- **配置文件**: config/config.yaml - 所有配置选项说明

## 许可证

MIT License
