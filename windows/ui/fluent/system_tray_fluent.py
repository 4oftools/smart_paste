"""
系统托盘模块
提供系统托盘图标和右键菜单功能
"""

from PyQt6.QtCore import Qt, QObject, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QMenu, QApplication, QSystemTrayIcon

from utils.logger import get_logger
from utils.theme import THEMES, get_theme_id
from utils.fluent_icons import FluentIcons, get_icon, get_icon_font
from config import settings

# 获取日志器
logger = get_logger('SystemTray')


class SystemTray(QObject):
    """系统托盘管理类"""

    # 信号：显示窗口请求
    show_window_requested = pyqtSignal()
    # 信号：退出请求
    exit_requested = pyqtSignal()
    # 信号：设置请求
    settings_requested = pyqtSignal()
    # 信号：清空历史请求
    clear_history_requested = pyqtSignal()
    # 信号：主题切换请求
    theme_changed_requested = pyqtSignal(str)
    # 信号：复制请求
    copy_requested = pyqtSignal(object)

    def __init__(self, storage=None, parent=None):
        super().__init__(parent)

        self.tray_icon = None
        self.storage = storage
        self.theme_actions = {}
        self.recent_actions = []
        self._setup_tray()
        logger.info("System tray initialized")

    def _setup_tray(self) -> None:
        """设置系统托盘"""
        # 创建托盘图标
        self.tray_icon = QSystemTrayIcon(self)

        # 创建图标（使用简单文本作为图标）
        icon = self._create_icon()
        self.tray_icon.setIcon(icon)

        # 创建右键菜单
        menu = self._create_context_menu()
        self.tray_icon.setContextMenu(menu)

        # 显示提示
        self.tray_icon.setToolTip("Smart Paste - 剪贴板历史管理器\n按 Ctrl+Shift+V 唤起")

        # 显示托盘图标
        self.tray_icon.show()

        logger.info("System tray icon displayed")

    def _create_icon(self) -> QIcon:
        """创建托盘图标"""
        # 创建一个简单的图标
        from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont

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

    def _create_context_menu(self) -> QMenu:
        """
        创建右键菜单

        Returns:
            菜单对象
        """
        menu = QMenu()

        # 显示/隐藏主窗口
        self.show_action = QAction(f"{get_icon(FluentIcons.VIEW)}  显示主窗口", self)
        self.show_action.triggered.connect(self._on_show_window)
        menu.addAction(self.show_action)

        # 最近记录子菜单
        self.recent_menu = menu.addMenu(f"{get_icon(FluentIcons.LIST)}  最近记录")
        self.recent_menu.aboutToShow.connect(self._on_recent_menu_about_to_show)

        menu.addSeparator()

        # 主题切换子菜单
        theme_menu = menu.addMenu(f"{get_icon(FluentIcons.PALETTE)}  主题")
        self._create_theme_menu(theme_menu)

        menu.addSeparator()

        # 清空历史记录
        self.clear_action = QAction(f"{get_icon(FluentIcons.CLEAR)}  清空历史", self)
        self.clear_action.triggered.connect(self._on_clear_history)
        menu.addAction(self.clear_action)

        # 设置
        self.settings_action = QAction(f"{get_icon(FluentIcons.SETTINGS)}  设置", self)
        self.settings_action.triggered.connect(self._on_settings)
        menu.addAction(self.settings_action)

        menu.addSeparator()

        # 退出
        self.exit_action = QAction(f"{get_icon(FluentIcons.CLOSE)}  退出", self)
        self.exit_action.triggered.connect(self._on_exit)
        menu.addAction(self.exit_action)

        logger.debug("Context menu created")

        return menu

    def _create_theme_menu(self, theme_menu: QMenu) -> None:
        """
        创建主题切换菜单

        Args:
            theme_menu: 主题菜单对象
        """
        current_theme = get_theme_id()

        for theme_id, theme_data in THEMES.items():
            action = QAction(theme_data['name'], self)
            action.setCheckable(True)
            action.setChecked(theme_id == current_theme)
            action.triggered.connect(lambda checked, tid=theme_id: self._on_theme_changed(tid))
            theme_menu.addAction(action)
            self.theme_actions[theme_id] = action

    def _create_recent_menu(self, recent_menu: QMenu) -> None:
        """
        创建最近记录菜单

        Args:
            recent_menu: 最近记录菜单对象
        """
        # 清除旧的 action
        for action in self.recent_actions:
            recent_menu.removeAction(action)
        self.recent_actions.clear()

        if self.storage is None:
            recent_menu.setEnabled(False)
            return

        # 获取最近 20 条记录
        items = self.storage.get_all(limit=20)

        if not items:
            no_data_action = QAction("暂无记录", self)
            no_data_action.setEnabled(False)
            recent_menu.addAction(no_data_action)
            self.recent_actions.append(no_data_action)
            return

        # 添加记录到菜单
        for item in items:
            # 根据内容类型选择图标
            if item.content_type.value == "image":
                icon = get_icon(FluentIcons.IMAGE)
            elif item.content_type.value == "file":
                icon = get_icon(FluentIcons.FOLDER)
            else:
                icon = get_icon(FluentIcons.DOCUMENT)

            # 截取内容前 50 个字符作为显示文本
            display_text = item.content[:50].replace('\n', ' ')
            if len(item.content) > 50:
                display_text += "..."

            action = QAction(f"{icon} {display_text}", self)
            action.triggered.connect(lambda checked, i=item: self._on_copy_recent(i))
            recent_menu.addAction(action)
            self.recent_actions.append(action)

    def _on_copy_recent(self, item) -> None:
        """
        复制最近记录

        Args:
            item: 剪贴板项
        """
        from core.clipboard_monitor import ClipboardMonitor
        logger.info(f"Copy recent item: type={item.content_type.value}")
        ClipboardMonitor.set_content(item)
        self.show_message("已复制", "内容已复制到剪贴板", 1000)

    def refresh_recent_menu(self) -> None:
        """
        刷新最近记录菜单
        当有新内容时调用
        """
        # 清空现有项，下次打开菜单时会重新加载
        for action in self.recent_actions:
            self.recent_menu.removeAction(action)
        self.recent_actions.clear()

    def _on_recent_menu_about_to_show(self) -> None:
        """
        最近记录菜单即将显示时调用
        动态加载最新的 20 条记录
        """
        # 清空现有项
        self.refresh_recent_menu()
        
        # 重新创建菜单项
        self._create_recent_menu(self.recent_menu)

    def _on_theme_changed(self, theme_id: str) -> None:
        """
        主题切换处理

        Args:
            theme_id: 主题 ID
        """
        logger.info(f"Theme changed to: {theme_id}")
        settings.set('theme', theme_id)

        # 更新菜单选中状态
        for tid, action in self.theme_actions.items():
            action.setChecked(tid == theme_id)

        self.theme_changed_requested.emit(theme_id)

    def update_theme_menu(self, current_theme: str) -> None:
        """
        更新主题菜单选中状态

        Args:
            current_theme: 当前主题 ID
        """
        for theme_id, action in self.theme_actions.items():
            action.setChecked(theme_id == current_theme)

    def _on_show_window(self) -> None:
        """显示主窗口"""
        logger.debug("Show window requested from tray menu")
        self.show_window_requested.emit()

    def _on_clear_history(self) -> None:
        """清空历史记录"""
        logger.debug("Clear history requested from tray menu")
        # 延迟显示对话框，避免菜单关闭时触发问题
        QTimer.singleShot(100, self._show_clear_confirm_dialog)

    def _show_clear_confirm_dialog(self) -> None:
        """显示清空历史确认对话框"""
        from PyQt6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            None,
            "清空历史",
            "确定要清空所有剪贴板历史记录吗？\n此操作不可撤销。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            logger.info("History cleared from tray menu")
            self.clear_history_requested.emit()

    def _on_settings(self) -> None:
        """打开设置"""
        logger.debug("Settings requested from tray menu")
        self.settings_requested.emit()

    def _on_exit(self) -> None:
        """退出应用"""
        logger.debug("Exit requested from tray menu")
        # 延迟显示对话框，避免菜单关闭时触发问题
        QTimer.singleShot(100, self._show_exit_confirm_dialog)

    def _show_exit_confirm_dialog(self) -> None:
        """显示退出确认对话框"""
        from PyQt6.QtWidgets import QMessageBox

        reply = QMessageBox.question(
            None,
            "退出",
            "确定要退出 Smart Paste 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            logger.info("Exit confirmed from tray menu")
            self.exit_requested.emit()

    def show_message(self, title: str, message: str, duration: int = 3000) -> None:
        """
        显示托盘通知消息

        Args:
            title: 标题
            message: 消息内容
            duration: 显示时长（毫秒）
        """
        self.tray_icon.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, duration)

    def set_tooltip(self, text: str) -> None:
        """
        设置托盘图标提示

        Args:
            text: 提示文本
        """
        self.tray_icon.setToolTip(text)

    def hide(self) -> None:
        """隐藏托盘图标"""
        if self.tray_icon:
            self.tray_icon.hide()
            logger.debug("System tray icon hidden")
