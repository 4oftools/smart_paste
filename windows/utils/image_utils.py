"""
图片处理工具模块
提供各种图片处理相关的工具函数
"""

import base64
import hashlib
import io
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image, ImageOps


class ImageUtils:
    """图片处理工具类"""

    @staticmethod
    def create_thumbnail(
        image: Image.Image,
        size: int = 200
    ) -> Image.Image:
        """
        创建图片缩略图

        Args:
            image: PIL图片对象
            size: 缩略图尺寸（正方形）

        Returns:
            缩略图
        """
        image = ImageOps.fit(image, (size, size), Image.LANCZOS)
        return image

    @staticmethod
    def image_to_base64(image: Image.Image, format: str = "PNG") -> str:
        """
        将图片转换为Base64字符串

        Args:
            image: PIL图片对象
            format: 图片格式

        Returns:
            Base64字符串
        """
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        return base64.b64encode(buffer.getvalue()).decode()

    @staticmethod
    def base64_to_image(base64_str: str) -> Optional[Image.Image]:
        """
        将Base64字符串转换为图片

        Args:
            base64_str: Base64字符串

        Returns:
            PIL图片对象
        """
        try:
            image_data = base64.b64decode(base64_str)
            return Image.open(io.BytesIO(image_data))
        except Exception:
            return None

    @staticmethod
    def save_image(image: Image.Image, path: Path) -> bool:
        """
        保存图片到文件

        Args:
            image: PIL图片对象
            path: 保存路径

        Returns:
            是否成功
        """
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            image.save(path)
            return True
        except Exception:
            return False

    @staticmethod
    def load_image(path: Path) -> Optional[Image.Image]:
        """
        从文件加载图片

        Args:
            path: 图片路径

        Returns:
            PIL图片对象
        """
        try:
            return Image.open(path)
        except Exception:
            return None

    @staticmethod
    def get_image_hash(image: Image.Image) -> str:
        """
        获取图片的哈希值（用于去重）

        Args:
            image: PIL图片对象

        Returns:
            MD5哈希值
        """
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return hashlib.md5(buffer.getvalue()).hexdigest()

    @staticmethod
    def get_image_size(image: Image.Image) -> Tuple[int, int]:
        """
        获取图片尺寸

        Args:
            image: PIL图片对象

        Returns:
            (宽度, 高度)
        """
        return image.size

    @staticmethod
    def resize_image(
        image: Image.Image,
        max_width: int = 1920,
        max_height: int = 1080
    ) -> Image.Image:
        """
        调整图片大小，保持宽高比

        Args:
            image: PIL图片对象
            max_width: 最大宽度
            max_height: 最大高度

        Returns:
            调整后的图片
        """
        width, height = image.size

        if width <= max_width and height <= max_height:
            return image

        ratio = min(max_width / width, max_height / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)

        return image.resize((new_width, new_height), Image.LANCZOS)

    @staticmethod
    def get_file_size_str(size: int) -> str:
        """
        格式化文件大小

        Args:
            size: 文件大小（字节）

        Returns:
            格式化后的字符串
        """
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        return f"{size / (1024 * 1024 * 1024):.1f} GB"

    @staticmethod
    def get_cache_path(filename: str) -> Path:
        """
        获取图片缓存路径

        Args:
            filename: 文件名

        Returns:
            缓存文件路径
        """
        from config import settings
        return settings.image_cache_dir / filename
