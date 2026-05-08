"""
Fluent 设计主题模块
基于 PyQt-Fluent-Widgets 的主题系统
"""

from enum import Enum
from typing import Dict


class FluentTheme(Enum):
    """Fluent 主题枚举"""
    DARK = "dark"
    LIGHT = "light"
    HIGH_CONTRAST = "high_contrast"


# Fluent 颜色方案
FLUENT_COLORS: Dict[str, Dict[str, str]] = {
    'dark': {
        # 基础色
        'solid_background': '#202020',
        'card_background': '#2C2C2C',
        'card_border': '#383838',
        
        # 文字色
        'text_primary': '#FFFFFF',
        'text_secondary': '#9E9E9E',
        'text_tertiary': '#7A7A7A',
        'text_disabled': '#5D5D5D',
        
        # 强调色
        'accent_default': '#60CDFF',
        'accent_hover': '#79D2FF',
        'accent_pressed': '#4CC2FF',
        'accent_disabled': '#2D5B6F',
        
        # 语义色
        'success': '#6CCB5F',
        'warning': '#FFD580',
        'error': '#FF6B6B',
        'info': '#60CDFF',
        
        # 分割线
        'divider': '#383838',
        
        # 图层
        'layer': '#2C2C2C',
        'layer_on_card': '#383838',
    },
    'light': {
        # 基础色
        'solid_background': '#F3F3F3',
        'card_background': '#FFFFFF',
        'card_border': '#E5E5E5',
        
        # 文字色
        'text_primary': '#1A1A1A',
        'text_secondary': '#5D5D5D',
        'text_tertiary': '#8A8A8A',
        'text_disabled': '#BDBDBD',
        
        # 强调色
        'accent_default': '#0067C0',
        'accent_hover': '#1074C7',
        'accent_pressed': '#005A9E',
        'accent_disabled': '#B8D3E9',
        
        # 语义色
        'success': '#107C10',
        'warning': '#797775',
        'error': '#C42B1C',
        'info': '#0067C0',
        
        # 分割线
        'divider': '#E5E5E5',
        
        # 图层
        'layer': '#FFFFFF',
        'layer_on_card': '#F3F3F3',
    },
}


def get_fluent_stylesheet(theme: str = 'dark') -> str:
    """
    获取 Fluent 风格样式表
    
    Args:
        theme: 主题名称 ('dark' 或 'light')
        
    Returns:
        样式表字符串
    """
    colors = FLUENT_COLORS.get(theme, FLUENT_COLORS['dark'])
    
    return f"""
        /* Fluent Design Stylesheet */
        
        * {{
            font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
        }}
        
        /* 基础控件 */
        QWidget {{
            background-color: {colors['solid_background']};
            color: {colors['text_primary']};
        }}
        
        /* 卡片式容器 */
        QFrame#card, QFrame#surface {{
            background-color: {colors['card_background']};
            border: 1px solid {colors['card_border']};
            border-radius: 8px;
        }}
        
        /* 按钮 */
        QPushButton {{
            background-color: {colors['card_background']};
            border: 1px solid {colors['card_border']};
            border-radius: 6px;
            padding: 8px 16px;
            color: {colors['text_primary']};
            font-size: 13px;
            font-weight: 500;
        }}
        
        QPushButton:hover {{
            background-color: {colors['layer_on_card']};
            border: 1px solid {colors['text_tertiary']};
        }}
        
        QPushButton:pressed {{
            background-color: {colors['layer']};
        }}
        
        QPushButton:disabled {{
            color: {colors['text_disabled']};
            border: 1px solid {colors['card_border']};
        }}
        
        /* 强调按钮 */
        QPushButton#accent_btn {{
            background-color: {colors['accent_default']};
            border: 1px solid {colors['accent_default']};
            color: #FFFFFF;
        }}
        
        QPushButton#accent_btn:hover {{
            background-color: {colors['accent_hover']};
            border: 1px solid {colors['accent_hover']};
        }}
        
        QPushButton#accent_btn:pressed {{
            background-color: {colors['accent_pressed']};
            border: 1px solid {colors['accent_pressed']};
        }}
        
        /* 输入框 */
        QLineEdit, QSpinBox, QComboBox {{
            background-color: {colors['solid_background']};
            border: 1px solid {colors['card_border']};
            border-radius: 6px;
            padding: 8px 12px;
            color: {colors['text_primary']};
            font-size: 13px;
        }}
        
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
            border: 2px solid {colors['accent_default']};
            padding: 7px 11px;
        }}
        
        QLineEdit:disabled, QSpinBox:disabled, QComboBox:disabled {{
            background-color: {colors['layer']};
            color: {colors['text_disabled']};
        }}
        
        /* 复选框 */
        QCheckBox {{
            color: {colors['text_primary']};
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border: 2px solid {colors['text_secondary']};
            border-radius: 4px;
            background-color: transparent;
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {colors['accent_default']};
            border: 2px solid {colors['accent_default']};
        }}
        
        QCheckBox::indicator:hover {{
            border: 2px solid {colors['accent_default']};
        }}
        
        /* 分组框 */
        QGroupBox {{
            font-weight: 600;
            font-size: 13px;
            color: {colors['text_primary']};
            border: 1px solid {colors['card_border']};
            border-radius: 8px;
            margin-top: 16px;
            padding-top: 16px;
            background-color: {colors['card_background']};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 12px;
            padding: 0 8px;
        }}
        
        /* 滚动条 */
        QScrollBar:vertical {{
            background-color: transparent;
            width: 14px;
            margin: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {colors['text_tertiary']};
            border-radius: 7px;
            min-height: 30px;
            margin: 2px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {colors['text_secondary']};
        }}
        
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        /* 分割线 */
        QFrame#divider {{
            background-color: {colors['divider']};
            max-height: 1px;
        }}
        
        /* 标签 */
        QLabel {{
            color: {colors['text_primary']};
            background: transparent;
        }}
        
        QLabel#secondary {{
            color: {colors['text_secondary']};
        }}
        
        QLabel#tertiary {{
            color: {colors['text_tertiary']};
        }}
        
        /* 菜单 */
        QMenu {{
            background-color: {colors['card_background']};
            border: 1px solid {colors['card_border']};
            border-radius: 8px;
            padding: 8px;
        }}
        
        QMenu::item {{
            padding: 8px 16px;
            border-radius: 6px;
            color: {colors['text_primary']};
        }}
        
        QMenu::item:selected {{
            background-color: {colors['layer_on_card']};
        }}
        
        QMenu::separator {{
            height: 1px;
            background-color: {colors['divider']};
            margin: 4px 8px;
        }}
    """


def apply_fluent_theme(widget, theme: str = 'dark') -> None:
    """
    应用 Fluent 主题到控件
    
    Args:
        widget: Qt 控件对象
        theme: 主题名称
    """
    widget.setStyleSheet(get_fluent_stylesheet(theme))
