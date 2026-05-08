"""
文本处理工具模块
提供各种文本处理相关的工具函数
"""

import hashlib
import re
from typing import List


class TextUtils:
    """文本处理工具类"""

    @staticmethod
    def truncate(text: str, max_length: int, suffix: str = "...") -> str:
        """
        截断文本到指定长度

        Args:
            text: 原始文本
            max_length: 最大长度
            suffix: 截断后添加的后缀

        Returns:
            截断后的文本
        """
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix

    @staticmethod
    def get_lines(text: str, count: int = 3) -> str:
        """
        获取文本的前几行

        Args:
            text: 原始文本
            count: 要获取的行数

        Returns:
            前几行文本
        """
        lines = text.split('\n')
        return '\n'.join(lines[:count])

    @staticmethod
    def strip_html(html: str) -> str:
        """
        移除HTML标签，只保留纯文本

        Args:
            html: HTML文本

        Returns:
            纯文本
        """
        # 简单的HTML标签移除
        clean = re.sub('<[^<]+?>', '', html)
        # 移除多余的空白
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean

    @staticmethod
    def is_code(text: str) -> bool:
        """
        判断文本是否可能是代码

        Args:
            text: 文本内容

        Returns:
            是否是代码
        """
        # 常见代码特征
        code_indicators = [
            'def ', 'function ', 'class ', 'import ', '#include',
            'public ', 'private ', 'void ', 'int ', 'str ', 'var ',
            'if ', 'for ', 'while ', 'return ', '=> ', '-> ',
            '{', '}', '(', ')', ';', 'self.', 'this.',
        ]

        text_lower = text.lower()
        for indicator in code_indicators:
            if indicator in text:
                return True

        return False

    @staticmethod
    def detect_language(text: str) -> str:
        """
        检测代码语言（简单版本）

        Args:
            text: 代码文本

        Returns:
            语言名称
        """
        text_lower = text.lower()

        if 'def ' in text and 'import ' in text:
            return 'python'
        elif 'function ' in text or '=> ' in text:
            return 'javascript'
        elif 'public ' in text and 'class ' in text:
            return 'java'
        elif '#include' in text:
            return 'c/cpp'
        elif '<?php' in text:
            return 'php'
        elif '<?xml' in text:
            return 'xml'
        elif '<html' in text or '<div' in text:
            return 'html'
        elif 'SELECT' in text or 'FROM' in text:
            return 'sql'

        return 'text'

    @staticmethod
    def get_hash(content: str) -> str:
        """
        获取内容的哈希值（用于去重）

        Args:
            content: 内容字符串

        Returns:
            MD5哈希值
        """
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """
        规范化空白字符

        Args:
            text: 原始文本

        Returns:
            规范化后的文本
        """
        return re.sub(r'\s+', ' ', text).strip()

    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """
        从文本中提取URL

        Args:
            text: 文本内容

        Returns:
            URL列表
        """
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return re.findall(url_pattern, text)

    @staticmethod
    def is_url(text: str) -> bool:
        """
        判断文本是否是URL

        Args:
            text: 文本内容

        Returns:
            是否是URL
        """
        url_pattern = r'^https?://[^\s<>"{}|\\^`\[\]]+$'
        return bool(re.match(url_pattern, text.strip()))
