"""
过滤面板模块
提供按条件过滤剪贴板记录的功能
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QButtonGroup
)
from PyQt6.QtGui import QFont

from models.enums import FilterType
from utils.theme import get_current_theme
from utils.fluent_icons import FluentIcons, get_icon, get_icon_font


class FilterPanel(QWidget):
    """过滤面板控件"""

    # 信号：过滤类型改变
    filter_changed = pyqtSignal(FilterType)

    # 信号：应用过滤器改变
    app_filter_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("filter_panel")
        # 确保整行（含右侧空白）都使用同一背景色绘制，避免右侧露出父级背景
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._init_ui()
        self.current_filter = FilterType.ALL
        self.app_list = []
        self.current_app_filter = None

    def _init_ui(self) -> None:
        """初始化 UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(8)

        # 过滤按钮组
        self.button_group = QButtonGroup(self)

        # 全部按钮
        self.btn_all = QPushButton()
        self.btn_all.setText(f"{get_icon(FluentIcons.MENU)} 全部")
        self.btn_all.setCheckable(True)
        self.btn_all.setChecked(True)
        self.btn_all.clicked.connect(lambda: self._on_filter_changed(FilterType.ALL))
        self.button_group.addButton(self.btn_all)

        # 文本按钮
        self.btn_text = QPushButton()
        self.btn_text.setText(f"{get_icon(FluentIcons.DOCUMENT)} 文本")
        self.btn_text.setCheckable(True)
        self.btn_text.clicked.connect(lambda: self._on_filter_changed(FilterType.TEXT))
        self.button_group.addButton(self.btn_text)

        # 图片按钮
        self.btn_image = QPushButton()
        self.btn_image.setText(f"{get_icon(FluentIcons.IMAGE)} 图片")
        self.btn_image.setCheckable(True)
        self.btn_image.clicked.connect(lambda: self._on_filter_changed(FilterType.IMAGE))
        self.button_group.addButton(self.btn_image)

        # 文件按钮
        self.btn_file = QPushButton()
        self.btn_file.setText(f"{get_icon(FluentIcons.FOLDER)} 文件")
        self.btn_file.setCheckable(True)
        self.btn_file.clicked.connect(lambda: self._on_filter_changed(FilterType.FILE))
        self.button_group.addButton(self.btn_file)

        # 收藏按钮
        self.btn_favorite = QPushButton()
        self.btn_favorite.setText(f"{get_icon(FluentIcons.STAR)} 收藏")
        self.btn_favorite.setCheckable(True)
        self.btn_favorite.clicked.connect(lambda: self._on_filter_changed(FilterType.FAVORITE))
        self.button_group.addButton(self.btn_favorite)

        # 添加按钮到布局
        layout.addWidget(self.btn_all)
        layout.addWidget(self.btn_text)
        layout.addWidget(self.btn_image)
        layout.addWidget(self.btn_file)
        layout.addWidget(self.btn_favorite)
        layout.addStretch()

        self.setLayout(layout)
        self._apply_style()

    def _apply_style(self) -> None:
        """应用样式"""
        theme = get_current_theme()
        
        # 设置图标字体
        icon_font = get_icon_font(16)
        self.btn_all.setFont(icon_font)
        self.btn_text.setFont(icon_font)
        self.btn_image.setFont(icon_font)
        self.btn_file.setFont(icon_font)
        self.btn_favorite.setFont(icon_font)
        
        self.setStyleSheet(f"""
            QWidget#filter_panel {{
                background-color: {theme['surface']};
                padding: 6px 10px;
                border-bottom: 1px solid {theme['border_light']};
            }}

            QPushButton {{
                background-color: {theme['surface_hover']};
                color: {theme['text_secondary']};
                border: 1px solid {theme['border_light']};
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 500;
                margin: 0 2px;
                font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
            }}

            QPushButton:hover {{
                background-color: {theme['surface_active']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
            }}

            QPushButton:checked {{
                background-color: {theme['accent']};
                color: white;
                border: 1px solid {theme['accent']};
                font-weight: 600;
            }}

            QPushButton:checked:hover {{
                background-color: {theme['accent_hover']};
                border: 1px solid {theme['accent_hover']};
            }}
        """)

    def _on_filter_changed(self, filter_type: FilterType) -> None:
        """过滤类型变化处理"""
        self.current_filter = filter_type
        self.filter_changed.emit(filter_type)

    def set_filter(self, filter_type: FilterType) -> None:
        """设置当前过滤类型"""
        self.current_filter = filter_type

        # 更新按钮状态
        self.btn_all.setChecked(filter_type == FilterType.ALL)
        self.btn_text.setChecked(filter_type == FilterType.TEXT)
        self.btn_image.setChecked(filter_type == FilterType.IMAGE)
        self.btn_file.setChecked(filter_type == FilterType.FILE)
