"""
设置对话框模块
应用程序的设置界面
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSpinBox, QLineEdit, QCheckBox, QGroupBox, QFormLayout,
    QComboBox, QMessageBox
)
from PyQt6.QtGui import QIcon, QPainter, QColor, QFont, QPixmap

from config import settings
from utils.logger import get_logger
from utils.theme import THEMES, get_current_theme, get_settings_dialog_stylesheet
from utils.fluent_icons import FluentIcons, get_icon, get_icon_font

logger = get_logger('SettingsDialog')


class SettingsDialog(QDialog):
    """设置对话框"""

    # 信号：设置已更改
    settings_changed = pyqtSignal()
    # 信号：清除历史记录
    clear_history_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._is_capturing = False
        self._captured_hotkey = None
        self._loading_settings = False

        # 必须设置，否则 Windows 下 QDialog 不会绘制样式表背景，背景色出不来
        self.setObjectName("settings_dialog")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._init_ui()
        self._load_settings()

    def _init_ui(self) -> None:
        """初始化 UI"""
        self.setWindowTitle("设置")
        self.setMinimumWidth(480)
        
        # 设置窗口图标（与托盘图标一致）
        self.setWindowIcon(self._create_window_icon())

        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # ========== 主题设置 ==========
        theme_group = QGroupBox("主题")
        theme_layout = QFormLayout()
        theme_layout.setSpacing(10)

        self.theme_combo = QComboBox()
        self.theme_combo.setMinimumWidth(200)
        for theme_id, theme_data in THEMES.items():
            self.theme_combo.addItem(theme_data['name'], theme_id)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)

        theme_layout.addRow("颜色主题:", self.theme_combo)

        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        # ========== 历史记录设置 ==========
        history_group = QGroupBox("历史记录")
        history_layout = QFormLayout()
        history_layout.setSpacing(10)

        self.max_items_spin = QSpinBox()
        self.max_items_spin.setRange(10, 1000)
        self.max_items_spin.setSingleStep(10)
        self.max_items_spin.setMinimumWidth(150)

        history_layout.addRow("最大记录数:", self.max_items_spin)

        history_group.setLayout(history_layout)
        layout.addWidget(history_group)

        # ========== 快捷键设置 ==========
        hotkey_group = QGroupBox("快捷键")
        hotkey_layout = QFormLayout()
        hotkey_layout.setSpacing(10)

        self.hotkey_edit = QLineEdit()
        self.hotkey_edit.setPlaceholderText("点击录制按钮后按下快捷键")
        self.hotkey_edit.setReadOnly(True)
        self.hotkey_edit.setMinimumWidth(200)

        self.hotkey_capture_btn = QPushButton("录制")
        self.hotkey_capture_btn.setCheckable(True)
        self.hotkey_capture_btn.setFixedWidth(80)
        self.hotkey_capture_btn.clicked.connect(self._on_capture_hotkey)

        hotkey_row = QHBoxLayout()
        hotkey_row.addWidget(self.hotkey_edit)
        hotkey_row.addWidget(self.hotkey_capture_btn)
        hotkey_row.addStretch()

        hotkey_layout.addRow("全局快捷键:", hotkey_row)

        # 快捷键提示
        theme = get_current_theme()
        hint_label = QLabel("提示：快捷键需要包含 Ctrl、Shift 或 Alt")
        hint_label.setObjectName("hint_label")
        hint_label.setStyleSheet(f"color: {theme['text_muted']}; font-size: 11px;")
        hotkey_layout.addRow("", hint_label)

        hotkey_group.setLayout(hotkey_layout)
        layout.addWidget(hotkey_group)

        # ========== 数据类型设置 ==========
        data_type_group = QGroupBox("支持的复制类型")
        data_type_layout = QVBoxLayout()
        data_type_layout.setSpacing(10)

        self.enable_text_check = QCheckBox("文本")
        self.enable_image_check = QCheckBox("图片")
        self.enable_file_check = QCheckBox("文件")
        self.enable_html_check = QCheckBox("HTML/富文本")

        data_type_layout.addWidget(self.enable_text_check)
        data_type_layout.addWidget(self.enable_image_check)
        data_type_layout.addWidget(self.enable_file_check)
        data_type_layout.addWidget(self.enable_html_check)

        data_type_group.setLayout(data_type_layout)
        layout.addWidget(data_type_group)

        # ========== 行为设置 ==========
        behavior_group = QGroupBox("行为")
        behavior_layout = QVBoxLayout()
        behavior_layout.setSpacing(10)

        self.auto_hide_check = QCheckBox("失去焦点自动隐藏")
        self.show_on_copy_check = QCheckBox("复制时自动显示")
        self.startup_minimized_check = QCheckBox("启动时最小化到托盘")

        behavior_layout.addWidget(self.auto_hide_check)
        behavior_layout.addWidget(self.show_on_copy_check)
        behavior_layout.addWidget(self.startup_minimized_check)

        behavior_group.setLayout(behavior_layout)
        layout.addWidget(behavior_group)

        # ========== 清除历史记录 ==========
        clear_group = QGroupBox("数据管理")
        clear_layout = QHBoxLayout()
        clear_layout.setSpacing(10)

        theme = get_current_theme()
        clear_label = QLabel("清除所有剪贴板历史记录")
        clear_label.setObjectName("clear_label")
        clear_label.setStyleSheet(f"color: {theme['danger']};")

        self.clear_btn = QPushButton()
        self.clear_btn.setText(f"{get_icon(FluentIcons.CLEAR)}  清除历史记录")
        self.clear_btn.setFixedWidth(180)
        self.clear_btn.clicked.connect(self._on_clear_history)
        self.clear_btn.setFont(get_icon_font(16))

        clear_layout.addWidget(clear_label)
        clear_layout.addStretch()
        clear_layout.addWidget(self.clear_btn)

        clear_group.setLayout(clear_layout)
        layout.addWidget(clear_group)

        # ========== 按钮 ==========
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.ok_btn = QPushButton("确定")
        self.ok_btn.setFixedWidth(100)
        self.ok_btn.clicked.connect(self._on_ok)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setFixedWidth(100)
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self._apply_style()

    def _load_settings(self) -> None:
        """加载设置"""
        self._loading_settings = True
        # 主题
        current_theme = settings.get('theme', 'dark')
        index = self.theme_combo.findData(current_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        self._loading_settings = False

        self.max_items_spin.setValue(settings.get('max_history_items', 100))
        self._captured_hotkey = settings.get('global_hotkey', 'ctrl+shift+v')
        self.hotkey_edit.setText(self._format_hotkey_for_display(self._captured_hotkey))
        self.auto_hide_check.setChecked(settings.get('auto_hide', True))
        self.show_on_copy_check.setChecked(settings.get('show_on_copy', False))
        self.startup_minimized_check.setChecked(settings.get('startup_minimized', False))

        # 加载数据类型设置
        self.enable_text_check.setChecked(settings.get('enable_text', True))
        self.enable_image_check.setChecked(settings.get('enable_image', True))
        self.enable_file_check.setChecked(settings.get('enable_file', True))
        self.enable_html_check.setChecked(settings.get('enable_html', True))

    def _create_window_icon(self) -> QIcon:
        """创建窗口图标（与托盘图标一致）"""
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)

        # 绘制圆形背景
        painter.setBrush(QColor(94, 129, 172))  # #5E81AC
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, 32, 32)

        # 绘制文字
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "S")

        painter.end()

        return QIcon(pixmap)

    def _apply_style(self) -> None:
        """应用样式"""
        self.setStyleSheet(get_settings_dialog_stylesheet())
        self.cancel_btn.setObjectName("cancel_btn")
        self.clear_btn.setObjectName("clear_btn")

    def _on_theme_changed(self, index: int) -> None:
        """主题下拉变更：立即保存并刷新设置页样式，使页面随所选主题切换"""
        if self._loading_settings:
            return
        theme_id = self.theme_combo.itemData(index)
        if not theme_id:
            return
        settings.set('theme', theme_id)
        logger.info(f"Theme changed to: {theme_id}")
        self._apply_style()
        self._update_theme_dependent_styles()
        self.update()
        self.repaint()

    def _update_theme_dependent_styles(self) -> None:
        """更新依赖主题的内联样式（下拉变更后与整体风格一致）"""
        theme = get_current_theme()
        hint = self.findChild(QLabel, "hint_label")
        if hint:
            hint.setStyleSheet(f"color: {theme['text_muted']}; font-size: 11px;")
        clear_label = self.findChild(QLabel, "clear_label")
        if clear_label:
            clear_label.setStyleSheet(f"color: {theme['danger']};")

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
            self.hotkey_edit.setText("请按下快捷键...")
            theme = get_current_theme()
            self.hotkey_edit.setStyleSheet(f"""
                background-color: {theme['surface_hover']};
                border: 2px solid {theme['accent']};
                border-radius: 6px;
                padding: 8px 12px;
                color: {theme['accent']};
                min-height: 24px;
                font-size: 13px;
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
        self.hotkey_edit.setStyleSheet("")  # 恢复默认样式
        self.releaseKeyboard()

        # 恢复显示
        if self._captured_hotkey:
            self.hotkey_edit.setText(self._format_hotkey_for_display(self._captured_hotkey))
        else:
            self.hotkey_edit.clear()

    def keyPressEvent(self, event) -> None:
        """键盘事件处理 - 录制快捷键"""
        if not self._is_capturing:
            super().keyPressEvent(event)
            return

        # 获取修饰键
        modifiers = []
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            modifiers.append('ctrl')
        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            modifiers.append('shift')
        if event.modifiers() & Qt.KeyboardModifier.AltModifier:
            modifiers.append('alt')

        # 获取按键
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

        # 获取按键名称
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

    def _on_ok(self) -> None:
        """确定按钮点击"""
        # 保存主题
        theme_id = self.theme_combo.currentData()
        if theme_id:
            settings.set('theme', theme_id)
            logger.info(f"Theme changed to: {theme_id}")

        # 保存其他设置
        settings.set('max_history_items', self.max_items_spin.value())
        settings.set('auto_hide', self.auto_hide_check.isChecked())
        settings.set('show_on_copy', self.show_on_copy_check.isChecked())
        settings.set('startup_minimized', self.startup_minimized_check.isChecked())

        # 保存数据类型设置
        settings.set('enable_text', self.enable_text_check.isChecked())
        settings.set('enable_image', self.enable_image_check.isChecked())
        settings.set('enable_file', self.enable_file_check.isChecked())
        settings.set('enable_html', self.enable_html_check.isChecked())

        if self._captured_hotkey:
            settings.set('global_hotkey', self._captured_hotkey)
            logger.info(f"Saved hotkey: {self._captured_hotkey}")

        logger.info("Settings saved")

        self.settings_changed.emit()
        self.accept()

    def get_new_hotkey(self) -> str:
        """获取新设置的快捷键"""
        return self._captured_hotkey
