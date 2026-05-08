"""
过滤面板模块 - Fluent 设计风格
使用 ToggleButton 组件
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QButtonGroup
)

try:
    from PyQtFluentWidgets import ToggleButton
    USE_FLUENT = True
except ImportError:
    USE_FLUENT = False
    from PyQt6.QtWidgets import QPushButton
    ToggleButton = QPushButton

from models.enums import FilterType
from utils.theme import get_current_theme
from utils.fluent_icons import FluentIcons, get_icon, get_icon_font


class FilterPanel(QWidget):
    """过滤面板 - Fluent ToggleButton 样式"""

    filter_changed = pyqtSignal(FilterType)
    app_filter_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self.current_filter = FilterType.ALL
        self.app_list = []
        self.current_app_filter = None

    def _init_ui(self) -> None:
        """初始化 UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(8)

        # 过滤按钮组
        self.button_group = QButtonGroup(self)

        # 全部按钮
        self.btn_all = ToggleButton()
        self.btn_all.setText(f"{get_icon(FluentIcons.MENU)} 全部")
        self.btn_all.setCheckable(True)
        self.btn_all.setChecked(True)
        self.btn_all.clicked.connect(lambda: self._on_filter_changed(FilterType.ALL))
        self.button_group.addButton(self.btn_all)

        # 文本按钮
        self.btn_text = ToggleButton()
        self.btn_text.setText(f"{get_icon(FluentIcons.DOCUMENT)} 文本")
        self.btn_text.setCheckable(True)
        self.btn_text.clicked.connect(lambda: self._on_filter_changed(FilterType.TEXT))
        self.button_group.addButton(self.btn_text)

        # 图片按钮
        self.btn_image = ToggleButton()
        self.btn_image.setText(f"{get_icon(FluentIcons.IMAGE)} 图片")
        self.btn_image.setCheckable(True)
        self.btn_image.clicked.connect(lambda: self._on_filter_changed(FilterType.IMAGE))
        self.button_group.addButton(self.btn_image)

        # 文件按钮
        self.btn_file = ToggleButton()
        self.btn_file.setText(f"{get_icon(FluentIcons.FOLDER)} 文件")
        self.btn_file.setCheckable(True)
        self.btn_file.clicked.connect(lambda: self._on_filter_changed(FilterType.FILE))
        self.button_group.addButton(self.btn_file)

        # 收藏按钮
        self.btn_favorite = ToggleButton()
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
        
        if USE_FLUENT:
            # Fluent ToggleButton 样式
            self.setStyleSheet(f"""
                FilterPanel {{
                    background-color: {theme['surface']};
                    border-bottom: 1px solid {theme['border_light']};
                }}
            """)
        else:
            # 标准 Qt 样式
            self.setStyleSheet(f"""
                FilterPanel {{
                    background-color: {theme['surface']};
                    padding: 6px 10px;
                    border-bottom: 1px solid {theme['border_light']};
                }}

                QPushButton {{
                    background-color: {theme['surface_hover']};
                    color: {theme['text']};
                    border: 1px solid {theme['border']};
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-size: 13px;
                    font-weight: 500;
                    margin: 0 2px;
                    font-family: "Microsoft YaHei", sans-serif;
                }}

                QPushButton:hover {{
                    background-color: {theme['surface_active']};
                    color: {theme['text']};
                    border: 1px solid {theme['border_focus']};
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
        self.btn_favorite.setChecked(filter_type == FilterType.FAVORITE)
