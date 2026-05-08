"""
搜索栏模块
提供实时搜索功能
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton, QLabel
)

from utils.theme import get_current_theme
from utils.fluent_icons import FluentIcons, get_icon, get_icon_font


class SearchBar(QWidget):
    """搜索栏控件"""

    # 信号：搜索文本改变
    search_changed = pyqtSignal(str)

    # 信号：清除搜索
    clear_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        """初始化 UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 搜索图标/标签
        self.icon_label = QLabel()
        self.icon_label.setText(get_icon(FluentIcons.SEARCH))
        self.icon_label.setFixedWidth(30)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setFont(get_icon_font(18))

        # 搜索输入框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索剪贴板历史...")
        self.search_input.setMinimumHeight(40)
        self.search_input.textChanged.connect(self._on_text_changed)

        # 清除按钮
        self.clear_btn = QPushButton()
        self.clear_btn.setText(get_icon(FluentIcons.CLOSE))
        self.clear_btn.setFixedWidth(40)
        self.clear_btn.setMinimumHeight(40)
        self.clear_btn.setFlat(True)
        self.clear_btn.setVisible(False)
        self.clear_btn.clicked.connect(self._on_clear_clicked)
        self.clear_btn.setFont(get_icon_font(18))

        layout.addWidget(self.icon_label)
        layout.addWidget(self.search_input)
        layout.addWidget(self.clear_btn)

        self.setLayout(layout)
        self._apply_style()

    def _apply_style(self) -> None:
        """应用样式"""
        theme = get_current_theme()
        self.setStyleSheet(f"""
            SearchBar {{
                background: transparent;
            }}

            QLineEdit {{
                background-color: {theme['surface']};
                border: 2px solid {theme['border_light']};
                border-radius: 10px;
                padding: 10px 16px;
                color: {theme['text']};
                font-size: 14px;
                selection-background-color: {theme['selection']};
            }}

            QLineEdit:focus {{
                border: 2px solid {theme['accent']};
                background-color: {theme['surface_hover']};
            }}

            QLineEdit::placeholder {{
                color: {theme['text_muted']};
            }}

            QPushButton {{
                background-color: transparent;
                color: {theme['text_muted']};
                border: none;
                border-radius: 6px;
                padding: 4px;
            }}

            QPushButton:hover {{
                background-color: {theme['surface_hover']};
                color: {theme['text']};
            }}

            QLabel {{
                color: {theme['text_secondary']};
                background: transparent;
            }}
        """)
        
        # 更新图标颜色
        self.icon_label.setStyleSheet(f"color: {theme['text']};")

    def _on_text_changed(self, text: str) -> None:
        """文本改变处理"""
        self.clear_btn.setVisible(len(text) > 0)
        self.search_changed.emit(text)

    def _on_clear_clicked(self) -> None:
        """清除按钮点击"""
        self.search_input.clear()
        self.clear_requested.emit()

    def clear(self) -> None:
        """清除搜索内容"""
        self.search_input.clear()
