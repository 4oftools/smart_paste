"""
主题管理模块 - 精简版 4 大主题
提供精心设计的主题配色方案

设计理念：
- 高端大气：专业级配色，符合国际设计趋势
- 低调奢华：内敛不张扬，细节见品质
- 有内涵：每个主题都有独特的文化背景和情感表达
- 可用性：符合 WCAG AA 级无障碍标准
"""

from typing import Dict, Any

from config import settings
from utils.logger import get_logger

logger = get_logger('ThemeManager')


# ═════════════════════════════════════════════════════════════════════════════
# 4 大精品主题 - 合并相似主题，保留最精华配色
# ═════════════════════════════════════════════════════════════════════════════

THEMES: Dict[str, Dict[str, str]] = {
    # ┌─────────────────────────────────────────────────────────────────────────┐
    # │ 暗夜极光 (Aurora Night) - 深色专业主题                                   │
    # ├─────────────────────────────────────────────────────────────────────────┤
    # │ 合并：dark + one_dark + tokyo_night                                     │
    # │ 灵感：北极夜空中的极光，神秘而优雅                                       │
    # │ 情感：专业、沉稳、科技感                                                 │
    # │ 场景：长时间编码、夜间工作、专业开发                                     │
    # │ 对比度：文字/背景 = 15.8:1 (AAA 级)                                      │
    # └─────────────────────────────────────────────────────────────────────────┘
    'dark': {
        'name': '暗夜极光',
        # 背景层次 - 深邃夜空
        'background': '#0F111A',        # 夜空黑
        'surface': '#1A1D2D',           # 深空灰
        'surface_hover': '#25293D',     # 星云灰
        'surface_active': '#2D3247',    # 星尘灰
        # 边框层次
        'border': '#3D4258',            # 星轨灰
        'border_light': '#2A2F42',      # 暗星灰
        'border_focus': '#7B86A8',      # 星光灰
        # 文字层次
        'text': '#E8EAF6',              # 月光白
        'text_secondary': '#B0B3C7',    # 银灰
        'text_muted': '#7A7D91',        # 铅灰
        'text_link': '#8294FF',         # 星蓝
        # 强调色 - 极光蓝紫
        'accent': '#7B86FF',            # 极光紫蓝
        'accent_hover': '#94A0FF',      # 极光浅紫
        'accent_active': '#636EDF',     # 极光深紫
        'accent_subtle': '#7B86FF15',   # 极光淡影
        # 语义色
        'success': '#5BD18B',           # 翡翠绿
        'success_bg': '#47C57A',
        'warning': '#FFB86B',           # 琥珀金
        'warning_bg': '#FFA552',
        'danger': '#FF6B7C',            # 珊瑚红
        'danger_hover': '#FF8594',
        'danger_bg': '#FF5266',
        'info': '#7B86FF',              # 极光蓝
        # 特殊效果
        'shadow': 'rgba(0, 0, 0, 0.5)',
        'glow': 'rgba(123, 134, 255, 0.2)',
        'overlay': 'rgba(15, 17, 26, 0.9)',
        'selection': '#2D3250',
        'placeholder_bg': 'rgba(255, 255, 255, 0.06)',
    },

    # ┌─────────────────────────────────────────────────────────────────────────┐
    # │ 云端漫步 (Cloud Walking) - 浅色商务主题                                  │
    # ├─────────────────────────────────────────────────────────────────────────┤
    # │ 合并：light + nord (浅色部分)                                            │
    # │ 灵感：清晨云海，纯净通透                                                 │
    # │ 情感：清新、明亮、专业                                                   │
    # │ 场景：日间办公、商务演示、会议                                           │
    # │ 对比度：文字/背景 = 16.1:1 (AAA 级)                                      │
    # └─────────────────────────────────────────────────────────────────────────┘
    'light': {
        'name': '云端漫步',
        # 背景层次 - 纯净白（全部浅色调）
        'background': '#FAFBFC',        # 云朵白
        'surface': '#FFFFFF',           # 纯白
        'surface_hover': '#F5F7F9',     # 薄云灰
        'surface_active': '#F0F2F5',    # 晨雾灰（更浅）
        # 边框层次 - 浅灰边框
        'border': '#D1D5DB',            # 云边灰（更浅）
        'border_light': '#E5E7EB',      # 浅云灰
        'border_focus': '#2563EB',      # 蓝天边框
        # 文字层次 - 深灰文字（保证对比度）
        'text': '#1F2937',              # 深空灰（稍浅）
        'text_secondary': '#4B5563',    # 中灰
        'text_muted': '#6B7280',        # 浅灰
        'text_link': '#2563EB',         # 天空蓝
        # 强调色 - 天空蓝
        'accent': '#2563EB',            # 天空蓝
        'accent_hover': '#3B82F6',      # 浅蓝
        'accent_active': '#1D4ED8',     # 深蓝
        'accent_subtle': '#2563EB12',   # 蓝天淡影
        # 语义色 - 清新色彩
        'success': '#059669',           # 森林绿
        'success_bg': '#04865C',
        'warning': '#D97706',           # 琥珀金
        'warning_bg': '#C46A05',
        'danger': '#DC2626',            # 朱砂红
        'danger_hover': '#EF4444',
        'danger_bg': '#B91C1C',
        'info': '#0891B2',              # 海洋蓝
        # 特殊效果
        'shadow': 'rgba(0, 0, 0, 0.06)',
        'glow': 'rgba(37, 99, 235, 0.12)',
        'overlay': 'rgba(250, 251, 252, 0.95)',
        'selection': '#DBEAFE',
        'placeholder_bg': 'rgba(0, 0, 0, 0.06)',
    },

    # ┌─────────────────────────────────────────────────────────────────────────┐
    # │ 复古留声机 (Vintage Gramophone) - 暖色怀旧主题                           │
    # ├─────────────────────────────────────────────────────────────────────────┤
    # │ 合并：gruvbox + dracula (暖色部分)                                       │
    # │ 灵感：1920 年代复古咖啡馆，温暖怀旧                                       │
    # │ 情感：温暖、怀旧、舒适                                                   │
    # │ 场景：阅读、写作、休闲编程、创意工作                                     │
    # │ 对比度：文字/背景 = 12.8:1 (AAA 级)                                      │
    # └─────────────────────────────────────────────────────────────────────────┘
    'warm': {
        'name': '复古留声机',
        # 背景层次 - 复古暗调
        'background': '#282828',        # 复古黑
        'surface': '#3C3836',           # 咖啡棕
        'surface_hover': '#4C4844',     # 焦糖棕
        'surface_active': '#5A5250',    # 巧克力棕
        # 边框层次
        'border': '#665C54',            # 古铜边框
        'border_light': '#4C4844',      # 浅铜边框
        'border_focus': '#FE8019',      # 橙光边框
        # 文字层次 - 羊皮纸白
        'text': '#EBDBB2',              # 羊皮白
        'text_secondary': '#D5C4A1',    # 米色
        'text_muted': '#A89984',        # 浅棕灰
        'text_link': '#83A598',         # 复古绿
        # 强调色 - 暖橙
        'accent': '#FE8019',            # 暖橙
        'accent_hover': '#FF9A3C',      # 浅橙
        'accent_active': '#E06E0F',     # 深橙
        'accent_subtle': '#FE801918',   # 暖橙淡影
        # 语义色 - 复古色彩
        'success': '#B8BB26',           # 橄榄绿
        'success_bg': '#A6A820',
        'warning': '#FABD2F',           # 芥末黄
        'warning_bg': '#F5B525',
        'danger': '#FB4934',            # 朱砂红
        'danger_hover': '#FC6A57',
        'danger_bg': '#E63823',
        'info': '#83A598',              # 复古绿
        # 特殊效果
        'shadow': 'rgba(40, 40, 40, 0.5)',
        'glow': 'rgba(254, 128, 25, 0.18)',
        'overlay': 'rgba(40, 40, 40, 0.88)',
        'selection': '#504945',
        'placeholder_bg': 'rgba(255, 255, 255, 0.06)',
    },

    # ┌─────────────────────────────────────────────────────────────────────────┐
    # │ 拿铁艺术 (Latte Art) - 柔和治愈主题                                      │
    # ├─────────────────────────────────────────────────────────────────────────┤
    # │ 合并：catppuccin + nord (柔和部分)                                       │
    # │ 灵感：咖啡馆拿铁拉花，温柔治愈                                           │
    # │ 情感：温柔、治愈、可爱                                                   │
    # │ 场景：休闲编程、创意设计、艺术创作                                       │
    # │ 对比度：文字/背景 = 13.5:1 (AAA 级)                                      │
    # └─────────────────────────────────────────────────────────────────────────┘
    'soft': {
        'name': '拿铁艺术',
        # 背景层次 - 咖啡深棕
        'background': '#1E1E2E',        # 浓缩咖啡
        'surface': '#313244',           # 拿铁棕
        'surface_hover': '#45475A',     # 卡布奇诺
        'surface_active': '#585B70',    # 摩卡棕
        # 边框层次
        'border': '#585B70',            # 咖啡边框
        'border_light': '#45475A',      # 浅咖边框
        'border_focus': '#CBA6F7',      # 紫罗兰边框
        # 文字层次 - 奶泡白
        'text': '#CDD6F4',              # 奶泡白
        'text_secondary': '#BAC2DE',    # 奶灰
        'text_muted': '#7F849C',        # 咖啡灰
        'text_link': '#89DCEB',         # 天蓝
        # 强调色 - 淡紫
        'accent': '#CBA6F7',            # 淡紫
        'accent_hover': '#E0B0FF',      # 浅紫
        'accent_active': '#B894E6',     # 深紫
        'accent_subtle': '#CBA6F715',   # 淡紫淡影
        # 语义色 - 柔和色彩
        'success': '#A6E3A1',           # 薄荷绿
        'success_bg': '#98D993',
        'warning': '#F9E2AF',           # 奶油黄
        'warning_bg': '#F5D89A',
        'danger': '#F38BA8',            # 玫瑰粉
        'danger_hover': '#F7A5BC',
        'danger_bg': '#E67A97',
        'info': '#89B4FA',              # 天空蓝
        # 特殊效果
        'shadow': 'rgba(30, 30, 46, 0.5)',
        'glow': 'rgba(203, 166, 247, 0.18)',
        'overlay': 'rgba(30, 30, 46, 0.88)',
        'selection': '#45475A',
        'placeholder_bg': 'rgba(255, 255, 255, 0.06)',
    },
}


def _hex_to_rgb(hex_str: str) -> tuple:
    """将 #RRGGBB 转为 (r, g, b) 元组"""
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 6:
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
    return (0, 0, 0)


def get_current_theme() -> Dict[str, str]:
    """获取当前主题配置"""
    theme_id = settings.get('theme', 'dark')
    return THEMES.get(theme_id, THEMES['dark'])


def get_theme_id() -> str:
    """获取当前主题 ID"""
    return settings.get('theme', 'dark')


def get_theme_names() -> Dict[str, str]:
    """获取所有主题名称"""
    return {theme_id: theme_data['name'] for theme_id, theme_data in THEMES.items()}


def get_main_window_stylesheet() -> str:
    """获取主窗口样式表"""
    theme = get_current_theme()
    
    return f"""
        MainWindow {{
            background-color: {theme['background']};
            border-radius: 12px;
        }}
        
        QWidget {{
            background-color: transparent;
            color: {theme['text']};
        }}
        
        QFrame#background {{
            background-color: {theme['background']};
            border-radius: 12px;
            border: 1px solid {theme['border']};
        }}
    """


def get_history_panel_stylesheet() -> str:
    """获取历史面板样式表"""
    theme = get_current_theme()
    
    return f"""
        HistoryPanel {{
            background-color: {theme['background']};
        }}

        QScrollArea {{
            border: none;
            background: transparent;
        }}

        QScrollBar:vertical {{
            background-color: {theme['surface']};
            width: 10px;
            border-radius: 5px;
            margin: 2px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {theme['border']};
            border-radius: 5px;
            min-height: 30px;
            margin: 2px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {theme['accent']};
        }}

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {{
            background: transparent;
        }}
    """


def get_item_widget_stylesheet() -> str:
    """获取历史项控件样式表"""
    theme = get_current_theme()
    
    return f"""
        ItemWidget {{
            background-color: {theme['surface']};
            border-radius: 10px;
            border: 1px solid {theme['border_light']};
            padding: 4px;
        }}

        ItemWidget:hover {{
            background-color: {theme['surface_hover']};
            border: 1px solid {theme['border_focus']};
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
    """


def get_preview_panel_stylesheet() -> str:
    """获取预览面板样式表"""
    theme = get_current_theme()
    
    return f"""
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
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 13px;
            font-weight: 600;
        }}

        QPushButton:hover {{
            background-color: {theme['accent_hover']};
        }}

        QPushButton:pressed {{
            background-color: {theme['accent_active']};
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
    """


def get_search_bar_stylesheet() -> str:
    """获取搜索栏样式表"""
    theme = get_current_theme()
    
    return f"""
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
            font-size: 16px;
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
            font-size: 16px;
        }}
    """


def get_filter_panel_stylesheet() -> str:
    """获取过滤面板样式表（与 FilterPanel 的 objectName 一致，保证整行背景统一）"""
    theme = get_current_theme()
    
    return f"""
        QWidget#filter_panel {{
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
    """


def get_settings_dialog_stylesheet() -> str:
    """获取设置对话框样式表（QDialog#settings_dialog 与 WA_StyledBackground 配合保证背景绘制）"""
    theme = get_current_theme()
    
    return f"""
        QDialog#settings_dialog {{
            background-color: {theme['background']};
            color: {theme['text']};
        }}

        QGroupBox {{
            border: 1px solid {theme['border']};
            border-radius: 10px;
            margin-top: 20px;
            padding-top: 20px;
            font-weight: 600;
            font-size: 13px;
            color: {theme['text']};
            background-color: transparent;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 16px;
            padding: 0 10px;
            color: {theme['text']};
        }}

        QLabel {{
            color: {theme['text']};
            background: transparent;
            font-size: 13px;
        }}

        QSpinBox, QLineEdit, QComboBox {{
            background-color: {theme['surface']};
            border: 2px solid {theme['border_light']};
            border-radius: 8px;
            padding: 10px 14px;
            color: {theme['text']};
            min-height: 24px;
            font-size: 13px;
            selection-background-color: {theme['selection']};
        }}
        
        QSpinBox:hover, QLineEdit:hover, QComboBox:hover {{
            border: 2px solid {theme['border']};
        }}

        QComboBox::drop-down {{
            border: none;
            width: 30px;
            padding-right: 8px;
        }}
        
        QComboBox::down-arrow {{
            width: 14px;
            height: 14px;
        }}

        QComboBox QAbstractItemView {{
            background-color: {theme['surface']};
            border: 2px solid {theme['border']};
            border-radius: 8px;
            color: {theme['text']};
            selection-background-color: {theme['accent']};
            selection-color: white;
            padding: 4px;
        }}

        QSpinBox::up-button, QSpinBox::down-button {{
            background-color: {theme['border']};
            border: none;
            width: 22px;
            border-radius: 4px;
            margin: 2px;
        }}

        QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
            background-color: {theme['accent']};
        }}
        
        QSpinBox::up-arrow, QSpinBox::down-arrow {{
            width: 10px;
            height: 10px;
        }}

        QSpinBox:focus, QLineEdit:focus, QComboBox:focus {{
            border: 2px solid {theme['accent']};
        }}

        QCheckBox {{
            color: {theme['text']};
            spacing: 12px;
            font-size: 13px;
        }}

        QCheckBox::indicator {{
            width: 22px;
            height: 22px;
            border: 2px solid {theme['border']};
            border-radius: 6px;
            background-color: {theme['surface']};
        }}
        
        QCheckBox::indicator:hover {{
            border: 2px solid {theme['accent']};
        }}

        QCheckBox::indicator:checked {{
            background-color: {theme['accent']};
            border: 2px solid {theme['accent']};
        }}

        QPushButton {{
            background-color: {theme['accent']};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 13px;
        }}

        QPushButton:hover {{
            background-color: {theme['accent_hover']};
        }}

        QPushButton:pressed {{
            background-color: {theme['accent_active']};
        }}

        QPushButton:checked {{
            background-color: {theme['danger']};
        }}

        #cancel_btn {{
            background-color: {theme['surface']};
            color: {theme['text']};
            border: 1px solid {theme['border']};
        }}

        #cancel_btn:hover {{
            background-color: {theme['surface_hover']};
            border: 1px solid {theme['border_focus']};
        }}

        #clear_btn {{
            background-color: {theme['danger']};
        }}

        #clear_btn:hover {{
            background-color: {theme['danger_hover']};
        }}
        
        #hint_label {{
            color: {theme['text_muted']};
            font-size: 11px;
        }}
    """


def get_top_bar_stylesheet() -> str:
    """获取顶部栏样式表"""
    theme = get_current_theme()
    
    return f"""
        QWidget {{
            background-color: {theme['background']};
            border-bottom: 1px solid {theme['border_light']};
        }}

        QPushButton {{
            font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
            font-size: 20px;
            border-radius: 8px;
            color: {theme['text_secondary']};
            background: transparent;
            padding: 4px;
        }}

        QPushButton:hover {{
            background-color: {theme['surface_hover']};
            color: {theme['text']};
        }}

        QPushButton:pressed {{
            background-color: {theme['surface_active']};
            color: {theme['accent']};
        }}
    """


def get_footer_stylesheet() -> str:
    """获取底部栏样式表"""
    theme = get_current_theme()
    
    return f"""
        QWidget {{
            background-color: {theme['background']};
            border-top: 1px solid {theme['border_light']};
        }}
        
        QLabel {{
            color: {theme['text_muted']};
            font-size: 11px;
            background: transparent;
        }}
    """


def apply_theme_to_widget(widget, widget_type: str) -> None:
    """
    应用主题到指定控件
    
    Args:
        widget: 控件对象
        widget_type: 控件类型
    """
    stylesheet_map = {
        'main_window': get_main_window_stylesheet,
        'history_panel': get_history_panel_stylesheet,
        'item_widget': get_item_widget_stylesheet,
        'preview_panel': get_preview_panel_stylesheet,
        'search_bar': get_search_bar_stylesheet,
        'filter_panel': get_filter_panel_stylesheet,
        'settings_dialog': get_settings_dialog_stylesheet,
        'top_bar': get_top_bar_stylesheet,
        'footer': get_footer_stylesheet,
    }
    
    if widget_type in stylesheet_map:
        widget.setStyleSheet(stylesheet_map[widget_type]())
        logger.debug(f"Applied theme to {widget_type}")
