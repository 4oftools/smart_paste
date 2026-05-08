"""
枚举类型定义
定义应用程序中使用的各种枚举类型
"""

from enum import Enum


class ContentType(Enum):
    """内容类型枚举"""
    TEXT = "text"           # 纯文本
    HTML = "html"           # HTML/富文本
    IMAGE = "image"         # 图片
    FILE = "file"           # 文件列表


class FilterType(Enum):
    """过滤类型枚举"""
    ALL = "all"             # 全部
    TEXT = "text"           # 仅文本
    IMAGE = "image"         # 仅图片
    FILE = "file"           # 仅文件
    FAVORITE = "favorite"   # 仅收藏


class SortType(Enum):
    """排序类型枚举"""
    NEWEST = "newest"       # 最新优先
    OLDEST = "oldest"       # 最旧优先
    SIZE_DESC = "size_desc" # 大小降序
    SIZE_ASC = "size_asc"   # 大小升序
