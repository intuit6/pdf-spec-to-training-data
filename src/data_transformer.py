"""数据转换模块

负责将解析后的 PDF 内容清洗、分块、转换为训练数据格式。
支持多种分块策略和清洗规则。
"""

import re
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class TextChunk:
    """文本块数据结构"""
    chunk_id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_char: int = 0
    end_char: int = 0
    source_page: Optional[int] = None


class TextCleaner:
    """文本清洗器"""

    def __init__(
        self,
        normalize_whitespace: bool = True,
        remove_control_chars: bool = True,
        normalize_punctuation: bool = True,
        remove_patterns: List[str] = None
    ):
        self.normalize_whitespace = normalize_whitespace
        self.remove_control_chars = remove_control_chars
        self.normalize_punctuation = normalize_punctuation
        self.remove_patterns = remove_patterns or []

        # 编译正则
        self.whitespace_re = re.compile(r'\s+')
        self.control_chars_re = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]')
        self.punctuation_map = {
            # 全角转半角
            '，': ',', '。': '.', '！': '!', '？': '?',
            '；': ';', '：': ':', '（': '(', '）': ')',
            '【': '[', '】': ']', '《': '"', '》': '"',
            '"': '"', ''': "'", ''': "'",
            '～': '~', '—': '-', '－': '-', '　': ' ',
        }
        self.punctuation_re = re.compile('|'.join(map(re.escape, self.punctuation_map.keys())))

        self.remove_patterns_re = [re.compile(pattern) for pattern in self.remove_patterns]

    def clean(self, text: str) -> str:
        """清洗文本"""
        if not text:
            return ""

        result = text

        # 移除指定模式
        for pattern_re in self.remove_patterns_re:
            result = pattern_re.sub('', result)

        # 规范化空白字符
        if self.normalize_whitespace:
            result = self.whitespace_re.sub(' ', result)
            result = result.strip()

        # 移除控制字符
        if self.remove_control_chars:
            result = self.control_chars_re.sub('', result)

        # 规范化标点符号
        if self.normalize_punctuation:
            result = self.punctuation_re.sub(lambda m: self.punctuation_map[m.group()], result)

        return result


class HeaderFooterRemover:
    """页眉页脚移除器"""

    def __init__(
        self,
        keywords: List[str] = None,
        margin_ratio: float = 0.15
    ):
        self.keywords = keywords or ["第", "页", "Page", "Copyright", "©"]
        self.margin_ratio = margin_ratio

    def is_margin_content(self, lines: List[str], total_lines: int) -> List[bool]:
        """识别哪些行可能是页眉页脚（基于位置）"""
        margin_lines = []
        margin_threshold = int(total_lines * self.margin_ratio)

        for i in range(total_lines):
            is_margin = i < margin_threshold or i >= total_lines - margin_threshold
            margin_lines.append(is_margin)

        return margin_lines

    def remove(self, lines: List[str]) -> List[str]:
        """移除页眉页脚"""
        if not lines:
            return []

        total_lines = len(lines)
        margin_lines = self.is_margin_content(lines, total_lines)

        filtered_lines = []
        for i, line in enumerate(lines):
            # 检查是否为页眉页脚
            if margin_lines[i]:
                # 检查是否包含关键词
                if any(keyword in line for keyword in self.keywords):
                    continue  # 跳过页眉页脚

            filtered_lines.append(line)

        return filtered_lines


class TextChunker:
    """文本分块器

    支持多种分块策略：
    - fixed: 固定长度分块
    - paragraph: 按段落分块
    - chapter: 按章节分块
    - page: 按页分块
    - none: 不分块
    """

    def __init__(
        self,
        strategy: str = "paragraph",
        max_chunk_size: int = 1000,
        overlap: int = 100,
        chapter_patterns: List[str] = None
    ):
        self.strategy = strategy
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

        # 章节识别模式
        self.chapter_patterns = chapter_patterns or [
            r'^第[零一二三四五六七八九十百千万\d]+章',
            r'^\d+\.\d+',
            r'^[A-Z]\.\s+',
            r'^第\s*[零一二三四五六七八九十\d]+\s*章',
        ]
        self.chapter_regex = re.compile('|'.join(self.chapter_patterns))

        # 段落分隔符
        self.paragraph_separators = ['\n\n', '\r\n\r\n']

    def chunk_text(self, text: str, page_num: int = None, **kwargs) -> List[TextChunk]:
        """分块文本

        Args:
            text: 原始文本
            page_num: 源页码（可选）
            **kwargs: 额外元数据

        Returns:
            文本块列表
        """
        if not text:
            return []

        strategy_map = {
            "fixed": self._chunk_fixed,
            "paragraph": self._chunk_by_paragraph,
            "chapter": self._chunk_by_chapter,
            "page": self._chunk_by_page,
            "none": self._chunk_none
        }

        if self.strategy not in strategy_map:
            raise ValueError(f"不支持的分块策略: {self.strategy}")

        chunks = strategy_map[self.strategy](text, page_num)

        # 为每个块添加元数据
        for i, chunk in enumerate(chunks):
            chunk.chunk_id = str(uuid.uuid4())[:8]
            chunk.metadata.update({
                "chunk_index": i,
                "chunk_strategy": self.strategy,
                "source_page": page_num,
                **kwargs
            })

        return chunks

    def _chunk_fixed(self, text: str, page_num: int) -> List[TextChunk]:
        """固定长度分块（带重叠）"""
        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + self.max_chunk_size, text_len)

            # 尝试在合适的位置断开（如标点、空格）
            if end < text_len:
                # 查找最近的分隔点
                sep_pos = self._find_separator(text, end, direction='backward')
                if sep_pos > start + self.max_chunk_size // 2:
                    end = sep_pos

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunk = TextChunk(
                    chunk_id="",
                    content=chunk_text,
                    start_char=start,
                    end_char=end
                )
                chunks.append(chunk)

            # 计算下一步起始位置（考虑重叠）
            start = end - self.overlap if self.overlap > 0 else end

        return chunks

    def _chunk_by_paragraph(self, text: str, page_num: int) -> List[TextChunk]:
        """按段落分块"""
        # 按段落分隔符分割
        paragraphs = []
        for sep in self.paragraph_separators:
            if sep in text:
                paragraphs = text.split(sep)
                break

        if not paragraphs:
            paragraphs = [text]

        # 合并短段落，确保不要超过最大块大小
        chunks = []
        current_chunk = []
        current_length = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            para_len = len(para)

            if current_length + para_len > self.max_chunk_size and current_chunk:
                # 保存当前块
                chunk_text = '\n\n'.join(current_chunk)
                chunks.append(TextChunk(
                    chunk_id="",
                    content=chunk_text,
                    start_char=0,
                    end_char=len(chunk_text)
                ))
                current_chunk = [para]
                current_length = para_len
            else:
                current_chunk.append(para)
                current_length += para_len

        # 处理最后一个块
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            chunks.append(TextChunk(
                chunk_id="",
                content=chunk_text,
                start_char=0,
                end_char=len(chunk_text)
            ))

        return chunks

    def _chunk_by_chapter(self, text: str, page_num: int) -> List[TextChunk]:
        """按章节分块"""
        lines = text.split('\n')
        chunks = []
        current_chapter = []
        current_chapter_title = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 检查是否是章节标题
            if self.chapter_regex.match(line):
                # 保存上一章
                if current_chapter:
                    chunk_text = '\n'.join(current_chapter)
                    chunks.append(TextChunk(
                        chunk_id="",
                        content=chunk_text,
                        metadata={"chapter_title": current_chapter_title},
                        start_char=0,
                        end_char=len(chunk_text)
                    ))

                # 开始新章节
                current_chapter = [line]
                current_chapter_title = line
            else:
                current_chapter.append(line)

        # 保存最后一章
        if current_chapter:
            chunk_text = '\n'.join(current_chapter)
            chunks.append(TextChunk(
                chunk_id="",
                content=chunk_text,
                metadata={"chapter_title": current_chapter_title},
                start_char=0,
                end_char=len(chunk_text)
            ))

        # 如果章节太少或找不到章节，回退到段落分块
        if len(chunks) <= 1:
            return self._chunk_by_paragraph(text, page_num)

        return chunks

    def _chunk_by_page(self, text: str, page_num: int) -> List[TextChunk]:
        """按页分块（忽略分页符）"""
        # 实际上这一步不做分块，只是包装成单个块
        return [TextChunk(
            chunk_id="",
            content=text.strip(),
            start_char=0,
            end_char=len(text)
        )]

    def _chunk_none(self, text: str, page_num: int) -> List[TextChunk]:
        """不分块"""
        return [TextChunk(
            chunk_id="",
            content=text.strip(),
            start_char=0,
            end_char=len(text)
        )]

    def _find_separator(self, text: str, pos: int, direction: str = 'backward') -> int:
        """查找合适的分隔位置"""
        if direction == 'backward':
            # 向后查找最近的分隔符
            for i in range(pos, max(0, pos - 100), -1):
                if text[i] in '。.!?;；\n':
                    return i + 1
        else:
            # 向前查找
            for i in range(pos, min(len(text), pos + 100)):
                if text[i] in '。.!?;；\n':
                    return i + 1

        return pos


class DataTransformer:
    """数据转换器

    将解析后的 PDF 页面内容转换为训练数据。
    支持文本清洗、分块、添加元数据等操作。
    """

    def __init__(
        self,
        cleaner: TextCleaner = None,
        chunker: TextChunker = None,
        header_footer_remover: HeaderFooterRemover = None
    ):
        self.cleaner = cleaner or TextCleaner()
        self.chunker = chunker or TextChunker()
        self.hf_remover = header_footer_remover or HeaderFooterRemover()

    def transform_pages(
        self,
        pages_content: List[Any],
        include_metadata: bool = True,
        min_text_length: int = 10
    ) -> List[TextChunk]:
        """转换页面内容为文本块

        Args:
            pages_content: 页面内容列表
            include_metadata: 是否包含元数据
            min_text_length: 最小文本长度过滤

        Returns:
            文本块列表
        """
        all_chunks = []

        for page in pages_content:
            # 清洗文本
            cleaned_text = self.cleaner.clean(page.text)

            # 按行分割并移除页眉页脚
            lines = cleaned_text.split('\n')
            filtered_lines = self.hf_remover.remove(lines)
            final_text = '\n'.join(filtered_lines)

            # 分块
            if len(final_text) >= min_text_length:
                chunks = self.chunker.chunk_text(
                    final_text,
                    page_num=page.page_num,
                    source_file=page.metadata.get("source_file", "")
                )
                all_chunks.extend(chunks)

        logger.info(f"生成了 {len(all_chunks)} 个文本块")
        return all_chunks

    def merge_with_tables(
        self,
        text_chunks: List[TextChunk],
        tables_by_page: Dict[int, List[Dict[str, Any]]]
    ) -> List[TextChunk]:
        """将表格数据合并到文本块中

        Args:
            text_chunks: 文本块列表
            tables_by_page: 按页分组的表格数据

        Returns:
            合并后的文本块列表
        """
        merged_chunks = []

        for chunk in text_chunks:
            page_num = chunk.metadata.get("source_page")
            if page_num and page_num in tables_by_page:
                tables = tables_by_page[page_num]
                table_texts = []

                for table in tables:
                    # 将表格转换为 Markdown 格式
                    table_text = self._format_table_as_markdown(table["data"])
                    table_texts.append(f"\n\n[表格 {table['table_id']}]\n{table_text}")

                # 将表格添加到块末尾
                chunk.content += ''.join(table_texts)
                chunk.metadata["has_table"] = True
                chunk.metadata["table_count"] = len(tables)

            merged_chunks.append(chunk)

        return merged_chunks

    def _format_table_as_markdown(self, table_data: List[List[str]]) -> str:
        """将表格数据格式化为 Markdown"""
        if not table_data:
            return ""

        lines = []
        for i, row in enumerate(table_data):
            # 清理每个单元格
            cells = [str(cell).strip() if cell else "" for cell in row]
            line = "| " + " | ".join(cells) + " |"
            lines.append(line)

            # 添加表头分隔线（仅第一行后）
            if i == 0:
                separator = "| " + " | ".join(["---"] * len(row)) + " |"
                lines.append(separator)

        return '\n'.join(lines)

    def create_qa_pairs(
        self,
        text_chunks: List[TextChunk],
        question_templates: List[str] = None
    ) -> List[Dict[str, str]]:
        """从文本块生成问答对（启发式）"""
        if question_templates is None:
            question_templates = [
                "请总结以下内容：{content}",
                "提取关键信息：{content}",
                "解释以下概念：{content}"
            ]

        qa_pairs = []

        for chunk in text_chunks:
            # 简化处理：截取前200字符作为内容
            short_content = chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content

            for template in question_templates:
                question = template.format(content=short_content)
                qa_pairs.append({
                    "instruction": question,
                    "input": "",
                    "output": chunk.content,
                    "source_chunk_id": chunk.chunk_id
                })

        return qa_pairs


class MetaDataEnhancer:
    """元数据增强器

    为数据块添加额外的元数据信息：
    - 来源文档信息
    - 提取时间
    - 内容类型
    - 质量评分
    """

    def __init__(self):
        self.extraction_time = datetime.now().isoformat()

    def enhance(
        self,
        chunk: TextChunk,
        document_metadata: Dict[str, Any],
        statistics: Dict[str, Any]
    ) -> TextChunk:
        """增强块元数据"""
        chunk.metadata.update({
            "extraction_time": self.extraction_time,
            "document": document_metadata.get("filename", ""),
            "document_title": document_metadata.get("title", ""),
            "total_pages": document_metadata.get("total_pages", 0),
            "chunk_length": len(chunk.content),
            "word_count": len(chunk.content.split()),
            "char_count": len(chunk.content),
            "extraction_stats": statistics
        })

        # 基于内容特征推断类型
        chunk.metadata["content_type"] = self._infer_content_type(chunk.content)

        return chunk

    def _infer_content_type(self, content: str) -> str:
        """推断内容类型"""
        content_lower = content.lower()

        # 检测是否为表格
        if '|' in content and '-|-' in content:
            return "table"

        # 检测是否为列表
        if re.search(r'^[•\-*•◎○▪]', content, re.MULTILINE):
            return "list"

        # 检测是否为代码
        if re.search(r'```|def |class |function ', content):
            return "code"

        # 检测章节标题特征
        if re.match(r'^第[零一二三四五六七八九十百千万\d]+章', content):
            return "heading"

        return "text"
