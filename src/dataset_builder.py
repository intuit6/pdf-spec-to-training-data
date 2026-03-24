"""数据集构建器

将处理后的文本块转换为各种训练数据格式并保存。
支持：JSONL, JSON, CSV, TXT, Parquet 等格式。
"""

import json
import csv
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import asdict

import pandas as pd

logger = logging.getLogger(__name__)


class DatasetBuilder:
    """数据集构建器"""

    def __init__(
        self,
        output_format: str = "jsonl",
        add_special_tokens: bool = False,
        special_tokens: Dict[str, str] = None
    ):
        """初始化数据集构建器

        Args:
            output_format: 输出格式：jsonl, json, csv, txt, parquet
            add_special_tokens: 是否添加特殊标记（BOS, EOS等）
            special_tokens: 特殊标记字典
        """
        self.output_format = output_format.lower()
        self.add_special_tokens = add_special_tokens

        self.special_tokens = {
            "bos": "<s>",
            "eos": "</s>",
            "sep": "<sep>",
            **(special_tokens or {})
        }

        # 验证输出格式
        supported_formats = ["jsonl", "json", "csv", "txt", "parquet"]
        if self.output_format not in supported_formats:
            raise ValueError(f"不支持的输出格式: {output_format}，支持: {supported_formats}")

    def build_from_chunks(
        self,
        chunks: List[Any],
        format_type: str = "text",
        dataset_config: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """从文本块构建数据集

        Args:
            chunks: TextChunk 列表
            format_type: 数据集格式类型：text, qa, instruction
            dataset_config: 数据集配置

        Returns:
            数据集记录列表
        """
        dataset = []

        for chunk in chunks:
            record = self._create_record(chunk, format_type, dataset_config)
            dataset.append(record)

        logger.info(f"构建了 {len(dataset)} 条数据记录，格式: {format_type}")
        return dataset

    def _create_record(
        self,
        chunk: Any,
        format_type: str,
        config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """创建单条数据记录"""
        config = config or {}

        if format_type == "text":
            return self._format_text(chunk)
        elif format_type == "qa":
            return self._format_qa(chunk, config)
        elif format_type == "instruction":
            return self._format_instruction(chunk, config)
        else:
            raise ValueError(f"不支持的格式类型: {format_type}")

    def _format_text(self, chunk: Any) -> Dict[str, Any]:
        """格式化为纯文本格式"""
        content = chunk.content

        if self.add_special_tokens:
            content = f"{self.special_tokens['bos']}{content}{self.special_tokens['eos']}"

        record = {
            "text": content,
            "metadata": chunk.metadata.copy() if hasattr(chunk, 'metadata') else {}
        }

        # 添加唯一ID
        if hasattr(chunk, 'chunk_id'):
            record["id"] = chunk.chunk_id

        return record

    def _format_qa(self, chunk: Any, config: Dict[str, Any]) -> Dict[str, Any]:
        """格式化为问答对格式"""
        # 简单实现：使用通用问题模板
        templates = config.get("question_templates", [
            "请阅读以下文档内容：{content}",
            "根据文档回答：{content}"
        ])

        import random
        template = random.choice(templates)
        short_content = chunk.content[:100] + "..." if len(chunk.content) > 100 else chunk.content
        instruction = template.format(content=short_content)

        record = {
            "instruction": instruction,
            "input": "",
            "output": chunk.content,
            "id": getattr(chunk, 'chunk_id', str(hash(chunk.content))),
            "metadata": chunk.metadata.copy() if hasattr(chunk, 'metadata') else {}
        }

        return record

    def _format_instruction(self, chunk: Any, config: Dict[str, Any]) -> Dict[str, Any]:
        """格式化为指令-响应对格式"""
        templates = config.get("instruction_templates", [
            "请阅读以下技术规范并回答问题：{task}",
            "根据文档内容，{task}。"
        ])

        tasks = config.get("task_types", ["总结主要内容", "提取关键信息"])
        import random

        template = random.choice(templates)
        task = random.choice(tasks)

        instruction = template.format(task=task)

        record = {
            "instruction": instruction,
            "input": chunk.content[:500],  # 限制输入长度
            "output": chunk.content,  # 完整回答
            "id": getattr(chunk, 'chunk_id', str(hash(chunk.content))),
            "metadata": chunk.metadata.copy() if hasattr(chunk, 'metadata') else {}
        }

        return record

    def save(
        self,
        dataset: List[Dict[str, Any]],
        output_path: Union[str, Path],
        filename_prefix: str = "dataset"
    ) -> Path:
        """保存数据集

        Args:
            dataset: 数据集记录列表
            output_path: 输出目录
            filename_prefix: 文件名前缀

        Returns:
            保存的文件路径
        """
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{self.output_format}_{timestamp}"

        full_path = output_path / f"{filename}.{self.output_format}"

        logger.info(f"保存数据集到: {full_path}")
        logger.info(f"记录数: {len(dataset)}")

        if self.output_format == "jsonl":
            self._save_jsonl(dataset, full_path)
        elif self.output_format == "json":
            self._save_json(dataset, full_path)
        elif self.output_format == "csv":
            self._save_csv(dataset, full_path)
        elif self.output_format == "txt":
            self._save_txt(dataset, full_path)
        elif self.output_format == "parquet":
            self._save_parquet(dataset, full_path)

        logger.info(f"数据集保存完成: {full_path}")
        return full_path

    def _save_jsonl(self, dataset: List[Dict], path: Path):
        """保存为 JSONL 格式（每行一个 JSON 对象）"""
        with open(path, 'w', encoding='utf-8') as f:
            for record in dataset:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')

    def _save_json(self, dataset: List[Dict], path: Path):
        """保存为 JSON 格式"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({
                "dataset": dataset,
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "format": "json",
                    "record_count": len(dataset)
                }
            }, f, ensure_ascii=False, indent=2)

    def _save_csv(self, dataset: List[Dict], path: Path):
        """保存为 CSV 格式"""
        if not dataset:
            logger.warning("数据集为空，跳过 CSV 保存")
            return

        # 展平嵌套的 metadata
        flattened_data = []
        for record in dataset:
            flat_record = {}
            for key, value in record.items():
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        flat_record[f"{key}_{subkey}"] = subvalue
                else:
                    flat_record[key] = value
            flattened_data.append(flat_record)

        with open(path, 'w', newline='', encoding='utf-8-sig') as f:
            if flattened_data:
                writer = csv.DictWriter(f, fieldnames=flattened_data[0].keys())
                writer.writeheader()
                writer.writerows(flattened_data)

    def _save_txt(self, dataset: List[Dict], path: Path):
        """保存为纯文本格式"""
        with open(path, 'w', encoding='utf-8') as f:
            for i, record in enumerate(dataset, 1):
                f.write(f"=== 记录 {i} ===\n\n")

                # 优先输出 text 字段
                if "text" in record:
                    f.write(record["text"])
                elif "output" in record:
                    f.write(record["output"])
                elif "instruction" in record:
                    f.write(f"指令: {record['instruction']}\n\n")
                    if "input" in record and record["input"]:
                        f.write(f"输入: {record['input']}\n\n")
                    f.write(f"回答: {record.get('output', '')}")

                f.write("\n\n" + "="*50 + "\n\n")

    def _save_parquet(self, dataset: List[Dict], path: Path):
        """保存为 Parquet 格式（高效二进制格式）"""
        if not dataset:
            logger.warning("数据集为空，跳过 Parquet 保存")
            return

        df = pd.DataFrame(dataset)
        df.to_parquet(path, index=False, compression='snappy')

    def save_metadata(
        self,
        output_path: Path,
        statistics: Dict[str, Any],
        config: Dict[str, Any]
    ):
        """保存处理元数据"""
        metadata_path = output_path / "metadata.json"

        metadata = {
            "created_at": datetime.now().isoformat(),
            "tool_version": "1.0.0",
            "statistics": statistics,
            "config": config
        }

        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        logger.info(f"元数据保存到: {metadata_path}")

    def merge_datasets(
        self,
        dataset_paths: List[Path],
        output_path: Path,
        deduplicate: bool = True
    ) -> Path:
        """合并多个数据集文件"""
        all_records = []

        for path in dataset_paths:
            logger.info(f"加载数据集: {path}")

            if path.suffix == '.jsonl':
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f:
                        all_records.append(json.loads(line.strip()))
            elif path.suffix == '.json':
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "dataset" in data:
                        all_records.extend(data["dataset"])
                    elif isinstance(data, list):
                        all_records.extend(data)
            elif path.suffix == '.parquet':
                df = pd.read_parquet(path)
                all_records.extend(df.to_dict('records'))

        logger.info(f"合并前总记录数: {len(all_records)}")

        # 去重（基于 content/text 字段）
        if deduplicate:
            seen = set()
            unique_records = []
            for record in all_records:
                content = record.get('text') or record.get('output') or str(record)
                if content not in seen:
                    seen.add(content)
                    unique_records.append(record)
            all_records = unique_records
            logger.info(f"去重后记录数: {len(all_records)}")

        # 保存合并后的数据集
        merged_path = output_path / f"merged_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{self.output_format}"
        self.save(all_records, output_path, f"merged_dataset")

        return merged_path
