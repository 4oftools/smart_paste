"""
主窗口模块
应用程序的主界面窗口 - Fluent 设计风格
"""

from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QMimeData, QByteArray
from PyQt6.QtGui import QCursor, QIcon, QDrag, QImage
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QDialog
)

from core.clipboard_monitor import ClipboardMonitor
from core.storage import Storage
from models.clipboard_item import ClipboardItem
from models.enums import FilterType
from ui.fluent.search_bar_fluent import SearchBar
from ui.fluent.filter_panel_fluent import FilterPanel
from ui.fluent.history_panel_fluent import HistoryPanel
from ui.fluent.preview_panel_fluent import PreviewPanel
from ui.fluent.settings_dialog_fluent import SettingsDialog
from utils.theme import get_current_theme, apply_theme_to_widget
from utils.fluent_icons import FluentIcons, get_icon, get_icon_font
from utils.logger import get_logger
from utils.fluent_theme import apply_fluent_theme, get_fluent_stylesheet


class MainWindow(QWidget):
    """主窗口 - Fluent 设计风格"""

    def __init__(self, storage: Storage, monitor: ClipboardMonitor, parent=None):
        super().__init__(parent)

        self.storage = storage
        self.monitor = monitor
        self.current_filter = FilterType.ALL
        self.search_text = ""

        # 动画相关
        self.fade_in_animation = None
        self.fade_out_animation = None
        
        # 拖拽相关
        self._drag_pos = None
        self._drag_start_pos = None

        self._init_ui()
        self._setup_window()
        self._connect_signals()
        self._apply_fluent_style()

        # 加载历史记录
        self._load_history()

    def _init_ui(self) -> None:
        """初始化 UI"""
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建背景卡片
        self.background_card = QFrame()
        self.background_card.setObjectName("background_card")
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)
        self.background_card.setLayout(card_layout)

        # 顶部栏
        top_bar = self._create_top_bar()
        card_layout.addWidget(top_bar)

        # 过滤面板
        self.filter_panel = FilterPanel()
        card_layout.addWidget(self.filter_panel)

        # 内容区域
        content_frame = QFrame()
        content_frame.setObjectName("content_frame")
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_frame.setLayout(content_layout)

        # 历史面板
        self.history_panel = HistoryPanel()
        content_layout.addWidget(self.history_panel, 1)

        # 分隔线
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.VLine)
        divider.setObjectName("divider")
        content_layout.addWidget(divider)

        # 预览面板
        self.preview_panel = PreviewPanel()
        content_layout.addWidget(self.preview_panel, 1)

        card_layout.addWidget(content_frame, 1)

        # 底部状态栏
        footer = self._create_footer()
        card_layout.addWidget(footer)

        main_layout.addWidget(self.background_card)
        self.setLayout(main_layout)

        self._apply_fluent_style()

    def _create_top_bar(self) -> QWidget:
        """创建顶部栏"""
        top_bar = QWidget()
        top_bar.setFixedHeight(60)
        top_bar.setObjectName("top_bar")

        layout = QHBoxLayout()
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(12)

        # 标题
        title_label = QLabel("📋 Smart Paste")
        title_label.setObjectName("title_label")
        title_label.setStyleSheet("font-size: 16px; font-weight: 600;")

        # 搜索栏
        self.search_bar = SearchBar()

        # 设置按钮
        self.settings_btn = QPushButton()
        self.settings_btn.setText(get_icon(FluentIcons.SETTINGS))
        self.settings_btn.setFixedSize(40, 40)
        self.settings_btn.setFlat(True)
        self.settings_btn.clicked.connect(self._on_settings_clicked)
        self.settings_btn.setFont(get_icon_font(20))
        self.settings_btn.setObjectName("icon_btn")

        # 隐藏按钮
        self.hide_btn = QPushButton()
        self.hide_btn.setText(get_icon(FluentIcons.CLOSE))
        self.hide_btn.setFixedSize(40, 40)
        self.hide_btn.setFlat(True)
        self.hide_btn.clicked.connect(self._on_hide_clicked)
        self.hide_btn.setFont(get_icon_font(20))
        self.hide_btn.setObjectName("icon_btn")

        layout.addWidget(title_label)
        layout.addWidget(self.search_bar, 1)
        layout.addWidget(self.settings_btn)
        layout.addWidget(self.hide_btn)

        top_bar.setLayout(layout)
        self.top_bar = top_bar

        return top_bar

    def _create_footer(self) -> QWidget:
        """创建底部提示"""
        footer = QWidget()
        footer.setFixedHeight(36)
        footer.setObjectName("footer")

        layout = QHBoxLayout()
        layout.setContentsMargins(20, 0, 20, 0)

        from utils.theme import get_current_theme
        theme = get_current_theme()
        hint_label = QLabel("↑↓ 选择  ·  Enter 复制  ·  Esc 关闭  ·  Ctrl+Shift+V 唤起")
        hint_label.setObjectName("hint_label")
        hint_label.setStyleSheet(f"color: {theme['text_muted']}; font-size: 11px;")

        layout.addWidget(hint_label)
        layout.addStretch()

        footer.setLayout(layout)
        return footer

    def _setup_window(self) -> None:
        """设置窗口属性"""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        from config import settings
        self.resize(settings.get('window_width', 1000), settings.get('window_height', 650))

    def _apply_fluent_style(self) -> None:
        """应用 Fluent 风格（随当前主题）"""
        from utils.theme import get_current_theme
        theme = get_current_theme()
        
        # 背景卡片样式
        self.background_card.setStyleSheet(f"""
            QFrame#background_card {{
                background-color: {theme['surface']};
                border: 1px solid {theme['border']};
                border-radius: 12px;
            }}
        """)
        
        # 顶部栏样式
        self.top_bar.setStyleSheet(f"""
            QWidget#top_bar {{
                background-color: {theme['surface']};
                border-bottom: 1px solid {theme['border']};
                border-radius: 12px 12px 0 0;
            }}
        """)
        
        # 内容区域样式
        for child in self.findChildren(QFrame, "content_frame"):
            child.setStyleSheet(f"""
                QFrame#content_frame {{
                    background-color: {theme['background']};
                }}
            """)
        
        # 底部样式
        footer = self.findChild(QWidget, "footer")
        if footer:
            footer.setStyleSheet(f"""
                QWidget#footer {{
                    background-color: {theme['surface']};
                    border-top: 1px solid {theme['border']};
                    border-radius: 0 0 12px 12px;
                }}
                QLabel {{
                    color: {theme['text_muted']};
                }}
            """)
        
        # 分隔线样式
        for child in self.findChildren(QFrame, "divider"):
            child.setStyleSheet(f"""
                QFrame#divider {{
                    background-color: {theme['border']};
                    max-width: 1px;
                }}
            """)
        
        # 图标按钮样式
        for btn in self.findChildren(QPushButton, "icon_btn"):
            btn.setStyleSheet(f"""
                QPushButton#icon_btn {{
                    background-color: transparent;
                    border: none;
                    border-radius: 20px;
                    color: {theme['text_secondary']};
                    font-size: 20px;
                }}
                QPushButton#icon_btn:hover {{
                    background-color: {theme['surface_hover']};
                    color: {theme['text']};
                }}
                QPushButton#icon_btn:pressed {{
                    background-color: {theme['surface_active']};
                }}
            """)

    def apply_theme(self) -> None:
        """应用当前主题"""
        self._apply_fluent_style()
        self._apply_theme_to_children()

    def _apply_theme_to_children(self) -> None:
        """应用主题到子组件"""
        # 更新历史面板
        if hasattr(self, 'history_panel'):
            apply_theme_to_widget(self.history_panel, 'history_panel')
            for widget in self.history_panel.item_widgets:
                apply_theme_to_widget(widget, 'item_widget')

        # 更新预览面板
        if hasattr(self, 'preview_panel'):
            apply_theme_to_widget(self.preview_panel, 'preview_panel')

        # 更新搜索栏
        if hasattr(self, 'search_bar'):
            apply_theme_to_widget(self.search_bar, 'search_bar')

        # 更新过滤面板
        if hasattr(self, 'filter_panel'):
            apply_theme_to_widget(self.filter_panel, 'filter_panel')

    def _load_history(self) -> None:
        """加载历史记录"""
        from models.enums import FilterType
        
        if self.current_filter == FilterType.FAVORITE:
            items = self.storage.get_all(favorite_only=True)
        elif self.current_filter == FilterType.TEXT:
            from core.clipboard_monitor import ContentType
            items = self.storage.get_all(content_type=ContentType.TEXT)
        elif self.current_filter == FilterType.IMAGE:
            from core.clipboard_monitor import ContentType
            items = self.storage.get_all(content_type=ContentType.IMAGE)
        elif self.current_filter == FilterType.FILE:
            from core.clipboard_monitor import ContentType
            items = self.storage.get_all(content_type=ContentType.FILE)
        else:
            items = self.storage.get_all()
        
        if self.search_text:
            items = self.storage.search(self.search_text)
        
        self.history_panel.set_items(items)
        logger = get_logger('MainWindow')
        logger.info(f"Loaded {len(items)} items to history panel")

    def refresh(self) -> None:
        """刷新窗口"""
        self._load_history()

    def _on_settings_clicked(self) -> None:
        """设置按钮点击处理"""
        dialog = SettingsDialog(self)
        dialog.settings_changed.connect(self._on_settings_changed)
        dialog.exec()

    def _on_settings_changed(self) -> None:
        """设置更改处理"""
        self._load_history()

    def _on_hide_clicked(self) -> None:
        """隐藏按钮点击处理"""
        self._hide_with_animation()

    def show_at_cursor(self) -> None:
        """在光标位置显示窗口"""
        cursor_pos = QCursor.pos()

        from PyQt6.QtGui import QGuiApplication
        screen = QGuiApplication.screenAt(cursor_pos)
        if screen:
            screen_geometry = screen.availableGeometry()
        else:
            screen_geometry = QGuiApplication.primaryScreen().availableGeometry()

        x = cursor_pos.x() - self.width() // 2
        y = cursor_pos.y() - self.height() // 2

        x = max(screen_geometry.x(), min(x, screen_geometry.right() - self.width()))
        y = max(screen_geometry.y(), min(y, screen_geometry.bottom() - self.height()))

        self.move(x, y)
        self._show_with_animation()

    def _show_with_animation(self) -> None:
        """显示窗口（带动画）"""
        self.show()
        self.activateWindow()
        self.raise_()
        self.setFocus()

    def _hide_with_animation(self) -> None:
        """隐藏窗口（带动画）"""
        self.hide()

    def keyPressEvent(self, event) -> None:
        """键盘事件处理"""
        if event.key() == Qt.Key.Key_Escape:
            self._hide_with_animation()
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            item = self.history_panel.get_selected_item()
            if item:
                from core.clipboard_monitor import ClipboardMonitor
                ClipboardMonitor.set_content(item)
        elif event.key() == Qt.Key.Key_Up:
            self.history_panel.select_previous()
        elif event.key() == Qt.Key.Key_Down:
            self.history_panel.select_next()
        elif event.key() == Qt.Key.Key_Delete:
            item = self.history_panel.get_selected_item()
            if item:
                self._delete_item(item)
        else:
            if not self.search_bar.search_input.hasFocus():
                self.search_bar.search_input.keyPressEvent(event)

        super().keyPressEvent(event)

    def mousePressEvent(self, event) -> None:
        """鼠标按下事件 - 处理窗口拖拽"""
        if event.button() == Qt.MouseButton.LeftButton:
            if event.position().y() <= 60:
                self._drag_start_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        """鼠标移动事件 - 处理窗口拖拽"""
        if self._drag_start_pos is not None:
            if event.buttons() & Qt.MouseButton.LeftButton:
                self.move(event.globalPosition().toPoint() - self._drag_start_pos)
                event.accept()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_pos = None
        super().mouseReleaseEvent(event)

    def _on_copy_requested(self) -> None:
        """复制请求处理"""
        item = self.history_panel.get_selected_item()
        if item:
            from core.clipboard_monitor import ClipboardMonitor
            ClipboardMonitor.set_content(item)

    def _on_delete_requested(self) -> None:
        """删除请求处理"""
        item = self.history_panel.get_selected_item()
        if item:
            self._delete_item(item)

    def _on_item_selected(self, item: ClipboardItem) -> None:
        """项选中处理"""
        self.preview_panel.set_item(item)

    def _on_favorite_toggled(self, item: ClipboardItem) -> None:
        """收藏状态变化处理"""
        self.storage.update_favorite(item.id, not item.is_favorite)
        self._load_history()

    def _on_copy_clicked(self) -> None:
        """复制按钮点击处理"""
        item = self.preview_panel.current_item
        if item:
            from core.clipboard_monitor import ClipboardMonitor
            ClipboardMonitor.set_content(item)

    def _on_delete_clicked(self) -> None:
        """删除按钮点击处理"""
        item = self.preview_panel.current_item
        if item:
            self._delete_item(item)

    def _delete_item(self, item: ClipboardItem) -> None:
        """删除项"""
        self.storage.delete(item.id)
        self._load_history()

    def _on_search_changed(self, text: str) -> None:
        """搜索文本变化处理"""
        self.search_text = text
        self._load_history()

    def _on_search_cleared(self) -> None:
        """搜索清除处理"""
        self.search_text = ""
        self._load_history()

    def _on_filter_changed(self, filter_type: FilterType) -> None:
        """过滤类型变化处理"""
        self.current_filter = filter_type
        self._load_history()

    def _connect_signals(self) -> None:
        """连接信号"""
        self.search_bar.search_changed.connect(self._on_search_changed)
        self.search_bar.clear_requested.connect(self._on_search_cleared)
        self.filter_panel.filter_changed.connect(self._on_filter_changed)
        self.history_panel.item_selected.connect(self._on_item_selected)
        self.history_panel.favorite_toggled.connect(self._on_favorite_toggled)
        self.history_panel.copy_requested.connect(self._on_copy_requested)
        self.history_panel.delete_requested.connect(self._on_delete_requested)
        self.preview_panel.copy_clicked.connect(self._on_copy_clicked)
        self.preview_panel.delete_clicked.connect(self._on_delete_clicked)
