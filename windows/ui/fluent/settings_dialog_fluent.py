"""
设置对话框模块 - Fluent 设计风格（世界级配色版）
使用 PyQt-Fluent-Widgets 组件
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QLineEdit, QCheckBox, QGroupBox, QFormLayout,
    QComboBox, QMessageBox, QScrollArea, QWidget, QFrame
)
from PyQt6.QtGui import QFont

from config import settings
from utils.logger import get_logger
from utils.theme import THEMES, get_current_theme
from utils.fluent_icons import FluentIcons, get_icon, get_icon_font

try:
    from PyQtFluentWidgets import (
        SettingCardGroup, PushSettingCard, ComboBoxSettingCard,
        SpinBoxSettingCard, SwitchSettingCard, PrimaryPushButton,
        FluentIcon as FIcon, InfoBar, InfoBarPosition
    )
    USE_FLUENT = True
except ImportError:
    USE_FLUENT = False

logger = get_logger('SettingsDialog')


class SettingsDialog(QDialog):
    """设置对话框 - Fluent 风格（世界级配色）"""

    settings_changed = pyqtSignal()
    clear_history_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_capturing = False
        self._captured_hotkey = None

        # 初始化控件引用
        self.theme_combo = None
        self.max_items_spin = None
        self.hotkey_edit = None
        self.hotkey_capture_btn = None
        self.enable_text_check = None
        self.enable_image_check = None
        self.enable_file_check = None
        self.enable_html_check = None
        self.auto_hide_check = None
        self.show_on_copy_check = None
        self.startup_minimized_check = None

        self._init_ui()
        self._load_settings()
        self._apply_theme()

    def _init_ui(self) -> None:
        """初始化 UI"""
        self.setWindowTitle("设置")
        self.setMinimumWidth(520)
        self.setMinimumHeight(650)

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 标题栏
        header = self._create_header()
        main_layout.addWidget(header)

        # 滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        # 内容容器
        self.content_widget = QWidget()
        self.content_widget.setObjectName("content_widget")
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(24, 20, 24, 24)
        self.content_layout.setSpacing(20)
        self.content_widget.setLayout(self.content_layout)

        self.scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(self.scroll_area, 1)

        # 底部按钮区域
        footer = self._create_footer()
        main_layout.addWidget(footer)

        self.setLayout(main_layout)

        # 创建设置项
        self._create_setting_items()

    def _create_header(self) -> QWidget:
        """创建标题栏"""
        header = QWidget()
        header.setFixedHeight(72)
        header.setObjectName("header")

        layout = QHBoxLayout()
        layout.setContentsMargins(24, 20, 24, 16)

        self.title_label = QLabel("⚙️ 设置")
        title_font = QFont("Microsoft YaHei", 18)
        title_font.setWeight(QFont.Weight.Bold)
        self.title_label.setFont(title_font)
        self.title_label.setObjectName("title_label")

        layout.addWidget(self.title_label)
        layout.addStretch()
        header.setLayout(layout)
        return header

    def _create_footer(self) -> QWidget:
        """创建底部按钮区"""
        footer = QWidget()
        footer.setFixedHeight(80)
        footer.setObjectName("footer")

        layout = QHBoxLayout()
        layout.setContentsMargins(24, 16, 24, 20)
        layout.setSpacing(12)

        # 清除历史按钮
        self.clear_btn = QPushButton()
        self.clear_btn.setText(f"{get_icon(FluentIcons.CLEAR)}  清除历史记录")
        self.clear_btn.setFixedHeight(44)
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.clicked.connect(self._on_clear_history)
        self.clear_btn.setFont(get_icon_font(14))
        self.clear_btn.setObjectName("clear_btn")

        layout.addWidget(self.clear_btn)
        layout.addStretch()

        # 确定/取消按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setFixedHeight(44)
        self.cancel_btn.setFixedWidth(100)
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setObjectName("cancel_btn")

        self.ok_btn = QPushButton("确定")
        self.ok_btn.setFixedHeight(44)
        self.ok_btn.setFixedWidth(100)
        self.ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ok_btn.clicked.connect(self._on_ok)
        self.ok_btn.setObjectName("ok_btn")

        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.ok_btn)
        layout.addLayout(button_layout)

        footer.setLayout(layout)
        return footer

    def _create_setting_items(self) -> None:
        """创建设置项"""
        # 主题设置卡片
        self._create_theme_card()

        # 历史记录设置卡片
        self._create_history_card()

        # 快捷键设置卡片
        self._create_hotkey_card()

        # 数据类型设置组
        self._create_data_type_group()

        # 行为设置组
        self._create_behavior_group()

    def _create_theme_card(self) -> None:
        """创建主题选择卡片"""
        card = QFrame()
        card.setObjectName("theme_card")
        card.setFrameShape(QFrame.Shape.NoFrame)
        card.setMinimumHeight(80)

        layout = QHBoxLayout()
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        # 图标和标签
        icon_label = QLabel("🎨")
        icon_label.setStyleSheet('font-family: "Segoe UI Emoji", "Apple Color Emoji", sans-serif; font-size: 24px; background: transparent;')

        title_label = QLabel("颜色主题")
        title_label.setStyleSheet('font-family: "Microsoft YaHei", sans-serif; font-size: 14px; font-weight: 600; background: transparent;')

        # 主题选择下拉框
        self.theme_combo = QComboBox()
        self.theme_combo.setMinimumWidth(180)
        self.theme_combo.setMaximumWidth(240)
        self.theme_combo.setFixedHeight(36)
        for theme_id, theme_data in THEMES.items():
            self.theme_combo.addItem(theme_data['name'], theme_id)
        self.theme_combo.setObjectName("theme_combo")

        # 连接主题改变信号
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)

        layout.addWidget(icon_label)
        layout.addWidget(title_label, 1)
        layout.addWidget(self.theme_combo)
        card.setLayout(layout)

        self.content_layout.addWidget(card)

    def _create_history_card(self) -> None:
        """创建历史记录卡片"""
        card = QFrame()
        card.setObjectName("history_card")
        card.setFrameShape(QFrame.Shape.NoFrame)
        card.setMinimumHeight(80)

        layout = QHBoxLayout()
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        # 图标和标签
        icon_label = QLabel("📋")
        icon_label.setStyleSheet('font-family: "Segoe UI Emoji", "Apple Color Emoji", sans-serif; font-size: 24px; background: transparent;')

        title_label = QLabel("最大记录数")
        title_label.setStyleSheet('font-family: "Microsoft YaHei", sans-serif; font-size: 14px; font-weight: 600; background: transparent;')

        # 数字输入框
        self.max_items_spin = QSpinBox()
        self.max_items_spin.setRange(10, 1000)
        self.max_items_spin.setSingleStep(10)
        self.max_items_spin.setValue(100)
        self.max_items_spin.setFixedWidth(120)
        self.max_items_spin.setFixedHeight(36)
        self.max_items_spin.setObjectName("max_items_spin")

        layout.addWidget(icon_label)
        layout.addWidget(title_label, 1)
        layout.addWidget(self.max_items_spin)
        card.setLayout(layout)

        self.content_layout.addWidget(card)

    def _create_hotkey_card(self) -> None:
        """创建快捷键卡片"""
        card = QFrame()
        card.setObjectName("hotkey_card")
        card.setFrameShape(QFrame.Shape.NoFrame)
        card.setMinimumHeight(100)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # 标题行
        header_layout = QHBoxLayout()

        icon_label = QLabel("⌨️")
        icon_label.setStyleSheet('font-family: "Segoe UI Emoji", "Apple Color Emoji", sans-serif; font-size: 24px; background: transparent;')

        title_label = QLabel("全局快捷键")
        title_label.setStyleSheet('font-family: "Microsoft YaHei", sans-serif; font-size: 14px; font-weight: 600; background: transparent;')

        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # 输入区域
        input_layout = QHBoxLayout()
        input_layout.setSpacing(12)

        self.hotkey_edit = QLineEdit()
        self.hotkey_edit.setPlaceholderText("点击录制按钮后按下快捷键")
        self.hotkey_edit.setReadOnly(True)
        self.hotkey_edit.setFixedHeight(40)
        self.hotkey_edit.setObjectName("hotkey_edit")

        self.hotkey_capture_btn = QPushButton("录制")
        self.hotkey_capture_btn.setCheckable(True)
        self.hotkey_capture_btn.setFixedWidth(80)
        self.hotkey_capture_btn.setFixedHeight(40)
        self.hotkey_capture_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.hotkey_capture_btn.clicked.connect(self._on_capture_hotkey)
        self.hotkey_capture_btn.setObjectName("hotkey_capture_btn")

        input_layout.addWidget(self.hotkey_edit)
        input_layout.addWidget(self.hotkey_capture_btn)

        layout.addLayout(input_layout)

        card.setLayout(layout)
        self.content_layout.addWidget(card)

    def _create_data_type_group(self) -> None:
        """创建数据类型设置组"""
        group = QGroupBox("支持的复制类型")
        group.setObjectName("data_type_group")

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 20, 16, 16)

        self.enable_text_check = QCheckBox("文本内容")
        self.enable_text_check.setObjectName("enable_text_check")

        self.enable_image_check = QCheckBox("图片内容")
        self.enable_image_check.setObjectName("enable_image_check")

        self.enable_file_check = QCheckBox("文件内容")
        self.enable_file_check.setObjectName("enable_file_check")

        self.enable_html_check = QCheckBox("HTML / 富文本内容")
        self.enable_html_check.setObjectName("enable_html_check")

        layout.addWidget(self.enable_text_check)
        layout.addWidget(self.enable_image_check)
        layout.addWidget(self.enable_file_check)
        layout.addWidget(self.enable_html_check)

        group.setLayout(layout)
        self.content_layout.addWidget(group)

    def _create_behavior_group(self) -> None:
        """创建行为设置组"""
        group = QGroupBox("行为设置")
        group.setObjectName("behavior_group")

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 20, 16, 16)

        self.auto_hide_check = QCheckBox("失去焦点时自动隐藏窗口")
        self.auto_hide_check.setObjectName("auto_hide_check")

        self.show_on_copy_check = QCheckBox("复制时自动显示窗口")
        self.show_on_copy_check.setObjectName("show_on_copy_check")

        self.startup_minimized_check = QCheckBox("启动时最小化到系统托盘")
        self.startup_minimized_check.setObjectName("startup_minimized_check")

        layout.addWidget(self.auto_hide_check)
        layout.addWidget(self.show_on_copy_check)
        layout.addWidget(self.startup_minimized_check)

        group.setLayout(layout)
        self.content_layout.addWidget(group)

    def _apply_theme(self) -> None:
        """应用主题样式（世界级配色）"""
        theme = get_current_theme()

        # 对话框整体样式
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {theme['background']};
                color: {theme['text']};
                border-radius: 12px;
            }}
        """)

        # 标题栏样式
        if hasattr(self, 'header'):
            self.header.setStyleSheet(f"""
                QWidget#header {{
                    background-color: {theme['surface']};
                    border-bottom: 1px solid {theme['border']};
                    border-top-left-radius: 12px;
                    border-top-right-radius: 12px;
                }}
            """)
        
        # 标题标签样式
        if hasattr(self, 'title_label'):
            self.title_label.setStyleSheet(f"""
                color: {theme['text']};
                font-size: 18px;
                font-weight: 600;
                background: transparent;
            """)

        # 滚动区域样式
        if hasattr(self, 'scroll_area'):
            self.scroll_area.setStyleSheet(f"""
                QScrollArea {{
                    border: none;
                    background-color: {theme['background']};
                }}
                QScrollArea > QWidget > QWidget {{
                    background-color: {theme['background']};
                }}
                QScrollBar:vertical {{
                    background-color: {theme['surface']};
                    width: 8px;
                    border-radius: 4px;
                    margin: 4px;
                }}
                QScrollBar::handle:vertical {{
                    background-color: {theme['border']};
                    border-radius: 4px;
                    min-height: 30px;
                }}
                QScrollBar::handle:vertical:hover {{
                    background-color: {theme['accent']};
                }}
                QScrollBar::add-line:vertical,
                QScrollBar::sub-line:vertical {{
                    height: 0px;
                }}
            """)

        # 内容容器样式
        if hasattr(self, 'content_widget'):
            self.content_widget.setStyleSheet(f"""
                QWidget#content_widget {{
                    background-color: {theme['background']};
                }}
            """)

        # 卡片样式（精美卡片设计）
        card_base_style = f"""
            QFrame {{
                background-color: {theme['surface']};
                border: 1px solid {theme['border_light']};
                border-radius: 12px;
            }}
            QFrame:hover {{
                border: 1px solid {theme['border_focus']};
                background-color: {theme['surface_hover']};
            }}
            QLabel {{
                color: {theme['text']};
                background: transparent;
            }}
            QLabel#desc_label {{
                color: {theme['text_secondary']};
                font-size: 12px;
            }}
        """

        for card_name in ["theme_card", "history_card", "hotkey_card"]:
            card = self.findChild(QFrame, card_name)
            if card:
                card.setStyleSheet(card_base_style)

        # 下拉框样式
        if hasattr(self, 'theme_combo'):
            self.theme_combo.setStyleSheet(f"""
                QComboBox {{
                    background-color: {theme['background']};
                    border: 2px solid {theme['border_light']};
                    border-radius: 8px;
                    padding: 8px 12px;
                    color: {theme['text']};
                    font-size: 13px;
                    min-height: 20px;
                }}
                QComboBox:hover {{
                    border: 2px solid {theme['border_focus']};
                }}
                QComboBox:focus {{
                    border: 2px solid {theme['accent']};
                }}
                QComboBox::drop-down {{
                    border: none;
                    width: 30px;
                }}
                QComboBox QAbstractItemView {{
                    background-color: {theme['surface']};
                    border: 1px solid {theme['border']};
                    border-radius: 8px;
                    color: {theme['text']};
                    selection-background-color: {theme['accent']};
                    selection-color: white;
                    padding: 4px;
                }}
            """)

        # 数字输入框样式
        if hasattr(self, 'max_items_spin'):
            self.max_items_spin.setStyleSheet(f"""
                QSpinBox {{
                    background-color: {theme['background']};
                    border: 2px solid {theme['border_light']};
                    border-radius: 8px;
                    padding: 8px 12px;
                    color: {theme['text']};
                    font-size: 13px;
                }}
                QSpinBox:hover {{
                    border: 2px solid {theme['border_focus']};
                }}
                QSpinBox:focus {{
                    border: 2px solid {theme['accent']};
                }}
                QSpinBox::up-button, QSpinBox::down-button {{
                    background-color: {theme['surface']};
                    border: none;
                    width: 20px;
                    border-radius: 4px;
                }}
                QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                    background-color: {theme['accent']};
                }}
            """)

        # 输入框样式
        if hasattr(self, 'hotkey_edit'):
            self.hotkey_edit.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {theme['background']};
                    border: 2px solid {theme['border_light']};
                    border-radius: 8px;
                    padding: 10px 14px;
                    color: {theme['text']};
                    font-size: 13px;
                }}
                QLineEdit:hover {{
                    border: 2px solid {theme['border_focus']};
                }}
                QLineEdit:focus {{
                    border: 2px solid {theme['accent']};
                }}
            """)

        # 录制按钮样式
        if hasattr(self, 'hotkey_capture_btn'):
            self.hotkey_capture_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {theme['surface']};
                    color: {theme['text']};
                    border: 2px solid {theme['border_light']};
                    border-radius: 8px;
                    padding: 10px 16px;
                    font-size: 13px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {theme['surface_hover']};
                    border: 2px solid {theme['border_focus']};
                }}
                QPushButton:pressed {{
                    background-color: {theme['surface_active']};
                }}
                QPushButton:checked {{
                    background-color: {theme['danger']};
                    color: white;
                    border: 2px solid {theme['danger']};
                }}
            """)

        # GroupBox 样式
        group_base_style = f"""
            QGroupBox {{
                background-color: {theme['surface']};
                border: 1px solid {theme['border_light']};
                border-radius: 12px;
                margin-top: 8px;
                padding-top: 28px;
                padding-bottom: 16px;
                padding-left: 16px;
                padding-right: 16px;
                font-weight: 600;
                font-size: 14px;
                color: {theme['text']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                top: 8px;
                padding: 0 8px;
                color: {theme['text']};
            }}
        """

        for group_name in ["data_type_group", "behavior_group"]:
            group = self.findChild(QGroupBox, group_name)
            if group:
                group.setStyleSheet(group_base_style)

        # 复选框样式
        for checkbox in self.findChildren(QCheckBox):
            checkbox.setStyleSheet(f"""
                QCheckBox {{
                    color: {theme['text']};
                    spacing: 10px;
                    font-size: 13px;
                    padding: 4px;
                }}
                QCheckBox::indicator {{
                    width: 20px;
                    height: 20px;
                    border: 2px solid {theme['border']};
                    border-radius: 6px;
                    background-color: {theme['background']};
                }}
                QCheckBox::indicator:hover {{
                    border: 2px solid {theme['accent']};
                }}
                QCheckBox::indicator:checked {{
                    background-color: {theme['accent']};
                    border: 2px solid {theme['accent']};
                }}
            """)

        # 底部栏样式
        if hasattr(self, 'footer'):
            self.footer.setStyleSheet(f"""
                QWidget#footer {{
                    background-color: {theme['surface']};
                    border-top: 1px solid {theme['border']};
                    border-bottom-left-radius: 12px;
                    border-bottom-right-radius: 12px;
                }}
            """)

        # 按钮样式
        if hasattr(self, 'cancel_btn'):
            self.cancel_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {theme['surface']};
                    color: {theme['text']};
                    border: 2px solid {theme['border_light']};
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-size: 13px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {theme['surface_hover']};
                    border: 2px solid {theme['border_focus']};
                }}
                QPushButton:pressed {{
                    background-color: {theme['surface_active']};
                }}
            """)

        if hasattr(self, 'ok_btn'):
            self.ok_btn.setStyleSheet(f"""
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
            """)

        if hasattr(self, 'clear_btn'):
            self.clear_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {theme['danger_bg']};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-size: 13px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {theme['danger_hover']};
                }}
                QPushButton:pressed {{
                    background-color: {theme['danger']};
                }}
            """)

        # 提示标签样式
        hint_label = self.findChild(QLabel, "hint_label")
        if hint_label:
            hint_label.setStyleSheet(f"""
                color: {theme['text_muted']};
                font-size: 11px;
                background: transparent;
            """)

    def _load_settings(self) -> None:
        """加载设置"""
        # 主题
        current_theme = settings.get('theme', 'dark')
        if self.theme_combo:
            index = self.theme_combo.findData(current_theme)
            if index >= 0:
                self.theme_combo.setCurrentIndex(index)

        if self.max_items_spin:
            self.max_items_spin.setValue(settings.get('max_history_items', 100))

        if self.hotkey_edit:
            self._captured_hotkey = settings.get('global_hotkey', 'ctrl+shift+v')
            self.hotkey_edit.setText(self._format_hotkey_for_display(self._captured_hotkey))

        if self.auto_hide_check:
            self.auto_hide_check.setChecked(settings.get('auto_hide', True))
        if self.show_on_copy_check:
            self.show_on_copy_check.setChecked(settings.get('show_on_copy', False))
        if self.startup_minimized_check:
            self.startup_minimized_check.setChecked(settings.get('startup_minimized', False))

        if self.enable_text_check:
            self.enable_text_check.setChecked(settings.get('enable_text', True))
        if self.enable_image_check:
            self.enable_image_check.setChecked(settings.get('enable_image', True))
        if self.enable_file_check:
            self.enable_file_check.setChecked(settings.get('enable_file', True))
        if self.enable_html_check:
            self.enable_html_check.setChecked(settings.get('enable_html', True))

    def _on_theme_changed(self, index: int) -> None:
        """主题改变处理"""
        theme_id = self.theme_combo.itemData(index)
        if theme_id:
            # 保存主题设置
            settings.set('theme', theme_id)
            logger.info(f"Theme changed to: {theme_id}")
            # 重新应用主题
            self._apply_theme()
            # 强制刷新
            self.update()
            self.repaint()

    def _format_hotkey_for_display(self, hotkey: str) -> str:
        """格式化快捷键用于显示"""
        if not hotkey:
            return ""

        keys = hotkey.lower().split('+')
        key_map = {
            'ctrl': 'Ctrl',
            'shift': 'Shift',
            'alt': 'Alt',
            'win': 'Win',
        }

        formatted = []
        for key in keys:
            key = key.strip()
            if key in key_map:
                formatted.append(key_map[key])
            else:
                formatted.append(key.upper())

        return ' + '.join(formatted)

    def _on_capture_hotkey(self) -> None:
        """开始/停止录制快捷键"""
        self._is_capturing = self.hotkey_capture_btn.isChecked()

        if self._is_capturing:
            theme = get_current_theme()
            self.hotkey_edit.setText("请按下快捷键...")
            self.hotkey_edit.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {theme['background']};
                    border: 2px solid {theme['accent']};
                    border-radius: 8px;
                    padding: 10px 14px;
                    color: {theme['accent']};
                    font-size: 13px;
                }}
            """)
            self.hotkey_capture_btn.setText("停止")
            self.grabKeyboard()
        else:
            self._stop_capture()

    def _stop_capture(self) -> None:
        """停止录制"""
        self._is_capturing = False
        self.hotkey_capture_btn.setChecked(False)
        self.hotkey_capture_btn.setText("录制")

        # 恢复输入框样式
        theme = get_current_theme()
        self.hotkey_edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: {theme['background']};
                border: 2px solid {theme['border_light']};
                border-radius: 8px;
                padding: 10px 14px;
                color: {theme['text']};
                font-size: 13px;
            }}
            QLineEdit:hover {{
                border: 2px solid {theme['border_focus']};
            }}
            QLineEdit:focus {{
                border: 2px solid {theme['accent']};
            }}
        """)

        self.releaseKeyboard()

        if self._captured_hotkey:
            self.hotkey_edit.setText(self._format_hotkey_for_display(self._captured_hotkey))
        else:
            self.hotkey_edit.clear()

    def keyPressEvent(self, event) -> None:
        """键盘事件处理 - 录制快捷键"""
        if not self._is_capturing:
            super().keyPressEvent(event)
            return

        modifiers = []
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            modifiers.append('ctrl')
        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            modifiers.append('shift')
        if event.modifiers() & Qt.KeyboardModifier.AltModifier:
            modifiers.append('alt')

        key = event.key()
        special_keys = {
            Qt.Key.Key_Control: None,
            Qt.Key.Key_Shift: None,
            Qt.Key.Key_Alt: None,
            Qt.Key.Key_Meta: None,
            Qt.Key.Key_Escape: None,
        }

        if key in special_keys:
            super().keyPressEvent(event)
            return

        if key == Qt.Key.Key_Escape:
            self._stop_capture()
            return

        if not modifiers:
            self.hotkey_edit.setText("需要修饰键 (Ctrl/Shift/Alt)")
            return

        key_name = None
        if Qt.Key.Key_F1 <= key <= Qt.Key.Key_F12:
            key_name = f"f{key - Qt.Key.Key_F1 + 1}"
        elif Qt.Key.Key_Space == key:
            key_name = "space"
        elif Qt.Key.Key_Return == key or Qt.Key.Key_Enter == key:
            key_name = "enter"
        elif Qt.Key.Key_Tab == key:
            key_name = "tab"
        elif Qt.Key.Key_Backspace == key:
            key_name = "backspace"
        elif Qt.Key.Key_Delete == key:
            key_name = "delete"
        elif Qt.Key.Key_Insert == key:
            key_name = "insert"
        elif Qt.Key.Key_Home == key:
            key_name = "home"
        elif Qt.Key.Key_End == key:
            key_name = "end"
        elif Qt.Key.Key_PageUp == key:
            key_name = "pageup"
        elif Qt.Key.Key_PageDown == key:
            key_name = "pagedown"
        elif Qt.Key.Key_Up == key:
            key_name = "up"
        elif Qt.Key.Key_Down == key:
            key_name = "down"
        elif Qt.Key.Key_Left == key:
            key_name = "left"
        elif Qt.Key.Key_Right == key:
            key_name = "right"
        else:
            key_name = chr(key).lower()

        if key_name:
            hotkey = '+'.join(modifiers + [key_name])
            self._captured_hotkey = hotkey
            self.hotkey_edit.setText(self._format_hotkey_for_display(hotkey))
            logger.info(f"Captured hotkey: {hotkey}")
            self._stop_capture()

    def _on_clear_history(self) -> None:
        """清除历史记录"""
        reply = QMessageBox.question(
            self,
            "清除历史记录",
            "确定要清除所有剪贴板历史记录吗？\n此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            logger.info("Clear history requested from settings")
            self.clear_history_requested.emit()
            if USE_FLUENT:
                InfoBar.success(
                    title='清除完成',
                    content='所有剪贴板历史记录已清除',
                    parent=self.window(),
                    duration=1000,
                    position=InfoBarPosition.TOP
                )

    def _on_ok(self) -> None:
        """确定按钮点击"""
        if self.theme_combo:
            theme_id = self.theme_combo.currentData()
            if theme_id:
                settings.set('theme', theme_id)
                logger.info(f"Theme changed to: {theme_id}")

        if self.max_items_spin:
            settings.set('max_history_items', self.max_items_spin.value())
        if self.auto_hide_check:
            settings.set('auto_hide', self.auto_hide_check.isChecked())
        if self.show_on_copy_check:
            settings.set('show_on_copy', self.show_on_copy_check.isChecked())
        if self.startup_minimized_check:
            settings.set('startup_minimized', self.startup_minimized_check.isChecked())

        if self.enable_text_check:
            settings.set('enable_text', self.enable_text_check.isChecked())
        if self.enable_image_check:
            settings.set('enable_image', self.enable_image_check.isChecked())
        if self.enable_file_check:
            settings.set('enable_file', self.enable_file_check.isChecked())
        if self.enable_html_check:
            settings.set('enable_html', self.enable_html_check.isChecked())

        if self._captured_hotkey:
            settings.set('global_hotkey', self._captured_hotkey)
            logger.info(f"Saved hotkey: {self._captured_hotkey}")

        logger.info("Settings saved")
        self.settings_changed.emit()

        if USE_FLUENT:
            InfoBar.success(
                title='设置已保存',
                content='所有设置已成功保存',
                parent=self.window(),
                duration=1000,
                position=InfoBarPosition.TOP
            )

        self.accept()

    def get_new_hotkey(self) -> str:
        """获取新设置的快捷键"""
        return self._captured_hotkey

    def showEvent(self, event) -> None:
        """显示事件 - 确保主题正确应用"""
        super().showEvent(event)
        self._apply_theme()
