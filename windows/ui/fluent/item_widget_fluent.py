"""
历史项控件模块 - Fluent 设计风格
使用 Fluent 卡片组件
"""

from pathlib import Path
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPoint, QMimeData, QByteArray
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QDrag, QImage
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
)
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve

try:
    from PyQtFluentWidgets import CardWidget
    USE_FLUENT = True
except ImportError:
    USE_FLUENT = False
    CardWidget = QFrame

from models.clipboard_item import ClipboardItem
from utils.theme import get_current_theme
from utils.fluent_icons import FluentIcons, get_icon, get_icon_font


class ItemWidget(CardWidget if USE_FLUENT else QFrame):
    """历史项控件 - Fluent 卡片样式"""

    clicked = pyqtSignal()
    favorite_toggled = pyqtSignal()

    def __init__(self, item: ClipboardItem, parent=None):
        super().__init__(parent)
        
        self.item = item
        self.is_selected = False
        self.is_hovered = False
        self.drag_start_pos = QPoint()
        
        # 启用鼠标跟踪
        self.setMouseTracking(True)
        
        # 设置 Fluent 样式
        if USE_FLUENT:
            self.setBorderRadius(8)
            self.setHoverEnabled(True)
        
        self._init_ui()
        self._setup_style()
        self._update_content()

    def _init_ui(self) -> None:
        """初始化 UI"""
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
        self.thumbnail_label.setObjectName("thumbnail")

        # 内容区域
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(4)

        # 内容文本
        self.content_label = QLabel()
        self.content_label.setWordWrap(True)
        self.content_label.setFont(QFont("Microsoft YaHei", 10))
        self.content_label.setObjectName("content_label")
        content_layout.addWidget(self.content_label)

        # 元信息行
        meta_layout = QHBoxLayout()
        meta_layout.setSpacing(12)

        # 来源应用
        self.app_label = QLabel()
        self.app_label.setFont(QFont("Microsoft YaHei", 8))
        self.app_label.setObjectName("meta_label")
        meta_layout.addWidget(self.app_label)

        # 时间
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Microsoft YaHei", 8))
        self.time_label.setObjectName("meta_label")
        meta_layout.addWidget(self.time_label)

        # 大小
        self.size_label = QLabel()
        self.size_label.setFont(QFont("Microsoft YaHei", 8))
        self.size_label.setObjectName("meta_label")
        meta_layout.addWidget(self.size_label)

        meta_layout.addStretch()
        content_layout.addLayout(meta_layout)

        # 收藏按钮
        self.favorite_btn = QLabel()
        self.favorite_btn.setText("☆")
        self.favorite_btn.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        self.favorite_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.favorite_btn.setObjectName("favorite_btn")
        self.favorite_btn.mousePressEvent = self._on_favorite_clicked
        content_layout.addWidget(self.favorite_btn)

        content_widget.setLayout(content_layout)

        layout.addWidget(self.thumbnail_label)
        layout.addWidget(content_widget, 1)

        self.setLayout(layout)

    def _setup_style(self) -> None:
        """设置样式"""
        theme = get_current_theme()
        
        if USE_FLUENT:
            # Fluent 风格
            self.setStyleSheet(f"""
                ItemWidget {{
                    background-color: {theme['surface']};
                    border: 1px solid {theme['border_light']};
                    border-radius: 8px;
                }}
                ItemWidget:hover {{
                    background-color: {theme['surface_hover']};
                    border: 1px solid {theme['border_focus']};
                }}
                QLabel {{
                    color: {theme['text']};
                    background: transparent;
                }}
                #content_label {{
                    color: {theme['text']};
                    font-size: 13px;
                }}
                #meta_label {{
                    color: {theme['text_secondary']};
                    font-size: 11px;
                }}
                #favorite_btn {{
                    color: {theme['warning']};
                    font-size: 20px;
                    padding: 4px;
                    border-radius: 4px;
                }}
                #favorite_btn:hover {{
                    background-color: {theme['surface_hover']};
                }}
                #thumbnail {{
                    background-color: {theme['surface_active']};
                    border-radius: 8px;
                    font-size: 32px;
                }}
            """)
        else:
            # 标准 Qt 风格
            self.setStyleSheet(f"""
                ItemWidget {{
                    background-color: {theme['surface']};
                    border-radius: 10px;
                    border: 1px solid {theme['border_light']};
                    padding: 4px;
                }}
                ItemWidget:hover {{
                    background-color: {theme['surface_hover']};
                    border: 1px solid {theme['border']};
                }}
                ItemWidget[selected="true"] {{
                    background-color: {theme['accent_subtle']};
                    border: 2px solid {theme['accent']};
                }}
                QLabel {{
                    color: {theme['text']};
                    background: transparent;
                }}
                #content_label {{
                    color: {theme['text']};
                }}
                #meta_label {{
                    color: {theme['text_secondary']};
                }}
                #favorite_btn {{
                    color: {theme['warning']};
                }}
                #thumbnail {{
                    background-color: {theme['surface_active']};
                    border-radius: 8px;
                    font-size: 32px;
                }}
            """)
        
        self.setProperty("selected", "false")

    def _update_content(self) -> None:
        """更新显示内容"""
        # 更新缩略图/图标
        if self.item.content_type.value == "image":
            self._set_image_thumbnail()
        elif self.item.content_type.value == "file":
            self._set_placeholder_thumbnail(get_icon(FluentIcons.FOLDER))
        else:
            self._set_placeholder_thumbnail(get_icon(FluentIcons.DOCUMENT))

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
        """设置图片缩略图"""
        image_path = Path(self.item.content)
        if not image_path.exists():
            self._set_placeholder_thumbnail(get_icon(FluentIcons.IMAGE))
            return

        thumbnail_path = self._get_thumbnail_path(image_path)
        if thumbnail_path.exists():
            pixmap = QPixmap(str(thumbnail_path))
            if not pixmap.isNull():
                self.thumbnail_label.setPixmap(pixmap)
                return

        self._create_and_cache_thumbnail(image_path)

    def _get_thumbnail_path(self, image_path: Path) -> Path:
        """获取缩略图缓存路径"""
        from config import settings
        import hashlib
        hash_value = hashlib.md5(str(image_path).encode()).hexdigest()
        return settings.image_cache_dir / f"thumb_{hash_value}.png"

    def _create_and_cache_thumbnail(self, image_path: Path) -> None:
        """创建并缓存缩略图"""
        pixmap = QPixmap(str(image_path))
        if pixmap.isNull():
            self._set_placeholder_thumbnail(get_icon(FluentIcons.IMAGE))
            return

        scaled = pixmap.scaled(
            60, 60,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        thumbnail_path = self._get_thumbnail_path(image_path)
        scaled.save(str(thumbnail_path))
        self.thumbnail_label.setPixmap(scaled)

    def _set_placeholder_thumbnail(self, emoji: str) -> None:
        """设置占位缩略图（使用当前主题 placeholder 色）"""
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
                    padding: 4px;
                    border-radius: 4px;
                }}
                QLabel:hover {{
                    background-color: {theme['surface_hover']};
                }}
            """)
        else:
            self.favorite_btn.setText("☆")
            self.favorite_btn.setStyleSheet(f"""
                QLabel {{
                    color: {theme['text_muted']};
                    font-size: 20px;
                    padding: 4px;
                    border-radius: 4px;
                }}
                QLabel:hover {{
                    color: {theme['warning']};
                    background-color: {theme['surface_hover']};
                }}
            """)

    def _on_favorite_clicked(self, event) -> None:
        """收藏按钮点击处理"""
        self.item.is_favorite = not self.item.is_favorite
        self._update_favorite_icon()
        self.favorite_toggled.emit()

    def set_selected(self, selected: bool) -> None:
        """设置选中状态"""
        self.is_selected = selected
        self.setProperty("selected", "true" if selected else "false")
        if USE_FLUENT:
            theme = get_current_theme()
            if selected:
                self.setStyleSheet(self.styleSheet() + f"""
                    ItemWidget {{
                        border: 2px solid {theme['accent']};
                    }}
                """)
        else:
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

        if (event.pos() - self.drag_start_pos).manhattanLength() < 10:
            super().mouseMoveEvent(event)
            return

        # 开始拖拽
        drag = QDrag(self)
        mime_data = QMimeData()

        if self.item.content_type.value == "image":
            pixmap = QPixmap(str(self.item.content))
            if not pixmap.isNull():
                mime_data.setImageData(pixmap)
                drag.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
        elif self.item.content_type.value == "file" and self.item.file_list:
            from PyQt6.QtCore import QUrl
            urls = [QUrl.fromLocalFile(f) for f in self.item.file_list]
            mime_data.setUrls(urls)
        else:
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
        from utils.theme import _hex_to_rgb
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
