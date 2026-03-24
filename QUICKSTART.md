# 快速开始指南

## 5 分钟上手

### 1. 安装依赖

```bash
# 方式一：使用安装脚本（推荐）
python install_and_run.py

# 方式二：手动安装
pip install -r requirements.txt
```

### 2. 准备 PDF 文件

创建一个 `pdfs` 目录，放入你的 PDF 规范文件：

```bash
mkdir -p pdfs
# 复制你的 PDF 文件到 pdfs/ 目录
cp /path/to/your/spec.pdf pdfs/
```

### 3. 运行处理

**方式 A：快速解析（只提取文本）**

```bash
python scripts/parse.py --input pdfs/ --output output/parsed/
```

**方式 B：完整数据集生成（推荐）**

```bash
python scripts/generate_dataset.py --config config/config.yaml
```

### 4. 查看结果

输出文件在 `output/dataset/` 目录：

- `xxx_jsonl_*.jsonl` - 训练数据集（每行一条记录）
- `xxx_stats.json` - 统计信息

### 5. 使用数据

**查看数据集内容：**

```bash
# 查看第一条记录
head -n 1 output/dataset/*.jsonl | python -m json.tool

# 统计记录数
wc -l output/dataset/*.jsonl

# 查看统计信息
cat output/dataset/*_stats.json
```

---

## 常用命令参考

### 解析单个 PDF（调试用）

```bash
python scripts/parse.py \
  --input ./pdfs/manual.pdf \
  --output ./output/parsed/ \
  --verbose
```

### 批量处理（递归子目录）

```bash
python scripts/parse.py \
  --input ./pdfs/ \
  --output ./output/parsed/ \
  --recursive
```

### 生成不同格式的数据集

```bash
# JSONL（推荐，用于 LLM 训练）
python scripts/generate_dataset.py --config config/config.yaml

# TXT（纯文本）
python scripts/transform.py \
  --input ./output/parsed/ \
  --output ./output/dataset/ \
  --format txt

# CSV（表格分析）
python scripts/transform.py \
  --input ./output/parsed/ \
  --output ./output/dataset/ \
  --format csv
```

### 调整分块策略

编辑 `config/config.yaml`：

```yaml
output:
  chunk_strategy: "chapter"  # 按章节分块（默认是 paragraph）
  max_chunk_size: 2000       # 增大块大小
```

或使用命令行参数：

```bash
python scripts/transform.py \
  --input ./output/parsed/ \
  --output ./output/dataset/ \
  --chunk-strategy fixed \
  --chunk-size 2000
```

---

## 配置文件说明

核心配置在 `config/config.yaml`：

| 配置项 | 说明 | 常用值 |
|--------|------|--------|
| input.path | 输入目录 | "./pdfs/" |
| output.format | 输出格式 | "jsonl", "txt", "csv" |
| output.chunk_strategy | 分块策略 | "paragraph", "chapter", "fixed" |
| extraction.extract_tables | 是否提取表格 | true/false |
| filtering.remove_headers_footers | 是否移除页眉页脚 | true/false |
| ocr.enabled | 是否启用 OCR | false（扫描件设为 true） |

---

## 典型使用场景

### 场景 1：技术规范文档

**特点：** 结构化强，含大量表格、章节标题

**推荐配置：**

```yaml
output:
  chunk_strategy: "chapter"   # 按章节分块，保持结构
  max_chunk_size: 2000

extraction:
  extract_tables: true
  preserve_layout:
    enabled: true
```

### 场景 2：产品说明书

**特点：** 图片多，文字少

**推荐配置：**

```yaml
extraction:
  extract_tables: false
  extract_images: true

output:
  chunk_strategy: "page"     # 按页分块
```

### 场景 3：标准文档（PDF/A）

**特点：** 文字型 PDF，内容规范

**推荐配置：**

```yaml
extraction:
  parser: "pdfplumber"
  preserve_layout:
    enabled: false           # 不保留排版，更紧凑

filtering:
  remove_headers_footers: true
  min_text_length: 50        # 过滤碎片内容
```

### 场景 4：扫描件或图片型 PDF

**必需：** 安装 Tesseract OCR

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim

# macOS
brew install tesseract tesseract-lang
```

**配置：**

```yaml
extraction:
  ocr:
    enabled: true
    languages: "chi_sim+eng"  # 中文+英文
    engine: "tesseract"       # 或 "paddle"（飞桨，中文更好）
```

---

## 故障排除

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 找不到 PDF 文件 | 路径错误 | 检查 input.path 配置，使用绝对路径 |
| 表格提取为空 | PDF 为图片型 | 启用 OCR 或使用其他解析器 |
| 内存不足 | 文件太大 | 减小 max_chunk_size，启用分批处理 |
| 中文乱码 | 编码问题 | 确保文件保存为 UTF-8 |
| OCR 识别率低 | 语言包缺失 | 安装对应语言的 Tesseract 包 |

---

## 高级用法

### 使用 Python API

```python
from src import PDFParser, DataTransformer, DatasetBuilder

# 1. 解析
parser = PDFParser("pdfs/manual.pdf")
metadata, pages = parser.parse("pdfs/manual.pdf")

# 2. 转换
transformer = DataTransformer()
chunks = transformer.transform_pages(pages)

# 3. 构建数据集
builder = DatasetBuilder(format="jsonl")
dataset = builder.build_from_chunks(chunks, format_type="text")

# 4. 保存
builder.save(dataset, "output/custom.jsonl")
```

### 批量合并多个数据集

```python
from src import DatasetBuilder

builder = DatasetBuilder(format="jsonl")
merged = builder.merge_datasets(
    ["output/dataset/part1.jsonl", "output/dataset/part2.jsonl"],
    output_path=Path("./output/final"),
    deduplicate=True
)
```

---

## 更多资源

- **详细文档**: 查看完整的 README.md
- **配置示例**: 参考 config/config.yaml 中的所有选项
- **问题反馈**: 提交 Issue 到项目仓库
- **自定义开发**: 参考 src/ 各模块代码

祝你使用愉快！📄✨
