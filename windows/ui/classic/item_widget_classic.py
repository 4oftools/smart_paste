"""
历史项控件模块
单个剪贴板历史记录的显示控件
"""

from pathlib import Path
from PyQt6.QtCore import Qt, QSize, QRect, pyqtSignal, QPoint, QMimeData, QByteArray
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QDrag, QImage
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
)
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve

from models.clipboard_item import ClipboardItem
from utils.theme import get_current_theme, _hex_to_rgb


class ItemWidget(QFrame):
    """单个剪贴板项控件"""

    # 信号：被点击
    clicked = pyqtSignal()
    # 信号：收藏状态改变
    favorite_toggled = pyqtSignal()

    def __init__(self, item: ClipboardItem, parent=None):
        super().__init__(parent)

        self.item = item
        self.is_selected = False
        self.is_hovered = False
        self.drag_start_pos = QPoint()

        self._init_ui()
        self._setup_style()

    def _init_ui(self) -> None:
        """初始化UI"""
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setFixedHeight(80)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QHBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        # 缩略图/图标
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(64, 64)
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 内容区域
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)

        # 主内容行
        self.content_label = QLabel()
        self.content_label.setWordWrap(True)
        self.content_label.setFont(QFont("Microsoft YaHei", 10))

        # 元信息行
        meta_layout = QHBoxLayout()
        meta_layout.setSpacing(12)

        # 来源应用
        self.app_label = QLabel()
        self.app_label.setFont(QFont("Microsoft YaHei", 8))

        # 时间
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Microsoft YaHei", 8))

        # 大小
        self.size_label = QLabel()
        self.size_label.setFont(QFont("Microsoft YaHei", 8))

        meta_layout.addWidget(self.app_label)
        meta_layout.addWidget(self.time_label)
        meta_layout.addWidget(self.size_label)
        meta_layout.addStretch()

        content_layout.addWidget(self.content_label)
        content_layout.addLayout(meta_layout)

        # 收藏按钮
        self.favorite_btn = QLabel()
        self.favorite_btn.setText("☆")
        self.favorite_btn.setFixedSize(30, 30)
        self.favorite_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.favorite_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.favorite_btn.mousePressEvent = self._on_favorite_clicked

        layout.addWidget(self.thumbnail_label)
        layout.addLayout(content_layout, 1)
        layout.addWidget(self.favorite_btn)

        self.setLayout(layout)

        # 设置内容
        self._update_content()

    def _update_content(self) -> None:
        """更新显示内容"""
        # 更新缩略图/图标
        if self.item.content_type.value == "image":
            # 显示图片缩略图（使用缓存）
            self._set_image_thumbnail()
        elif self.item.content_type.value == "file":
            self._set_placeholder_thumbnail("📁")
        else:
            self._set_placeholder_thumbnail("📝")

        # 更新内容文本
        preview_text = self.item.preview_text
        from utils.text_utils import TextUtils
        self.content_label.setText(TextUtils.truncate(preview_text, 80))

        # 更新元信息
        self.app_label.setText(f"📱 {self.item.source_app or 'Unknown'}")
        self.time_label.setText(f"🕐 {self.item.time_str}")
        self.size_label.setText(f"📦 {self.item.display_size}")

        # 更新收藏状态
        self._update_favorite_icon()

    def _set_image_thumbnail(self) -> None:
        """设置图片缩略图（使用缓存）"""
        image_path = Path(self.item.content)
        if not image_path.exists():
            self._set_placeholder_thumbnail("🖼️")
            return

        # 检查是否有缓存的缩略图
        thumbnail_path = self._get_thumbnail_path(image_path)
        if thumbnail_path.exists():
            pixmap = QPixmap(str(thumbnail_path))
            if not pixmap.isNull():
                self.thumbnail_label.setPixmap(pixmap)
                return

        # 没有缓存，创建新的缩略图
        self._create_and_cache_thumbnail(image_path)

    def _get_thumbnail_path(self, image_path: Path) -> Path:
        """获取缩略图缓存路径"""
        from config import settings
        # 使用文件名的哈希作为缩略图文件名
        import hashlib
        hash_value = hashlib.md5(str(image_path).encode()).hexdigest()
        return settings.image_cache_dir / f"thumb_{hash_value}.png"

    def _create_and_cache_thumbnail(self, image_path: Path) -> None:
        """创建并缓存缩略图"""
        pixmap = QPixmap(str(image_path))
        if pixmap.isNull():
            self._set_placeholder_thumbnail("🖼️")
            return

        # 创建缩略图
        scaled = pixmap.scaled(
            60, 60,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        # 保存到缓存
        thumbnail_path = self._get_thumbnail_path(image_path)
        scaled.save(str(thumbnail_path))

        self.thumbnail_label.setPixmap(scaled)

    def _set_placeholder_thumbnail(self, emoji: str) -> None:
        """设置占位缩略图（使用当前主题的 placeholder 色）"""
        theme = get_current_theme()
        placeholder_bg = theme.get('placeholder_bg', 'rgba(255, 255, 255, 0.06)')
        self.thumbnail_label.setText(emoji)
        self.thumbnail_label.setStyleSheet(f"""
            QLabel {{
                font-size: 32px;
                background-color: {placeholder_bg};
                border-radius: 8px;
            }}
        """)

    def _update_favorite_icon(self) -> None:
        """更新收藏图标"""
        theme = get_current_theme()
        if self.item.is_favorite:
            self.favorite_btn.setText("⭐")
            self.favorite_btn.setStyleSheet(f"""
                QLabel {{
                    color: {theme['warning']};
                    font-size: 20px;
                }}
            """)
        else:
            self.favorite_btn.setText("☆")
            self.favorite_btn.setStyleSheet(f"""
                QLabel {{
                    color: {theme['text_muted']};
                    font-size: 20px;
                }}
            """)

    def _on_favorite_clicked(self, event) -> None:
        """收藏按钮点击处理"""
        self.item.is_favorite = not self.item.is_favorite
        self._update_favorite_icon()
        self.favorite_toggled.emit()

    def _setup_style(self) -> None:
        """设置样式"""
        theme = get_current_theme()
        self.setStyleSheet(f"""
            ItemWidget {{
                background-color: {theme['surface']};
                border-radius: 8px;
                border: 2px solid transparent;
            }}

            ItemWidget:hover {{
                background-color: {theme['border']};
            }}

            ItemWidget[selected="true"] {{
                background-color: {theme['accent']};
                border: 2px solid {theme['accent_hover']};
            }}

            QLabel {{
                color: {theme['text']};
                background: transparent;
            }}
        """)

        self.setProperty("selected", "false")

    def set_selected(self, selected: bool) -> None:
        """设置选中状态"""
        self.is_selected = selected
        self.setProperty("selected", "true" if selected else "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def update_item(self, item: ClipboardItem) -> None:
        """更新项内容"""
        self.item = item
        self._update_content()

    def mousePressEvent(self, event) -> None:
        """鼠标点击处理"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_pos = event.pos()
            self.clicked.emit()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        """鼠标移动处理（拖拽）"""
        if not event.buttons() & Qt.MouseButton.LeftButton:
            super().mouseMoveEvent(event)
            return

        # 检查拖拽距离阈值
        if (event.pos() - self.drag_start_pos).manhattanLength() < 10:
            super().mouseMoveEvent(event)
            return

        # 开始拖拽
        drag = QDrag(self)
        mime_data = QMimeData()

        if self.item.content_type.value == "image":
            # 拖拽图片
            pixmap = QPixmap(str(self.item.content))
            if not pixmap.isNull():
                mime_data.setImageData(pixmap)
                drag.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
        elif self.item.content_type.value == "file" and self.item.file_list:
            # 拖拽文件
            from PyQt6.QtCore import QUrl
            urls = [QUrl.fromLocalFile(f) for f in self.item.file_list]
            mime_data.setUrls(urls)
        else:
            # 拖拽文本
            mime_data.setText(self.item.content)
            drag.setPixmap(self._create_text_pixmap(self.item.content[:50]))

        drag.setMimeData(mime_data)
        drag.exec(Qt.DropAction.CopyAction)

    def enterEvent(self, event) -> None:
        """鼠标进入"""
        self.is_hovered = True
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        """鼠标离开"""
        self.is_hovered = False
        super().leaveEvent(event)

    def _create_text_pixmap(self, text: str) -> QImage:
        """创建文本缩略图（使用当前主题色）"""
        theme = get_current_theme()
        r, g, b = _hex_to_rgb(theme['surface'])
        bg_color = QColor(r, g, b, 230)
        r, g, b = _hex_to_rgb(theme['text'])
        text_color = QColor(r, g, b)

        pixmap = QImage(200, 60, QImage.Format.Format_ARGB32)
        pixmap.fill(bg_color)

        painter = QPainter(pixmap)
        painter.setPen(text_color)
        painter.setFont(QFont("Microsoft YaHei", 10))
        painter.drawText(QRect(10, 10, 180, 40), Qt.TextFlag.TextWordWrap, text)
        painter.end()

        return pixmap
