# PDF Spec to Training Data

> 将 PDF 规范文档转换为可用于训练的机器学习数据集

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/yourusername/pdf-spec-to-training-data/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/pdf-spec-to-training-data/actions)
[![codecov](https://codecov.io/gh/yourusername/pdf-spec-to-training-data/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/pdf-spec-to-training-data)
[![PyPI version](https://badge.fury.io/py/pdf-spec-to-training-data.svg)](https://badge.fury.io/py/pdf-spec-to-training-data)
[![Downloads](https://pepy.tech/badge/pdf-spec-to-training-data)](https://pepy.tech/project/pdf-spec-to-training-data)

一个强大而灵活的工具，用于将 PDF 规范文档（技术文档、标准规范、产品手册等）转换为可用于训练机器学习模型的数据集。支持文本提取、表格识别、结构化解析和多格式输出。

✨ ** Features **
- 📄 **PDF 文本提取**：高精度提取文字型 PDF 内容
- 📊 **表格识别**：自动提取有线表和无线表，支持合并单元格
- 🔍 **智能分块**：按章节、段落或固定长度智能分割文本
- 📤 **多格式输出**：JSONL、CSV、TXT、Parquet 等格式
- ⚙️ **配置驱动**：YAML 配置文件控制提取规则
- 🚀 **批量处理**：支持目录批量处理和并行加速
- 🔧 **OCR 支持**：可选的 Tesseract/PaddleOCR 支持
- 📈 **质量评估**：自动统计提取质量和覆盖度

## 主要功能

- **PDF 文本提取**：从 PDF 中提取纯文本内容
- **表格识别与提取**：自动识别并提取 PDF 中的表格数据
- **结构化解析**：识别标题、章节、列表等结构
- **多格式输出**：支持 JSONL、CSV、JSON、TXT 等多种训练数据格式
- **批量处理**：支持批量处理多个 PDF 文件
- **配置文件驱动**：通过配置文件控制提取规则和输出格式

---

## 🚀 快速开始

### 安装

```bash
# 1. 克隆或下载项目
git clone https://github.com/yourusername/pdf-spec-to-training-data.git
cd pdf-spec-to-training-data

# 2. 安装依赖（推荐使用虚拟环境）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 3. 安装项目
pip install -e .

# 或安装完整依赖（包括 OCR 支持）
pip install -e ".[all]"
```

### 基础使用

#### 方式一：一条命令生成数据集

```bash
# 准备配置文件
cp config/config.yaml config/myconfig.yaml
# 编辑 config.yaml 调整输入输出路径

# 运行完整流程
python scripts/generate_dataset.py --config config/config.yaml

# 查看结果
ls output/dataset/
```

#### 方式二：模块化使用

```python
from src import PDFParser, DataTransformer, DatasetBuilder

# 1. 解析 PDF
parser = PDFParser("spec.pdf")
metadata, pages = parser.parse("spec.pdf")
print(f"解析了 {len(pages)} 页，{len(metadata.title)} 标题")

# 2. 转换数据
transformer = DataTransformer()
chunks = transformer.transform_pages(pages)
print(f"生成了 {len(chunks)} 个文本块")

# 3. 构建数据集
builder = DatasetBuilder(format="jsonl")
dataset = builder.build_from_chunks(chunks, format_type="text")

# 4. 保存
output_path = builder.save(dataset, "output", "my_dataset")
print(f"数据集保存到: {output_path}")
```

更多详细教程请查看 [QUICKSTART.md](QUICKSTART.md) 和 [docs/USAGE.md](docs/USAGE.md)。

---

## 📦 核心特性详解

### PDF 解析引擎

支持两种解析后端，可自动或手动选择：

| 引擎 | 优势 | 适用场景 |
|------|------|----------|
| `pdfplumber` | 表格提取强，布局保留好 | 技术文档、规范 |
| `pymupdf` | 速度极快，内存占用低 | 纯文本型 PDF |

```python
parser = PDFParser(parser="pdfplumber")  # 或 "pymupdf"
```

### 表格提取

- **有线表（Lattice）**：识别表格边框线
- **无线表（Stream）**：基于文本位置推断表格
- **自动检测**：智能选择最佳策略
- **支持合并单元格**：保留表格结构信息

```yaml
extraction:
  table:
    strategy: "auto"  # lattice, stream, auto
    edge_tol: 5
    min_size: [2, 2]
```

### 智能分块策略

| 策略 | 说明 | 适用 |
|------|------|------|
| `fixed` | 固定长度分块（可重叠） | NLP 训练、统一输入长度 |
| `paragraph` | 按段落分块 | 保持语义完整 |
| `chapter` | 按章节分块 | 技术文档、书籍 |
| `page` | 按页分块 | 简单场景、有明确页结构 |
| `none` | 不分块 | 后续自定义处理 |

```yaml
output:
  chunk_strategy: "chapter"
  max_chunk_size: 1500
  chunk_overlap: 100
```

### 输出格式

| 格式 | 推荐场景 | 示例 |
|------|----------|------|
| **JSONL** | LLM 训练、流式处理 | `{"text": "...", "metadata": {...}}` |
| **Parquet** | 大数据分析、Spark | 列式存储，高效 |
| **CSV** | Excel 查看、表格分析 | 扁平化列 |
| **TXT** | 词频统计、简单查看 | 纯文本 |
| **JSON** | 人类可读、API 响应 | 嵌套结构 |

---

## 🛠️ 配置说明

核心配置文件 `config/config.yaml`：

```yaml
# 输入
input:
  path: "./pdfs/"
  recursive: true

# 输出
output:
  format: "jsonl"
  chunk_strategy: "paragraph"
  max_chunk_size: 1000

# 提取配置
extraction:
  extract_text: true
  extract_tables: true
  preserve_layout:
    enabled: true

# 过滤配置
filtering:
  remove_headers_footers:
    enabled: true
    keywords: ["第", "页", "Copyright"]
  min_text_length: 10

# OCR（扫描件）
extraction:
  ocr:
    enabled: true
    languages: "chi_sim+eng"
    engine: "tesseract"  # 或 "paddle"
```

[查看更多配置选项](docs/USAGE.md#配置详解)。

---

## 📚 典型使用场景

### 场景一：技术规范文档（表格+章节）

```yaml
extraction:
  extract_tables: true
  table:
    strategy: "lattice"  # 有线表

output:
  chunk_strategy: "chapter"  # 按章节分块
  max_chunk_size: 2000

dataset:
  format: "qa"  # 生成问答对
```

### 场景二：产品说明书（图片+文字）

```yaml
extraction:
  extract_tables: false
  extract_images: true  # 提取图片（需扩展代码）

output:
  chunk_strategy: "page"
```

### 场景三：扫描件 PDF（OCR）

**前置要求**：安装 Tesseract 和中文语言包

```bash
# Ubuntu
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim

# macOS
brew install tesseract tesseract-lang
```

配置：
```yaml
extraction:
  ocr:
    enabled: true
    languages: "chi_sim+eng"
    engine: "paddle"  # 中文效果更好（需安装 paddleocr）
```

### 场景四：批量处理大量文件

```bash
# 自动并行处理
performance:
  workers: 8  # CPU 核心数

# 递归搜索子目录
input:
  recursive: true
```

---

## 📖 文档

- [快速开始指南](QUICKSTART.md) - 5 分钟上手
- [详细使用文档](docs/USAGE.md) - 配置、API、高级用法
- [示例代码](examples/usage_demo.py) - 完整 API 示例
- [GitHub 设置指南](GITHUB_SETUP.md) - 如何部署到 GitHub

---

## 🧪 测试与质量

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest tests/ -v

# 代码格式化
black src/ tests/ scripts/
isort src/ tests/ scripts/

# 代码检查
flake8 src/ tests/
mypy src/ --ignore-missing-imports
```

---

## 🔒 安全性

本工具旨在处理本地文档，不会向外部发送数据，确保你的敏感文档安全。

详见 [SECURITY.md](SECURITY.md)。

---

## 🤝 贡献

欢迎贡献！请先阅读 [贡献指南](CONTRIBUTING.md)。

## 📄 许可证

MIT License © 2025 PDF Spec to Training Data Contributors

## 高级功能

### 1. 自定义提取规则

通过正则表达式或关键词匹配，提取特定内容：

```python
# config/rules.yaml
rules:
  - name: "章节标题"
    pattern: "^第[一二三四五六七八九十]+章"
    type: "heading"
  - name: "表格标题"
    pattern: "^表\\d+"
    type: "table_caption"
```

### 2. 数据清洗

内置多种清洗选项：
- 删除页眉页脚
- 移除多余空格和换行
- 标准化标点符号
- 合并短行

### 3. 分块策略

支持多种文本分块方式：
- 固定长度分块
- 按段落分块
- 按章节分块
- 重叠分块（保留上下文）

### 4. 质量评估

提供提取质量报告：
- 提取文本占原文档比例
- 表格识别准确率
- 遗漏内容统计

## 使用示例

```python
from src.pdf_parser import PDFParser
from src.data_transformer import DataTransformer
from src.dataset_builder import DatasetBuilder

# 1. 解析 PDF
parser = PDFParser("document.pdf")
pages = parser.extract_text_with_layout()

# 2. 提取表格
tables = parser.extract_tables()

# 3. 转换数据
transformer = DataTransformer()
chunks = transformer.create_chunks(pages, chunk_size=1000)

# 4. 构建数据集
builder = DatasetBuilder()
dataset = builder.build_from_chunks(chunks, format="jsonl")

# 5. 保存
builder.save(dataset, "output.jsonl")
```

## 常见 PDF 类型适配

| PDF 类型 | 推荐配置 | 注意事项 |
|---------|---------|---------|
| 文字型 PDF | `extract_text: true`, `preserve_layout: true` | 提取质量高，速度快 |
| 扫描型 PDF | `ocr_enabled: true` | 需要安装 Tesseract 和中文语言包 |
| 表格密集型 | `extract_tables: true`, `table_orientation: "detect"` | 可能需要手动调整表格边界 |
| 混合型 | 所有选项启用 | 处理时间较长 |

## 性能优化

1. **并行处理**：使用多进程批量处理 PDF
2. **缓存**：缓存已解析的 PDF 避免重复处理
3. **选择性提取**：只提取需要的页面范围
4. **增量处理**：支持断点续传

## 故障排除

### 问题：表格提取不准确
**解决**：调整 `table_orientation` 和 `table_edge_tol` 参数，或使用 `table_manual_areas` 指定表格区域。

### 问题：OCR 识别率低
**解决**：确保安装了对应语言包（`tesseract-lang-{zh,en}`），预处理图像（去噪、增强对比度）。

### 问题：输出文件太大
**解决**：减小 `max_chunk_size`，启用 `split_by_page`，或使用 `filtering` 删除无关内容。

## 扩展开发

### 添加新的输出格式

1. 在 `src/dataset_builder.py` 中添加新的 `export_xxx` 方法
2. 在配置文件中添加对应格式选项
3. 编写格式验证和测试

### 支持新的 PDF 类型

在 `pdf_parser.py` 中添加新的提取策略，根据 PDF 特征自动选择最佳策略。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request。
