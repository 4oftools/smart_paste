"""
Fluent Icons 工具模块
提供 PyQt-Fluent-Widgets 图标支持
"""

from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

try:
    from PyQtFluentWidgets import FluentIcon
    USE_FLUENT_ICONS = True
    print(f"{USE_FLUENT_ICONS}aasawsas")
except ImportError:
    USE_FLUENT_ICONS = False


class FluentIcons:
    """Fluent Icons 图标映射类"""
    
    # 导航/操作
    MENU = ("Menu", "☰")
    SETTINGS = ("Setting", "⚙️")
    CLOSE = ("Close", "✕")
    SEARCH = ("Search", "🔍")
    MORE = ("More", "⋮")
    
    # 剪贴板相关
    COPY = ("Copy", "📋")
    PASTE = ("Paste", "📄")
    DELETE = ("Delete", "🗑️")
    CLEAR = ("Clear", "🧹")
    
    # 文件类型
    DOCUMENT = ("Document", "📝")
    IMAGE = ("Image", "🖼️")
    FOLDER = ("Folder", "📁")
    GLOBE = ("Globe", "🌐")
    
    # 收藏/星标
    STAR = ("Star", "⭐")
    STAR_OUTLINE = ("StarOff", "☆")
    
    # 可见性
    VIEW = ("View", "👁️")
    HIDE = ("Hide", "🙈")
    
    # 编辑
    EDIT = ("Edit", "✏️")
    SAVE = ("Save", "💾")
    
    # 播放/控制
    PLAY = ("Play", "▶️")
    PAUSE = ("Pause", "⏸️")
    
    # 颜色/主题
    PALETTE = ("Palette", "🎨")
    
    # 键盘/快捷键
    KEYBOARD = ("Keyboard", "⌨️")
    
    # 列表/菜单
    LIST = ("List", "📋")
    GRID = ("Grid", "⊞")
    
    # 信息
    INFO = ("Info", "ℹ️")
    WARNING = ("Warning", "⚠️")
    ERROR = ("Error", "❌")
    SUCCESS = ("Accept", "✅")
    
    # 箭头
    UP = ("Up", "↑")
    DOWN = ("Down", "↓")
    LEFT = ("Left", "←")
    RIGHT = ("Right", "→")
    
    # 其他
    PIN = ("Pin", "📌")
    UNPIN = ("Unpin", "📍")
    REFRESH = ("Refresh", "🔄")
    SEND = ("Send", "📤")
    DOWNLOAD = ("Download", "📥")
    UPLOAD = ("Upload", "📤")
    LINK = ("Link", "🔗")
    UNLINK = ("Unlink", "🔗")
    ATTACHMENT = ("Attachment", "📎")
    PRINT = ("Print", "🖨️")
    SHARE = ("Share", "📤")
    HOME = ("Home", "🏠")
    BACK = ("Back", "←")
    FORWARD = ("Forward", "→")
    REFRESH = ("Refresh", "🔄")
    SYNC = ("Sync", "🔄")
    ADD = ("Add", "+")
    REMOVE = ("Remove", "−")
    CHECKBOX = ("CheckBox", "☑️")
    CHECKBOX_OUTLINE = ("CheckBoxOff", "⬜")
    RADIO = ("Radio", "🔘")
    RADIO_OUTLINE = ("RadioOff", "⚪")
    TOGGLE = ("Toggle", "🔛")
    TOGGLE_OFF = ("ToggleOff", "⭕")
    SLIDER = ("Slider", "🎚️")
    SWITCH = ("Switch", "🔘")


def get_fluent_icon(icon_tuple) -> str:
    """
    获取 Fluent Icon
    
    Args:
        icon_tuple: 图标元组 (FluentIcon名称, emoji后备)
    
    Returns:
        图标字符串（如果可用则返回 FluentIcon，否则返回 emoji）
    """
    if USE_FLUENT_ICONS:
        # 返回 FluentIcon 名称，用于样式表
        return icon_tuple[0]
    else:
        # 返回 emoji 后备
        return icon_tuple[1]


def get_fluent_icon_font(size: int = 16) -> QFont:
    """
    获取 Fluent Icons 字体
    
    Args:
        size: 字体大小
    
    Returns:
        QFont 对象
    """
    if USE_FLUENT_ICONS:
        # Fluent Icons 使用 Segoe Fluent Icons 字体
        font = QFont("Segoe Fluent Icons")
        font.setPointSize(size)
        return font
    else:
        # 降级使用 emoji 字体
        font = QFont("Segoe UI Emoji")
        font.setPointSize(size)
        return font


def get_fluent_icon_stylesheet(icon_name: str, size: int = 16, color: str = None) -> str:
    """
    获取 Fluent Icon 样式表
    
    Args:
        icon_name: FluentIcon 名称
        size: 字体大小
        color: 颜色（可选）
    
    Returns:
        样式表字符串
    """
    if USE_FLUENT_ICONS:
        style = f"""
            font-family: "Segoe Fluent Icons", "Segoe MDL2 Assets";
            font-size: {size}px;
        """
    else:
        style = f"""
            font-family: "Segoe UI Emoji", "Apple Color Emoji";
            font-size: {size}px;
        """
    
    if color:
        style += f"color: {color};"
    
    return style


# 兼容性别名，保持与旧代码兼容
MaterialIcon = FluentIcons
get_icon = get_fluent_icon
get_icon_font = get_fluent_icon_font
