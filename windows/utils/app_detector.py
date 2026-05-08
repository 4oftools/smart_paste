"""
应用检测模块
用于获取剪贴板内容来源的应用信息
"""

import ctypes
from typing import Optional, Tuple

try:
    import win32gui
    import win32process
except ImportError:
    win32gui = None
    win32process = None


class AppDetector:
    """应用检测类"""

    # 应用名称映射（可自定义）
    APP_NAMES = {
        'chrome.exe': 'Chrome',
        'firefox.exe': 'Firefox',
        'edge.exe': 'Edge',
        'msedge.exe': 'Edge',
        'notepad++.exe': 'Notepad++',
        'notepad.exe': '记事本',
        'code.exe': 'VS Code',
        'explorer.exe': '资源管理器',
        'cmd.exe': '命令提示符',
        'powershell.exe': 'PowerShell',
        'windowsterminal.exe': '终端',
        'wechat.exe': '微信',
        'qq.exe': 'QQ',
        'word.exe': 'Word',
        'excel.exe': 'Excel',
        'powerpnt.exe': 'PowerPoint',
        'winword.exe': 'Word',
        'excel.exe': 'Excel',
    }

    @staticmethod
    def get_active_window_info() -> Tuple[Optional[str], Optional[str]]:
        """
        获取当前活动窗口的信息

        Returns:
            (应用名称, 窗口标题)
        """
        if win32gui is None:
            return None, None

        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return None, None

            # 获取窗口标题
            window_title = win32gui.GetWindowText(hwnd) or ""

            # 获取进程信息
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                handle = ctypes.windll.kernel32.OpenProcess(0x0410, False, pid)

                if handle:
                    name_buf = ctypes.create_unicode_buffer(1024)
                    ctypes.windll.psapi.GetModuleBaseNameW(handle, 0, name_buf, 1024)
                    app_name = name_buf.value
                    ctypes.windll.kernel32.CloseHandle(handle)

                    # 映射应用名称
                    app_name = AppDetector._map_app_name(app_name)
                else:
                    app_name = "Unknown"
            except Exception:
                app_name = "Unknown"

            return app_name, window_title

        except Exception:
            return None, None

    @staticmethod
    def _map_app_name(exe_name: str) -> str:
        """
        映射可执行文件名到友好的应用名称

        Args:
            exe_name: 可执行文件名

        Returns:
            友好的应用名称
        """
        exe_name_lower = exe_name.lower()
        return AppDetector.APP_NAMES.get(exe_name_lower, exe_name)

    @staticmethod
    def add_app_mapping(exe_name: str, friendly_name: str) -> None:
        """
        添加应用名称映射

        Args:
            exe_name: 可执行文件名
            friendly_name: 友好的应用名称
        """
        AppDetector.APP_NAMES[exe_name.lower()] = friendly_name

    @staticmethod
    def get_app_icon(exe_name: str, size: int = 32) -> Optional[bytes]:
        """
        获取应用图标（可选功能）

        Args:
            exe_name: 可执行文件名
            size: 图标尺寸

        Returns:
            图标的字节数据
        """
        # TODO: 实现应用图标提取功能
        # 这需要使用 shell32.SHGetFileInfo 等Windows API
        return None

    @staticmethod
    def get_window_class(hwnd: int) -> Optional[str]:
        """
        获取窗口类名（用于特殊检测）

        Args:
            hwnd: 窗口句柄

        Returns:
            窗口类名
        """
        if win32gui is None:
            return None

        try:
            return win32gui.GetClassName(hwnd)
        except Exception:
            return None

    @staticmethod
    def is_browser_window(hwnd: int) -> bool:
        """
        判断是否是浏览器窗口

        Args:
            hwnd: 窗口句柄

        Returns:
            是否是浏览器窗口
        """
        class_name = AppDetector.get_window_class(hwnd)
        if class_name:
            browser_classes = ['Chrome_WidgetWin_1', 'MozillaWindowClass', 'EdgeUi']
            return any(cls in class_name for cls in browser_classes)
        return False
