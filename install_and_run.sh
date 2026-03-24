#!/usr/bin/env python3
"""
快速安装和测试脚本

自动安装依赖，验证安装，运行示例。
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description=""):
    """运行命令并显示输出"""
    print(f"\n{'='*60}")
    print(f"执行: {description or cmd}")
    print('='*60)

    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print("错误输出:", result.stderr)

    return result.returncode == 0

def check_python():
    """检查 Python 版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 版本过低: {version.major}.{version.minor}.{version.micro}")
        print("   需要 Python 3.8+")
        return False

    print(f"✓ Python 版本: {version.major}.{version.minor}.{version.micro}")
    return True

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

    tests = [
        ("src.pdf_parser", "PDF 解析器"),
        ("src.data_transformer", "数据转换器"),
        ("src.dataset_builder", "数据集构建器"),
        ("src.utils", "工具函数"),
    ]

    all_passed = True
    for module, name in tests:
        try:
            __import__(module)
            print(f"  ✓ {name}: {module}")
        except ImportError as e:
            print(f"  ✗ {name}: 导入失败 - {e}")
            all_passed = False

    return all_passed

def run_self_test():
    """运行自检"""
    print("\n运行自检...")

    # 检查可选依赖
    optional_deps = {
        "pymupdf": "PyMuPDF (fitz)",
        "paddleocr": "PaddleOCR (中文OCR)"
    }

    for module, name in optional_deps:
        try:
            __import__(module)
            print(f"  ✓ {name}: 已安装")
        except ImportError:
            print(f"  ○ {name}: 未安装（可选）")

    return True

def show_next_steps():
    """显示下一步操作"""
    print("\n" + "="*60)
    print("安装完成！")
    print("="*60)
    print("""
下一步操作：

1. 准备 PDF 文件
   将需要处理的 PDF 规范文件放到 ./pdfs/ 目录

2. 配置转换参数
   根据需要编辑 config/config.yaml

3. 运行解析测试
   python scripts/parse.py --input ./pdfs/sample.pdf --output ./output/parsed/

4. 生成训练数据集
   python scripts/generate_dataset.py --config config/config.yaml

5. 使用转换工具
   python scripts/transform.py --input ./parsed/ --output ./dataset/

提示：
- 中文 PDF 建议安装 Tesseract 中文字体包
- 扫描件 PDF 需要启用 OCR（--ocr 或配置文件中设置）
- 大文件处理可能需要较多内存，可以调整分块大小
    """)

def main():
    print("PDF 规范转训练数据 - 安装脚本")
    print(f"Python: {sys.executable}")

    steps = [
        ("检查 Python 环境", check_python),
        ("安装依赖包", install_requirements),
        ("测试模块导入", test_imports),
        ("运行自检", run_self_test),
    ]

    for desc, func in steps:
        if not func():
            print(f"\n❌ {desc} 失败，请检查问题后重试")
            return 1

    show_next_steps()
    return 0

if __name__ == "__main__":
    sys.exit(main())
