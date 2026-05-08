"""
Smart Paste - Windows 剪贴板历史管理器
仿照 Paste 的功能和界面风格
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
from ui.classic.main_window_classic import MainWindow
from ui.classic.system_tray_classic import SystemTray
from config import settings
from utils.logger import get_logger

# 获取日志器
logger = get_logger('SmartPaste')


class SmartPasteApp:
    """Smart Paste 应用主类"""

    def __init__(self):
        logger.info("Starting Smart Paste...")

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

        # 创建主窗口
        self.main_window = MainWindow(self.storage, self.monitor)

        # 连接信号
        self._connect_signals()

        # 注册全局快捷键
        self._register_hotkey()

        # 捕获启动时剪贴板中已有的内容
        self._capture_initial_clipboard()

        logger.info("Application initialized successfully")

    def _connect_signals(self) -> None:
        """连接信号"""
        # 监听新剪贴板内容
        self.monitor.new_content.connect(self._on_new_content)

        # 全局快捷键触发
        self.hotkey_manager.hotkey_triggered.connect(self._on_hotkey_triggered)

        # 系统托盘信号
        self.system_tray.show_window_requested.connect(self._on_tray_show_window)
        self.system_tray.exit_requested.connect(self._on_tray_exit)
        self.system_tray.settings_requested.connect(self._on_tray_settings)
        self.system_tray.clear_history_requested.connect(self._on_tray_clear_history)
        self.system_tray.theme_changed_requested.connect(self._on_theme_changed)

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

    def _on_hotkey_triggered(self) -> None:
        """全局快捷键触发处理"""
        if self.main_window.isVisible():
            logger.debug("Hiding window (hotkey triggered)")
            self.main_window._hide_with_animation()
        else:
            logger.debug("Showing window (hotkey triggered)")
            self.main_window.show_at_cursor()
            self.main_window.search_bar.set_focus()

    def _on_tray_show_window(self) -> None:
        """托盘显示窗口处理"""
        logger.debug("Show window requested from tray")
        if self.main_window.isVisible():
            self.main_window._hide_with_animation()
        else:
            self.main_window.show_at_cursor()
            self.main_window.search_bar.search_input.setFocus()

    def _on_tray_exit(self) -> None:
        """托盘退出处理"""
        logger.info("Exit requested from tray")
        self.app.quit()

    def _on_tray_settings(self) -> None:
        """托盘设置处理"""
        logger.debug("Settings requested from tray")
        from ui.classic.settings_dialog_classic import SettingsDialog

        dialog = SettingsDialog(self.main_window)
        dialog.settings_changed.connect(self._on_settings_changed)
        dialog.clear_history_requested.connect(self._on_clear_history_from_settings)

        if dialog.exec():
            logger.info("Settings dialog accepted")

    def _on_settings_changed(self) -> None:
        """设置更改处理"""
        logger.info("Settings changed, updating...")
        

        # 应用主题
        self.main_window.apply_theme()
        # 重新注册快捷键
        new_hotkey = settings.get('global_hotkey', 'ctrl+shift+v')
        logger.info(f"Re-registering hotkey: {new_hotkey}")
        self.hotkey_manager.unregister()
        if not self.hotkey_manager.register(new_hotkey):
            logger.error(f"Failed to register new hotkey: {new_hotkey}")
            self.system_tray.show_message("快捷键错误", f"无法注册快捷键 {new_hotkey}", 1000)
        else:
            self.system_tray.show_message("设置已保存", "快捷键已更新", 1000)

    def _on_theme_changed(self, theme_id: str) -> None:
        """主题切换处理"""
        logger.info(f"Theme changed from tray: {theme_id}")
        self.main_window.apply_theme()
        self.system_tray.show_message("主题已切换", f"已切换到 {theme_id} 主题", 1000)
        
        # 如果设置对话框正在显示，也更新它的主题
        for widget in self.app.topLevelWidgets():
            if isinstance(widget, QDialog) and widget.isVisible():
                if hasattr(widget, '_apply_theme'):
                    widget._apply_theme()
                    widget.update()
                    widget.repaint()

    def _on_clear_history_from_settings(self) -> None:
        """从设置对话框清除历史记录"""
        logger.info("Clear history from settings dialog")
        self.storage.clear_all()
        self.main_window._load_history()
        self.system_tray.show_message("清除完成", "所有剪贴板历史记录已清除", 1000)

    def _on_tray_clear_history(self) -> None:
        """托盘清空历史处理"""
        logger.debug("Clear history requested from tray")
        self.storage.clear_all()
        self.main_window._load_history()
        self.system_tray.show_message("清空完成", "所有剪贴板历史记录已清空", 1000)

    def _register_hotkey(self) -> None:
        """注册全局快捷键"""
        hotkey = settings.get('global_hotkey', 'ctrl+shift+v')
        logger.info(f"Registering global hotkey: {hotkey}")
        if not self.hotkey_manager.register(hotkey):
            logger.error("Failed to register global hotkey")

    def _capture_initial_clipboard(self) -> None:
        """捕获启动时剪贴板中已有的内容"""
        try:
            item = self.monitor.get_current_content()
            if item:
                item_id = self.storage.add(item)
                if item_id:
                    logger.info(f"Captured initial clipboard content: type={item.content_type.value}")
                    self.main_window._load_history()
                else:
                    logger.debug("Initial clipboard content already exists in history")
        except Exception as e:
            logger.error(f"Error capturing initial clipboard: {e}", exc_info=True)

    def run(self) -> int:
        """运行应用"""
        # 如果不是启动时最小化
        if not settings.get('startup_minimized', False):
            # 不自动显示，等待快捷键
            pass

        # 设置应用退出处理
        self.app.aboutToQuit.connect(self._on_exit)

        logger.info("Starting application event loop...")
        return self.app.exec()

    def _on_exit(self) -> None:
        """应用退出处理"""
        logger.info("Application shutting down...")
        # 注销快捷键
        self.hotkey_manager.unregister()
        # 隐藏系统托盘
        self.system_tray.hide()
        logger.info("Goodbye!")


def main():
    """主函数"""
    app = SmartPasteApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
