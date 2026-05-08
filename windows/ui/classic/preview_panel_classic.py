"""
预览面板模块
显示选中内容的详细预览
"""

from pathlib import Path
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage, QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame
)

from models.clipboard_item import ClipboardItem
from utils.theme import get_current_theme
from utils.fluent_icons import FluentIcons, get_icon, get_icon_font


class PreviewPanel(QFrame):
    """预览面板控件"""

    # 信号：复制按钮点击
    copy_clicked = pyqtSignal()
    # 信号：删除按钮点击
    delete_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_item: ClipboardItem = None
        self._init_ui()

    def _init_ui(self) -> None:
        """初始化 UI"""
        self.setFixedWidth(350)
        self.setFrameShape(QFrame.Shape.NoFrame)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 头部
        header = self._create_header()
        layout.addWidget(header)

        # 内容区域（滚动）
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        # 内容容器
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(16, 16, 16, 16)
        self.content_layout.setSpacing(16)

        # 预览内容标签
        self.preview_label = QLabel()
        self.preview_label.setWordWrap(True)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.preview_label.setFont(QFont("Microsoft YaHei", 10))
        self.preview_label.setObjectName("preview_content")

        self.content_layout.addWidget(self.preview_label)
        self.content_layout.addStretch()

        self.content_widget.setLayout(self.content_layout)
        self.scroll_area.setWidget(self.content_widget)

        layout.addWidget(self.scroll_area, 1)

        # 底部按钮
        footer = self._create_footer()
        layout.addWidget(footer)

        self.setLayout(layout)

        self._setup_style()

    def _create_header(self) -> QWidget:
        """创建头部"""
        header = QWidget()
        header.setFixedHeight(50)

        layout = QHBoxLayout()
        layout.setContentsMargins(16, 0, 16, 0)

        self.title_label = QLabel()
        self.title_label.setText("内容预览")
        title_font = QFont("Microsoft YaHei", 11)
        title_font.setWeight(QFont.Weight.Bold)
        self.title_label.setFont(title_font)

        layout.addWidget(self.title_label)
        layout.addStretch()

        header.setLayout(layout)
        return header

    def _create_footer(self) -> QWidget:
        """创建底部按钮区域"""
        footer = QWidget()
        footer.setFixedHeight(60)

        layout = QHBoxLayout()
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        # 复制按钮
        self.copy_btn = QPushButton()
        self.copy_btn.setText(f"{get_icon(FluentIcons.COPY)}  复制")
        self.copy_btn.setFixedHeight(40)
        self.copy_btn.clicked.connect(self._on_copy_clicked)
        self.copy_btn.setFont(get_icon_font(16))

        # 删除按钮
        self.delete_btn = QPushButton()
        self.delete_btn.setText(f"{get_icon(FluentIcons.DELETE)}  删除")
        self.delete_btn.setFixedHeight(40)
        self.delete_btn.clicked.connect(self._on_delete_clicked)
        self.delete_btn.setFont(get_icon_font(16))

        layout.addWidget(self.copy_btn)
        layout.addWidget(self.delete_btn)

        footer.setLayout(layout)
        return footer

    def _setup_style(self) -> None:
        """设置样式"""
        theme = get_current_theme()
        self.setStyleSheet(f"""
            PreviewPanel {{
                background-color: {theme['background']};
                border-left: 1px solid {theme['border']};
            }}

            QLabel {{
                color: {theme['text']};
                background: transparent;
            }}

            QScrollArea {{
                border: none;
                background: transparent;
            }}

            QPushButton {{
                background-color: {theme['accent']};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
                font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
            }}

            QPushButton:hover {{
                background-color: {theme['accent_hover']};
            }}

            QPushButton:pressed {{
                background-color: {theme['accent']};
            }}

            #delete_btn {{
                background-color: {theme['danger']};
            }}

            #delete_btn:hover {{
                background-color: {theme['danger_hover']};
            }}
            
            #preview_content {{
                color: {theme['text']};
                background-color: {theme['surface']};
                border-radius: 8px;
                padding: 12px;
            }}
        """)

        self.delete_btn.setObjectName("delete_btn")

    def set_item(self, item: ClipboardItem) -> None:
        """设置要预览的项"""
        self.current_item = item

        if item is None:
            self._show_empty()
            return

        # 更新标题
        if item.content_type.value == "image":
            self.title_label.setText("🖼️ 图片预览")
        elif item.content_type.value == "file":
            count = len(item.file_list) if item.file_list else 0
            self.title_label.setText(f"📁 {count} 个文件")
        elif item.content_type.value == "html":
            self.title_label.setText("🌐 HTML 内容")
        else:
            self.title_label.setText("📝 文本内容")

        # 更新预览内容
        self._update_preview_content(item)

    def _update_preview_content(self, item: ClipboardItem) -> None:
        """更新预览内容"""
        if item.content_type.value == "image":
            self._show_image_preview(item)
        elif item.content_type.value == "file":
            self._show_file_preview(item)
        elif item.content_type.value == "html":
            self._show_html_preview(item)
        else:
            self._show_text_preview(item)

    def _show_text_preview(self, item: ClipboardItem) -> None:
        """显示文本预览"""
        text = item.content
        # 限制显示长度
        if len(text) > 2000:
            text = text[:2000] + "\n\n...（内容过长，已截断）"
        self.preview_label.setText(text)
        self.preview_label.show()

    def _show_image_preview(self, item: ClipboardItem) -> None:
        """显示图片预览"""
        image_path = Path(item.content)
        if image_path.exists():
            pixmap = QPixmap(str(image_path))
            if not pixmap.isNull():
                # 缩放图片以适应预览区域
                scaled = pixmap.scaled(
                    self.scroll_area.viewport().width() - 50,
                    400,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.preview_label.setPixmap(scaled)
                self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.preview_label.show()
                return

        self.preview_label.setText("图片加载失败")
        self.preview_label.show()

    def _show_file_preview(self, item: ClipboardItem) -> None:
        """显示文件预览"""
        if item.file_list:
            file_text = "文件列表:\n\n" + "\n".join(item.file_list)
            self.preview_label.setText(file_text)
            self.preview_label.show()
        else:
            self.preview_label.setText("无文件内容")
            self.preview_label.show()

    def _show_html_preview(self, item: ClipboardItem) -> None:
        """显示 HTML 预览"""
        # 去除 HTML 标签显示纯文本
        import re
        text = re.sub(r'<[^>]+>', '', item.content)
        if len(text) > 2000:
            text = text[:2000] + "\n\n...（内容过长，已截断）"
        self.preview_label.setText(text)
        self.preview_label.show()

    def _show_empty(self) -> None:
        """显示空状态"""
        self.title_label.setText("内容预览")
        self.preview_label.setText("未选中任何内容")
        self.preview_label.show()

    def _on_copy_clicked(self) -> None:
        """复制按钮点击"""
        self.copy_clicked.emit()

    def _on_delete_clicked(self) -> None:
        """删除按钮点击"""
        self.delete_clicked.emit()
