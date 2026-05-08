"""
Smart Paste - Windows 剪贴板历史管理器
Fluent Design 版本
仿照 Paste 的功能和界面风格，采用 Fluent Design 设计语言
"""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.QtGui import QFont

from core.clipboard_monitor import ClipboardMonitor
from core.storage import Storage
from core.hotkey_manager import HotkeyManager
from ui.fluent.main_window_fluent import MainWindow
from ui.fluent.system_tray_fluent import SystemTray
from config import settings
from utils.logger import get_logger

# 获取日志器
logger = get_logger('SmartPaste')


class SmartPasteApp:
    """Smart Paste Fluent 应用主类"""

    def __init__(self):
        logger.info("Starting Smart Paste Fluent...")

        # 创建应用
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Smart Paste")
        self.app.setOrganizationName("Smart Paste")

        # 设置当最后一个窗口关闭时不退出应用（托盘应用需要）
        self.app.setQuitOnLastWindowClosed(False)

        # 设置字体
        font = QFont("Microsoft YaHei", 10)
        self.app.setFont(font)

        # 初始化组件
        logger.info("Initializing components...")
        self.storage = Storage()
        self.monitor = ClipboardMonitor()
        self.hotkey_manager = HotkeyManager()

        # 创建系统托盘
        self.system_tray = SystemTray(self.storage)

        # 创建主窗口 - 使用 Fluent 版本
        self.main_window = MainWindow(self.storage, self.monitor)

        # 连接信号
        self._connect_signals()

        # 注册全局热键
        self._register_hotkey()

        # 连接系统托盘信号
        self.system_tray.show_window_requested.connect(self._show_window)
        self.system_tray.exit_requested.connect(self._exit_app)
        self.system_tray.settings_requested.connect(self._show_settings)
        self.system_tray.clear_history_requested.connect(self._clear_history)
        self.system_tray.theme_changed_requested.connect(self._on_theme_changed_from_tray)
        self.system_tray.copy_requested.connect(self._on_copy_from_tray)

        logger.info("Application initialized successfully")

    def _connect_signals(self) -> None:
        """连接信号"""
        # 连接剪贴板监控信号
        self.monitor.new_content.connect(self._on_new_content)

    def _on_new_content(self, item) -> None:
        """新剪贴板内容处理"""
        # 保存到数据库
        item_id = self.storage.add(item)
        if item_id:
            logger.debug(f"New clipboard item saved: type={item.content_type.value}, size={item.display_size}")
            # 刷新历史列表
            self.main_window._load_history()

            # 刷新托盘最近记录菜单
            self.system_tray.refresh_recent_menu()

            # 如果设置了复制时自动显示
            if settings.get('show_on_copy', False):
                self.main_window.show_at_cursor()
        else:
            logger.debug("Clipboard item already exists (duplicate)")

    def _register_hotkey(self) -> None:
        """注册全局热键"""
        try:
            hotkey = settings.get('hotkey', 'ctrl+shift+v')
            self.hotkey_manager.register(hotkey, self._on_hotkey_triggered)
            logger.info(f"Registering global hotkey: {hotkey}")
        except Exception as e:
            logger.error(f"Failed to register hotkey: {e}")

    def _on_hotkey_triggered(self) -> None:
        """热键触发处理"""
        logger.debug("Global hotkey triggered")
        self._show_window()

    def _show_window(self) -> None:
        """显示主窗口"""
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()

    def _show_settings(self) -> None:
        """显示设置对话框 - 使用 Fluent 版本"""
        from ui.fluent.settings_dialog_fluent import SettingsDialog
        dialog = SettingsDialog(self.main_window)
        dialog.settings_changed.connect(self._on_settings_changed)
        dialog.clear_history_requested.connect(self._clear_history)
        dialog.exec()

    def _on_settings_changed(self) -> None:
        """设置更改处理"""
        logger.info("Settings changed, reloading...")
        # 重新加载设置
        self._register_hotkey()
        # 刷新主窗口
        self.main_window.refresh()

    def _clear_history(self) -> None:
        """清空历史记录"""
        logger.info("Clearing history...")
        self.storage.clear_all()
        self.main_window.refresh()

    def _on_theme_changed_from_tray(self, theme_id: str) -> None:
        """从托盘菜单切换主题"""
        logger.info(f"Theme changed from tray: {theme_id}")
        from config import settings as app_settings
        app_settings.set('theme', theme_id)
        # 应用主题到所有窗口
        self._apply_theme_to_all_windows(theme_id)
        # 刷新主窗口
        self.main_window.refresh()

    def _apply_theme_to_all_windows(self, theme_id: str) -> None:
        """应用主题到所有窗口"""
        from utils.theme import get_current_theme
        theme = get_current_theme()
        # 应用主题到主窗口
        if hasattr(self.main_window, '_apply_fluent_style'):
            self.main_window._apply_fluent_style()
        # 应用主题到所有子对话框
        for widget in self.app.topLevelWidgets():
            if isinstance(widget, QDialog) and widget.isVisible():
                if hasattr(widget, '_apply_theme'):
                    widget._apply_theme()

    def _on_copy_from_tray(self, item) -> None:
        """从托盘菜单复制项目"""
        logger.info(f"Copy from tray: item_id={item.id if hasattr(item, 'id') else 'unknown'}")
        if hasattr(item, 'content'):
            import pyperclip
            pyperclip.copy(item.content)

    def _exit_app(self) -> None:
        """退出应用"""
        logger.info("Exiting application...")
        self.hotkey_manager.unregister()
        self.app.quit()

    def run(self) -> int:
        """运行应用"""
        logger.info("Starting application event loop...")
        return self.app.exec()


def main():
    """主函数"""
    app = SmartPasteApp()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
