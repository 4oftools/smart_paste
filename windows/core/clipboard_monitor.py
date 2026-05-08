"""
剪贴板监听模块
监听Windows剪贴板变化，捕获复制的内容
"""

import io
import sys
from pathlib import Path
from typing import Optional, Callable
from datetime import datetime

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QApplication

from models.clipboard_item import ClipboardItem
from models.enums import ContentType
from utils.image_utils import ImageUtils
from utils.text_utils import TextUtils
from utils.app_detector import AppDetector
from utils.logger import get_logger

# 获取日志器
logger = get_logger('ClipboardMonitor')


class ClipboardMonitor(QObject):
    """剪贴板监听器"""

    # 信号：检测到新剪贴板内容
    new_content = pyqtSignal(ClipboardItem)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.clipboard = QApplication.clipboard()
        self.last_content = None
        self.last_content_hash = None

        # 连接剪贴板变化信号
        self.clipboard.dataChanged.connect(self._on_clipboard_changed)

        # 应用检测器
        self.app_detector = AppDetector()

        logger.info("Clipboard monitor initialized")

    def _on_clipboard_changed(self) -> None:
        """剪贴板内容变化处理"""
        try:
            item = self._create_clipboard_item()
            if item and item.content_hash != self.last_content_hash:
                self.last_content_hash = item.content_hash
                logger.debug(f"New clipboard content detected: {item.content_type.value}")
                self.new_content.emit(item)
        except Exception as e:
            # 静默处理错误，避免影响用户体验
            logger.error(f"Error processing clipboard change: {e}", exc_info=True)

    def _create_clipboard_item(self) -> Optional[ClipboardItem]:
        """
        从当前剪贴板内容创建剪贴板项

        Returns:
            剪贴板项对象，如果无法创建则返回None
        """
        mime_data = self.clipboard.mimeData()

        # 获取来源应用信息
        source_app, source_window_title = self.app_detector.get_active_window_info()

        content_type = self._detect_content_type(mime_data)

        item = None
        if content_type == ContentType.IMAGE:
            item = self._create_image_item(mime_data, source_app, source_window_title)
        elif content_type == ContentType.FILE:
            item = self._create_file_item(mime_data, source_app, source_window_title)
        elif content_type == ContentType.HTML:
            item = self._create_html_item(mime_data, source_app, source_window_title)
        elif content_type == ContentType.TEXT:
            item = self._create_text_item(mime_data, source_app, source_window_title)

        # 计算内容哈希（用于去重）
        if item:
            item.content_hash = self._compute_content_hash(item)

        return item

    def _compute_content_hash(self, item: ClipboardItem) -> str:
        """
        计算内容哈希（用于去重）

        Args:
            item: 剪贴板项

        Returns:
            内容哈希
        """
        import hashlib
        if item.content_type == ContentType.IMAGE:
            # 对于图片，使用内容的哈希
            return hashlib.md5(item.content.encode('utf-8')).hexdigest()
        else:
            # 对于文本等，使用内容本身
            return hashlib.md5(item.content.encode('utf-8')).hexdigest()

    def _detect_content_type(self, mime_data) -> ContentType:
        """
        检测剪贴板内容类型

        Args:
            mime_data: MIME数据对象

        Returns:
            内容类型
        """
        # 优先级：图片 > 文件 > HTML > 文本
        # 图片优先级最高，因为复制图片时某些应用可能同时设置URL
        
        from config import settings
        
        if mime_data.hasImage() and settings.get('enable_image', True):
            return ContentType.IMAGE

        if mime_data.hasUrls():
            urls = mime_data.urls()
            # 检查是否是文件URL
            if urls and urls[0].isLocalFile() and settings.get('enable_file', True):
                return ContentType.FILE

        if mime_data.hasHtml() and settings.get('enable_html', True):
            return ContentType.HTML

        if mime_data.hasText() and settings.get('enable_text', True):
            return ContentType.TEXT

        return ContentType.TEXT  # 默认

    def _create_text_item(
        self,
        mime_data,
        source_app: str,
        source_window_title: str
    ) -> Optional[ClipboardItem]:
        """创建文本类型的剪贴板项"""
        text = mime_data.text()
        if not text or text.strip() == "":
            return None

        # 检查文本长度，避免记录过长内容
        max_text_size = 1024 * 1024  # 1MB
        if len(text.encode('utf-8')) > max_text_size:
            return None

        return ClipboardItem(
            content=text,
            content_type=ContentType.TEXT,
            source_app=source_app or "",
            source_window_title=source_window_title or "",
            created_at=datetime.now(),
            item_size=len(text.encode('utf-8')),
        )

    def _create_image_item(
        self,
        mime_data,
        source_app: str,
        source_window_title: str
    ) -> Optional[ClipboardItem]:
        """创建图片类型的剪贴板项"""
        # 从剪贴板获取图片
        image = self.clipboard.image()
        if image.isNull():
            return None

        # 保存图片到缓存目录
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f"clipboard_{timestamp}.png"
        image_path = ImageUtils.get_cache_path(filename)

        try:
            # 保存原始图片
            image.save(str(image_path))

            # 计算大小
            image_size = image_path.stat().st_size

            # 限制图片大小，避免存储过大图片
            max_image_size = 50 * 1024 * 1024  # 50MB
            if image_size > max_image_size:
                logger.warning(f"Image too large ({image_size / (1024*1024):.1f}MB), skipping")
                image_path.unlink(missing_ok=True)
                return None

            logger.debug(f"Image saved: {image_path.name} ({image_size / 1024:.1f}KB)")

            return ClipboardItem(
                content=str(image_path),  # 存储图片路径
                content_type=ContentType.IMAGE,
                source_app=source_app or "",
                source_window_title=source_window_title or "",
                created_at=datetime.now(),
                item_size=image_size,
            )
        except Exception as e:
            logger.error(f"Error saving image: {e}", exc_info=True)
            return None

    def _create_file_item(
        self,
        mime_data,
        source_app: str,
        source_window_title: str
    ) -> Optional[ClipboardItem]:
        """创建文件类型的剪贴板项"""
        urls = mime_data.urls()
        if not urls:
            return None

        file_list = []
        total_size = 0

        for url in urls:
            if url.isLocalFile():
                file_path = url.toLocalFile()
                if Path(file_path).exists():
                    file_list.append(file_path)
                    try:
                        total_size += Path(file_path).stat().st_size
                    except Exception:
                        pass

        if not file_list:
            return None

        # 限制文件数量
        max_files = 100
        if len(file_list) > max_files:
            file_list = file_list[:max_files]
            logger.warning(f"File list truncated to {max_files} items")

        logger.debug(f"Files captured: {len(file_list)} items, {total_size / 1024:.1f}KB")

        return ClipboardItem(
            content=f"{len(file_list)} files",  # 简短描述
            content_type=ContentType.FILE,
            source_app=source_app or "",
            source_window_title=source_window_title or "",
            created_at=datetime.now(),
            item_size=total_size,
            file_list=file_list,
        )

    def _create_html_item(
        self,
        mime_data,
        source_app: str,
        source_window_title: str
    ) -> Optional[ClipboardItem]:
        """创建HTML类型的剪贴板项"""
        html = mime_data.html()
        text = mime_data.text()

        # 如果只有HTML没有文本，提取纯文本
        if not text or text.strip() == "":
            text = TextUtils.strip_html(html)

        if not text or text.strip() == "":
            return None

        # 检查内容大小
        max_size = 1024 * 1024  # 1MB
        content_size = len(html.encode('utf-8'))
        if content_size > max_size:
            # 内容过大，只存储文本
            content_type = ContentType.TEXT
            content = text
            content_size = len(text.encode('utf-8'))
        else:
            content_type = ContentType.HTML
            content = html

        return ClipboardItem(
            content=content,
            content_type=content_type,
            source_app=source_app or "",
            source_window_title=source_window_title or "",
            created_at=datetime.now(),
            item_size=content_size,
        )

    def get_current_content(self) -> Optional[ClipboardItem]:
        """
        获取当前剪贴板内容

        Returns:
            剪贴板项对象
        """
        return self._create_clipboard_item()

    @staticmethod
    def set_content(item: ClipboardItem) -> bool:
        """
        将剪贴板项内容设置到剪贴板

        Args:
            item: 剪贴板项

        Returns:
            是否成功
        """
        clipboard = QApplication.clipboard()

        try:
            if item.content_type == ContentType.IMAGE:
                # 加载图片并设置
                image = QImage(str(item.content))
                if not image.isNull():
                    clipboard.setImage(image)
                    logger.debug(f"Copied image to clipboard")
                    return True
                else:
                    logger.error(f"Failed to load image: {item.content}")
                    return False
            elif item.content_type == ContentType.FILE:
                # 设置文件列表到剪贴板
                from PyQt6.QtCore import QMimeData, QUrl
                mime_data = QMimeData()
                urls = [QUrl.fromLocalFile(f) for f in item.file_list if f]
                if urls:
                    mime_data.setUrls(urls)
                    clipboard.setMimeData(mime_data)
                    logger.debug(f"Copied {len(urls)} files to clipboard")
                    return True
                else:
                    logger.warning("No valid file paths to copy")
                    return False
            elif item.content_type == ContentType.HTML:
                # 设置HTML内容
                from PyQt6.QtCore import QMimeData
                mime_data = QMimeData()
                mime_data.setHtml(item.content)
                mime_data.setText(item.content)  # 同时设置纯文本
                clipboard.setMimeData(mime_data)
                logger.debug("Copied HTML content to clipboard")
                return True
            elif item.content_type == ContentType.TEXT:
                # 设置文本
                clipboard.setText(item.content)
                logger.debug(f"Copied text to clipboard ({len(item.content)} chars)")
                return True

            return False
        except Exception as e:
            logger.error(f"Error setting clipboard content: {e}", exc_info=True)
            return False
