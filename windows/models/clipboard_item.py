"""
剪贴板项数据模型
定义剪贴板历史记录的数据结构
"""

from datetime import datetime
from typing import Optional, List

from .enums import ContentType


class ClipboardItem:
    """剪贴板项数据模型"""

    def __init__(
        self,
        id: Optional[int] = None,
        content: str = "",
        content_type: ContentType = ContentType.TEXT,
        raw_data: Optional[bytes] = None,
        source_app: str = "",
        source_window_title: str = "",
        created_at: Optional[datetime] = None,
        is_favorite: bool = False,
        item_size: int = 0,
        file_list: Optional[List[str]] = None,
    ):
        self.id = id
        self.content = content  # 文本内容或图片路径
        self.content_type = content_type
        self.raw_data = raw_data  # 原始数据（可选）
        self.source_app = source_app  # 来源应用名称
        self.source_window_title = source_window_title  # 来源窗口标题
        self.created_at = created_at or datetime.now()
        self.is_favorite = is_favorite
        self.item_size = item_size  # 内容大小（字节）
        self.file_list = file_list or []  # 文件列表（当content_type为FILE时）
        self.content_hash = None  # 内容哈希，用于去重

    @property
    def preview_text(self) -> str:
        """获取预览文本"""
        if self.content_type == ContentType.TEXT:
            # 返回前几行文本
            lines = self.content.split('\n')[:3]
            return '\n'.join(lines)
        elif self.content_type == ContentType.HTML:
            return "HTML内容"
        elif self.content_type == ContentType.IMAGE:
            return "图片"
        elif self.content_type == ContentType.FILE:
            count = len(self.file_list) if self.file_list else 0
            return f"{count} 个文件"
        return ""

    @property
    def display_size(self) -> str:
        """获取格式化的显示大小"""
        if self.item_size < 1024:
            return f"{self.item_size} B"
        elif self.item_size < 1024 * 1024:
            return f"{self.item_size / 1024:.1f} KB"
        elif self.item_size < 1024 * 1024 * 1024:
            return f"{self.item_size / (1024 * 1024):.1f} MB"
        return f"{self.item_size / (1024 * 1024 * 1024):.1f} GB"

    @property
    def time_str(self) -> str:
        """获取时间字符串"""
        now = datetime.now()
        delta = now - self.created_at

        if delta.seconds < 60:
            return "刚刚"
        elif delta.seconds < 3600:
            minutes = delta.seconds // 60
            return f"{minutes} 分钟前"
        elif delta.days == 0:
            hours = delta.seconds // 3600
            return f"{hours} 小时前"
        elif delta.days == 1:
            return "昨天"
        elif delta.days < 7:
            return f"{delta.days} 天前"
        else:
            return self.created_at.strftime("%Y-%m-%d")

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'content': self.content,
            'content_type': self.content_type.value,
            'raw_data': self.raw_data,
            'source_app': self.source_app,
            'source_window_title': self.source_window_title,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_favorite': self.is_favorite,
            'item_size': self.item_size,
            'file_list': self.file_list,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ClipboardItem':
        """从字典创建"""
        created_at = None
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'])

        return cls(
            id=data.get('id'),
            content=data.get('content', ''),
            content_type=ContentType(data.get('content_type', 'text')),
            raw_data=data.get('raw_data'),
            source_app=data.get('source_app', ''),
            source_window_title=data.get('source_window_title', ''),
            created_at=created_at,
            is_favorite=data.get('is_favorite', False),
            item_size=data.get('item_size', 0),
            file_list=data.get('file_list', []),
        )

    def __repr__(self) -> str:
        return f"ClipboardItem(id={self.id}, type={self.content_type}, favorite={self.is_favorite})"
