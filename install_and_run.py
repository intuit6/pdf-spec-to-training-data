#!/usr/bin/env python3
"""
快速安装和测试脚本（Windows/Linux/macOS 通用）

用法：
  chmod +x install_and_run.sh (Linux/macOS)
  或直接运行: python install_and_run.py

自动安装依赖，验证安装，运行示例。
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description="", check=True):
    """运行命令并显示输出"""
    print(f"\n{'='*60}")
    print(f"执行: {description or cmd}")
    print('='*60)

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            text=True,
            capture_output=True,
            env=os.environ.copy()
        )

        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("错误输出:", result.stderr)

        if check and result.returncode != 0:
            print(f"❌ 命令执行失败，退出码: {result.returncode}")
            return False

        return True
    except Exception as e:
        print(f"❌ 执行命令异常: {e}")
        return False

def check_python():
    """检查 Python 版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 版本过低: {version.major}.{version.minor}.{version.micro}")
        print("   需要 Python 3.8+")
        return False

    print(f"✓ Python 版本: {version.major}.{version.minor}.{version.micro}")
    print(f"✓ Python 路径: {sys.executable}")
    return True

def upgrade_pip():
    """升级 pip"""
    print("\n升级 pip...")
    return run_command(
        f"{sys.executable} -m pip install --upgrade pip",
        "升级 pip"
    )

def install_requirements():
    """安装依赖"""
    req_file = Path(__file__).parent / "requirements.txt"
    if not req_file.exists():
        print("❌ 找不到 requirements.txt")
        return False

    print("\n开始安装依赖包...")
    return run_command(
        f"{sys.executable} -m pip install -r {req_file} --upgrade",
        "安装依赖包"
    )

def install_package():
    """安装项目包（开发模式）"""
    print("\n安装项目包...")
    return run_command(
        f"{sys.executable} -m pip install -e .",
        "安装项目（开发模式）"
    )

def test_imports():
    """测试导入"""
    print("\n测试模块导入...")

    # 确保 src 在路径中
    sys.path.insert(0, str(Path(__file__).parent))

    tests = [
        ("pdf_parser", "PDF 解析器"),
        ("data_transformer", "数据转换器"),
        ("dataset_builder", "数据集构建器"),
        ("utils", "工具函数"),
    ]

    all_passed = True
    for module, name in tests:
        try:
            __import__(module)
            print(f"  ✓ {name}: src.{module}")
        except ImportError as e:
            print(f"  ✗ {name}: 导入失败 - {e}")
            all_passed = False

    return all_passed

def run_self_test():
    """运行自检"""
    print("\n运行自检...")

    # 检查可选依赖
    optional_deps = [
        ("pymupdf", "PyMuPDF", "fitz", "用于更快 PDF 解析"),
        ("paddleocr", "PaddleOCR", "paddleocr", "用于中文 OCR（效果更好）"),
    ]

    for module_name, display_name, import_name, desc in optional_deps:
        try:
            __import__(import_name)
            print(f"  ✓ {display_name}: 已安装 - {desc}")
        except ImportError:
            print(f"  ○ {display_name}: 未安装（可选）- {desc}")

    # 检查 Tesseract（如果 OCR 需要）
    print("\n  OCR 环境检查:")
    try:
        result = subprocess.run(["tesseract", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ Tesseract: {result.stdout.split()[1]}")
        else:
            print(f"  ○ Tesseract: 未安装或不在 PATH 中")
    except FileNotFoundError:
        print(f"  ○ Tesseract: 未安装（如需 OCR 请安装）")

    return True

def create_directories():
    """创建必要的目录"""
    print("\n创建项目目录结构...")

    dirs = [
        "pdfs",           # PDF 输入目录
        "output/parsed",  # 解析结果
        "output/dataset", # 训练数据集
        "output/images",  # 提取的图片
        "logs",           # 日志
        "config",         # 配置文件
    ]

    base_dir = Path(__file__).parent
    for dir_path in dirs:
        (base_dir / dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ 创建目录: {dir_path}")

    return True

def show_next_steps():
    """显示下一步操作"""
    print("\n" + "="*60)
    print("安装完成！")
    print("="*60)
    print("""
下一步操作：

1. 准备 PDF 文件
   - 将需要处理的 PDF 规范文件复制到 ./pdfs/ 目录
   - 支持 .pdf 扩展名（大小写不敏感）

2. 配置转换参数（可选）
   - 编辑 config/config.yaml
   - 常用调整：分块策略、输出格式、是否启用 OCR

3. 快速开始测试

   a) 解析单个 PDF：
      python scripts/parse.py --input ./pdfs/your_doc.pdf --output ./output/parsed/ --verbose

   b) 生成训练数据集：
      python scripts/generate_dataset.py --config config/config.yaml

   c) 直接转换已解析的数据：
      python scripts/transform.py --input ./output/parsed/ --output ./output/dataset/ --format jsonl

4. 输出文件位置
   - 解析结果: ./output/parsed/{文件名}_parsed.json
   - 训练数据集: ./output/dataset/{文件名}_jsonl_*.jsonl
   - 统计信息: ./output/dataset/{文件名}_stats.json

5. 使用训练数据
   - JSONL 格式可直接用于训练大语言模型（如 Llama, GPT 等）
   - CSV 格式可用于表格分析或传统机器学习
   - TXT 格式可用于词频分析等

常见问题：
  Q: 扫描件 PDF 怎么处理？
  A: 确保安装了 Tesseract 和中文语言包，在配置文件中启用 ocr.enabled: true

  Q: 表格识别不准确？
  A: 尝试调整 config.yaml 中 table.strategy 为 "lattice"（有线表）或 "stream"（无线表）

  Q: 如何处理大量 PDF？
  A: 所有脚本都支持批量处理，配置文件中的 performance.workers 可调整并行数

更多帮助：
  - 查看 README.md 了解详细功能
  - 查看 config/config.yaml 了解所有配置选项
  - 运行脚本加 --help 查看更多参数
    """)

def main():
    print("PDF 规范转训练数据 - 安装脚本")
    print(f"Python: {sys.executable}")

    steps = [
        ("检查 Python 环境", check_python),
        ("升级 pip", upgrade_pip),
        ("安装依赖包", install_requirements),
        ("创建项目目录", create_directories),
        ("测试模块导入", test_imports),
        ("运行自检", run_self_test),
    ]

    for desc, func in steps:
        print()
        if not func():
            print(f"\n❌ {desc} 失败，请检查问题后重试")
            return 1

    show_next_steps()
    return 0

if __name__ == "__main__":
    sys.exit(main())
