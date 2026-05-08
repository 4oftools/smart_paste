"""
主窗口模块
应用程序的主界面窗口
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
from ui.classic.search_bar_classic import SearchBar
from ui.classic.filter_panel_classic import FilterPanel
from ui.classic.history_panel_classic import HistoryPanel
from ui.classic.preview_panel_classic import PreviewPanel
from ui.classic.settings_dialog_classic import SettingsDialog
from utils.theme import get_current_theme, apply_theme_to_widget, get_top_bar_stylesheet, get_footer_stylesheet, _hex_to_rgb
from utils.fluent_icons import FluentIcons, get_icon, get_icon_font
from utils.logger import get_logger
from utils.fluent_theme import apply_fluent_theme


class MainWindow(QWidget):
    """主窗口"""

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

        # 加载历史记录（需要在 UI 初始化之后）
        self._load_history()

    def _init_ui(self) -> None:
        """初始化 UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 顶部栏
        top_bar = self._create_top_bar()
        layout.addWidget(top_bar)

        # 过滤面板
        self.filter_panel = FilterPanel()
        layout.addWidget(self.filter_panel)

        # 内容区域（左右分栏）
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # 历史面板
        self.history_panel = HistoryPanel()
        content_layout.addWidget(self.history_panel)

        # 预览面板
        self.preview_panel = PreviewPanel()
        content_layout.addWidget(self.preview_panel)

        self.content_widget = QWidget()
        self.content_widget.setLayout(content_layout)
        theme = get_current_theme()
        self.content_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {theme['background']};
            }}
        """)
        layout.addWidget(self.content_widget, 1)

        # 底部提示
        footer = self._create_footer()
        layout.addWidget(footer)

        self.setLayout(layout)

        # 加载外部样式表
        self._load_stylesheet()
        self._apply_style()

    def _create_top_bar(self) -> QWidget:
        """创建顶部栏"""
        self.top_bar = QWidget()
        self.top_bar.setFixedHeight(60)

        layout = QHBoxLayout()
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(12)

        # 搜索栏
        self.search_bar = SearchBar()

        # 设置按钮
        self.settings_btn = QPushButton()
        self.settings_btn.setText(get_icon(FluentIcons.SETTINGS))
        self.settings_btn.setFixedSize(40, 40)
        self.settings_btn.setFlat(True)
        self.settings_btn.clicked.connect(self._on_settings_clicked)
        self.settings_btn.setFont(get_icon_font(20))

        # 隐藏按钮
        self.hide_btn = QPushButton()
        self.hide_btn.setText(get_icon(FluentIcons.CLOSE))
        self.hide_btn.setFixedSize(40, 40)
        self.hide_btn.setFlat(True)
        self.hide_btn.clicked.connect(self._on_hide_clicked)
        self.hide_btn.setFont(get_icon_font(20))

        layout.addWidget(self.search_bar, 1)
        layout.addWidget(self.settings_btn)
        layout.addWidget(self.hide_btn)

        self.top_bar.setLayout(layout)
        self.top_bar.setStyleSheet(get_top_bar_stylesheet())
        
        # 启用顶部栏的鼠标跟踪
        self.top_bar.setAttribute(Qt.WidgetAttribute.WA_Hover)

        return self.top_bar

    def _create_footer(self) -> QWidget:
        """创建底部提示"""
        footer = QWidget()
        footer.setFixedHeight(30)

        layout = QHBoxLayout()
        layout.setContentsMargins(16, 0, 16, 0)

        hint_label = QLabel()
        hint_label.setText("↑↓ 选择  Enter 复制  Esc 关闭  Ctrl+Shift+V 唤起")
        hint_label.setObjectName("hint_label")

        layout.addWidget(hint_label)
        layout.addStretch()

        footer.setLayout(layout)
        footer.setStyleSheet(get_footer_stylesheet())

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
        self.resize(settings.get('window_width', 900), settings.get('window_height', 600))

    def _apply_style(self) -> None:
        """应用样式"""
        theme = get_current_theme()
        
        self.setStyleSheet(f"""
            MainWindow {{
                background-color: {theme['background']};
                border-radius: 12px;
            }}
        """)

        # 设置窗口透明圆角背景
        self._setup_rounded_background()

        # 应用主题到子组件
        self._apply_theme_to_children()

    def _apply_theme_to_children(self) -> None:
        """应用主题到子组件"""
        theme = get_current_theme()

        # 更新内容区域背景（避免切换主题后仍为旧主题底色）
        if hasattr(self, 'content_widget'):
            self.content_widget.setStyleSheet(f"""
                QWidget {{
                    background-color: {theme['background']};
                }}
            """)

        # 更新背景
        if hasattr(self, 'background'):
            self.background.setStyleSheet(f"""
                QFrame#background {{
                    background-color: {theme['background']};
                    border-radius: 12px;
                    border: 1px solid {theme['border']};
                }}
            """)

        # 更新顶部栏
        if hasattr(self, 'settings_btn') and self.settings_btn.parent():
            apply_theme_to_widget(self.settings_btn.parent(), 'top_bar')

        # 更新历史面板
        if hasattr(self, 'history_panel'):
            apply_theme_to_widget(self.history_panel, 'history_panel')
            # 更新历史项
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

    def apply_theme(self) -> None:
        """应用当前主题（公开方法）"""
        self._apply_style()

    def _load_stylesheet(self) -> None:
        """加载外部样式表。已禁用 styles.qss 的加载，避免其硬编码深色主题覆盖多主题配色。"""
        # 不再加载 resources/styles.qss，其内容为固定深色主题，会导致切换主题后
        # 部分全局选择器（*、QPushButton、QLineEdit 等）仍为深色。所有样式由
        # utils.theme 与 _apply_style / apply_theme_to_widget 按当前主题动态应用。
        pass

    def _setup_rounded_background(self) -> None:
        """设置圆角背景"""
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        theme = get_current_theme()

        # 创建背景控件
        self.background = QFrame(self)
        self.background.setObjectName("background")
        self.background.setStyleSheet(f"""
            QFrame#background {{
                background-color: {theme['background']};
                border-radius: 12px;
                border: 1px solid {theme['border']};
            }}
        """)

        # 调整背景大小
        self._adjust_background()

        # 将背景放到最底层，避免遮挡其他控件
        self.background.lower()

    def _adjust_background(self) -> None:
        """调整背景大小"""
        self.background.setGeometry(0, 0, self.width(), self.height())

    def resizeEvent(self, event) -> None:
        """窗口大小变化"""
        super().resizeEvent(event)
        self._adjust_background()

    def _connect_signals(self) -> None:
        """连接信号"""
        # 搜索栏
        self.search_bar.search_changed.connect(self._on_search_changed)
        self.search_bar.clear_requested.connect(self._on_search_cleared)

        # 过滤面板
        self.filter_panel.filter_changed.connect(self._on_filter_changed)

        # 历史面板
        self.history_panel.item_selected.connect(self._on_item_selected)
        self.history_panel.favorite_toggled.connect(self._on_favorite_toggled)
        self.history_panel.copy_requested.connect(self._on_copy_requested)
        self.history_panel.delete_requested.connect(self._on_delete_requested)

        # 预览面板
        self.preview_panel.copy_clicked.connect(self._on_copy_clicked)
        self.preview_panel.delete_clicked.connect(self._on_delete_clicked)

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

    def _on_item_selected(self, item: ClipboardItem) -> None:
        """项选中处理"""
        self.preview_panel.set_item(item)

    def _on_favorite_toggled(self, item: ClipboardItem) -> None:
        """收藏状态变化处理"""
        self.storage.update_favorite(item.id, not item.is_favorite)
        self._load_history()

    def _on_copy_requested(self) -> None:
        """复制请求处理"""
        item = self.history_panel.get_selected_item()
        if item:
            ClipboardMonitor.set_content(item)

    def _on_delete_requested(self) -> None:
        """删除请求处理"""
        item = self.history_panel.get_selected_item()
        if item:
            self._delete_item(item)

    def _on_copy_clicked(self) -> None:
        """复制按钮点击处理"""
        item = self.preview_panel.current_item
        if item:
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

    def _load_history(self) -> None:
        """加载历史记录"""
        from models.enums import FilterType
        
        # 根据过滤类型获取数据
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
        
        # 搜索过滤
        if self.search_text:
            items = self.storage.search(self.search_text)
        
        self.history_panel.set_items(items)
        logger = get_logger('MainWindow')
        logger.info(f"Loaded {len(items)} items to history panel")

    def _on_settings_clicked(self) -> None:
        """设置按钮点击处理"""
        dialog = SettingsDialog(self)
        dialog.settings_changed.connect(self._on_settings_changed)
        dialog.exec()

    def _on_settings_changed(self) -> None:
        """设置更改处理"""
        # 重新加载历史记录
        self._load_history()

    def _on_hide_clicked(self) -> None:
        """隐藏按钮点击处理"""
        self._hide_with_animation()

    def show_at_cursor(self) -> None:
        """在光标位置显示窗口"""
        cursor_pos = QCursor.pos()

        # 获取屏幕信息
        from PyQt6.QtGui import QGuiApplication
        screen = QGuiApplication.screenAt(cursor_pos)
        if screen:
            screen_geometry = screen.availableGeometry()
        else:
            screen_geometry = screen.availableGeometry()

        # 计算窗口位置（居中显示）
        x = cursor_pos.x() - self.width() // 2
        y = cursor_pos.y() - self.height() // 2

        # 确保窗口不超出屏幕
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
            # 复制选中项
            item = self.history_panel.get_selected_item()
            if item:
                ClipboardMonitor.set_content(item)
        elif event.key() == Qt.Key.Key_Up:
            # 选择上一项
            self.history_panel.select_previous()
        elif event.key() == Qt.Key.Key_Down:
            # 选择下一项
            self.history_panel.select_next()
        elif event.key() == Qt.Key.Key_Delete:
            # 删除选中项
            item = self.history_panel.get_selected_item()
            if item:
                self._delete_item(item)
        else:
            # 将其他按键传递给搜索栏
            if not self.search_bar.search_input.hasFocus():
                self.search_bar.search_input.keyPressEvent(event)

        super().keyPressEvent(event)

    def eventFilter(self, obj, event) -> bool:
        """事件过滤器 - 处理顶部栏拖拽"""
        from PyQt6.QtCore import QEvent
        
        # 处理顶部栏的鼠标事件用于拖拽
        if obj == self.top_bar:
            if event.type() == QEvent.Type.MouseButtonPress:
                if event.button() == Qt.MouseButton.LeftButton:
                    self._drag_start_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                    event.accept()
                    return True
            elif event.type() == QEvent.Type.MouseMove:
                if self._drag_start_pos is not None:
                    self.move(event.globalPosition().toPoint() - self._drag_start_pos)
                    event.accept()
                    return True
            elif event.type() == QEvent.Type.MouseButtonRelease:
                self._drag_start_pos = None
                event.accept()
                return True
        
        return super().eventFilter(obj, event)

    def mousePressEvent(self, event) -> None:
        """鼠标按下事件 - 处理窗口拖拽"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 检查点击位置是否在顶部栏
            if event.position().y() <= 60:  # 顶部栏高度
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

    def _create_text_pixmap(self, text: str) -> QImage:
        """创建文本缩略图（使用当前主题色）"""
        from PyQt6.QtGui import QPainter, QFont, QColor
        from PyQt6.QtCore import QRect

        theme = get_current_theme()
        r, g, b = _hex_to_rgb(theme['surface'])
        bg_color = QColor(r, g, b, 230)
        r, g, b = _hex_to_rgb(theme['text'])
        text_color = QColor(r, g, b)

        pixmap = QImage(200, 60, QImage.Format.Format_ARGB32)
        pixmap.fill(bg_color)

        painter = QPainter(pixmap)
        painter.setPen(text_color)
        painter.setFont(QFont("Microsoft YaHei", 10))
        painter.drawText(QRect(10, 10, 180, 40), Qt.TextFlag.TextWordWrap, text)
        painter.end()

        return pixmap
