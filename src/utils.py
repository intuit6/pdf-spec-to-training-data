"""工具函数模块

提供通用工具函数：文件操作、配置加载、日志设置等。
"""

import os
import sys
import yaml
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from datetime import datetime


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    console: bool = True
) -> logging.Logger:
    """配置日志系统

    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
        log_file: 日志文件路径（可选）
        console: 是否输出到控制台

    Returns:
        根日志记录器
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # 创建格式器
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 根日志记录器
    logger = logging.getLogger()
    logger.setLevel(numeric_level)

    # 清除现有处理器
    logger.handlers.clear()

    # 控制台处理器
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # 文件处理器
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def load_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """加载 YAML 配置文件

    Args:
        config_path: 配置文件路径

    Returns:
        配置字典
    """
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    logger = logging.getLogger(__name__)
    logger.info(f"加载配置文件: {config_path}")

    return config


def ensure_dir(path: Union[str, Path]) -> Path:
    """确保目录存在，如果不存在则创建

    Args:
        path: 目录路径

    Returns:
        Path 对象
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_size_mb(file_path: Union[str, Path]) -> float:
    """获取文件大小（MB）"""
    return Path(file_path).stat().st_size / (1024 * 1024)


def human_readable_size(size_bytes: int) -> str:
    """将字节数转换为可读字符串"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def save_json(data: Any, file_path: Union[str, Path], indent: int = 2):
    """保存数据为 JSON 文件"""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def load_json(file_path: Union[str, Path]) -> Any:
    """从 JSON 文件加载数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_output_filename(
    prefix: str,
    suffix: str,
    output_dir: Path,
    format: str = "jsonl"
) -> Path:
    """生成输出文件名（带时间戳）"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.{format}"
    return output_dir / filename


def validate_pdf_file(file_path: Union[str, Path]) -> bool:
    """验证是否为有效的 PDF 文件"""
    file_path = Path(file_path)

    if not file_path.exists():
        return False

    if not file_path.is_file():
        return False

    if file_path.suffix.lower() != '.pdf':
        return False

    # 检查文件头
    try:
        with open(file_path, 'rb') as f:
            header = f.read(4)
            return header.startswith(b'%PDF')
    except:
        return False


def extract_text_from_html_like(text: str) -> str:
    """从 HTML 或标记化文本中提取纯文本"""
    import re

    # 移除 HTML 标签
    text = re.sub(r'<[^>]+>', '', text)

    # 移除多余的空白
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def calculate_text_similarity(text1: str, text2: str) -> float:
    """计算两段文本的相似度（简化版）"""
    from collections import Counter

    if not text1 or not text2:
        return 0.0

    # 分词
    words1 = Counter(text1.lower().split())
    words2 = Counter(text2.lower().split())

    # Jaccard 相似度
    intersection = sum((words1 & words2).values())
    union = sum((words1 | words2).values())

    if union == 0:
        return 0.0

    return intersection / union


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
    """展平嵌套字典"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """将列表分块"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def safe_filename(filename: str) -> str:
    """生成安全的文件名（移除非法字符）"""
    import re
    # 移除或替换非法字符
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 移除末尾空格和点
    filename = filename.rstrip(' .')
    return filename or "unnamed"


def merge_dicts(*dicts: Dict[Any, Any]) -> Dict[Any, Any]:
    """合并多个字典（后面的覆盖前面的）"""
    result = {}
    for d in dicts:
        result.update(d)
    return result


def get_timestamp_str() -> str:
    """获取当前时间戳字符串"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def is_chinese(text: str) -> bool:
    """判断文本是否包含中文字符"""
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
    return bool(chinese_pattern.search(text))


if __name__ == "__main__":
    # 测试工具函数
    print("工具模块测试")
    print(f"当前时间: {get_timestamp_str()}")
    print(f"安全文件名: {safe_filename('test/file:name.txt')}")
    print(f"文件大小: {human_readable_size(1024*1024*5)}")
