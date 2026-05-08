"""
全局快捷键管理模块
注册和管理全局热键
"""

import keyboard
from typing import Optional, Callable
from PyQt6.QtCore import QObject, pyqtSignal
from utils.logger import get_logger

# 获取日志器
logger = get_logger('HotkeyManager')


class HotkeyManager(QObject):
    """全局快捷键管理器"""

    # 信号：快捷键被触发
    hotkey_triggered = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_hotkey = None
        self.callback_id = None

        logger.info("Hotkey manager initialized")

    def register(self, hotkey: str, callback: Optional[Callable] = None) -> bool:
        """
        注册全局快捷键

        Args:
            hotkey: 快捷键字符串，如 'ctrl+shift+v'
            callback: 触发时的回调函数

        Returns:
            是否注册成功
        """
        # 先移除旧的快捷键
        if self.current_hotkey:
            self.unregister()

        try:
            if callback:
                self.callback_id = keyboard.add_hotkey(hotkey, callback)
            else:
                self.callback_id = keyboard.add_hotkey(hotkey, self._on_hotkey_triggered)

            self.current_hotkey = hotkey
            logger.info(f"Global hotkey registered: {hotkey}")
            return True
        except Exception as e:
            logger.error(f"Failed to register hotkey '{hotkey}': {e}", exc_info=True)
            return False

    def unregister(self) -> bool:
        """
        注销当前快捷键

        Returns:
            是否成功
        """
        if self.callback_id is not None:
            try:
                keyboard.remove_hotkey(self.callback_id)
                logger.info(f"Global hotkey unregistered: {self.current_hotkey}")
                self.callback_id = None
                self.current_hotkey = None
                return True
            except Exception as e:
                logger.error(f"Failed to unregister hotkey: {e}", exc_info=True)
                return False
        return False

    def _on_hotkey_triggered(self) -> None:
        """快捷键触发处理"""
        logger.debug("Global hotkey triggered")
        self.hotkey_triggered.emit()

    def is_registered(self) -> bool:
        """
        检查是否有注册的快捷键

        Returns:
            是否有快捷键
        """
        return self.current_hotkey is not None

    def get_current_hotkey(self) -> Optional[str]:
        """
        获取当前快捷键

        Returns:
            当前快捷键字符串
        """
        return self.current_hotkey

    @staticmethod
    def normalize_hotkey(hotkey: str) -> str:
        """
        规范化快捷键字符串

        Args:
            hotkey: 原始快捷键字符串

        Returns:
            规范化后的快捷键
        """
        # 统一为小写
        hotkey = hotkey.lower()

        # 规范化分隔符
        hotkey = hotkey.replace(' ', '+')
        hotkey = hotkey.replace('-', '+')

        # 去除重复的+
        while '++' in hotkey:
            hotkey = hotkey.replace('++', '+')

        # 去除首尾的+
        hotkey = hotkey.strip('+')

        return hotkey

    @staticmethod
    def format_hotkey_for_display(hotkey: str) -> str:
        """
        格式化快捷键用于显示

        Args:
            hotkey: 原始快捷键字符串

        Returns:
            格式化后的快捷键
        """
        # 分割按键
        keys = hotkey.lower().split('+')

        # 映射按键名
        key_map = {
            'ctrl': 'Ctrl',
            'control': 'Ctrl',
            'shift': 'Shift',
            'alt': 'Alt',
            'win': 'Win',
            'windows': 'Win',
            'cmd': 'Win',
            'command': 'Win',
            'space': 'Space',
        }

        formatted = []
        for key in keys:
            key = key.strip()
            # 特殊处理空格
            if key == 'space':
                formatted.append('Space')
            elif key in key_map:
                formatted.append(key_map[key])
            else:
                # 首字母大写
                formatted.append(key.capitalize())

        return ' + '.join(formatted)

    @staticmethod
    def validate_hotkey(hotkey: str) -> bool:
        """
        验证快捷键是否有效

        Args:
            hotkey: 快捷键字符串

        Returns:
            是否有效
        """
        try:
            # 尝试规范化
            normalized = HotkeyManager.normalize_hotkey(hotkey)

            if not normalized:
                return False

            # 检查是否包含至少一个修饰键
            modifiers = ['ctrl', 'shift', 'alt', 'win']
            keys = normalized.split('+')

            # 必须至少有一个修饰键
            has_modifier = any(mod in keys for mod in modifiers)

            # 检查是否只有一个非修饰键
            non_modifiers = [k for k in keys if k not in modifiers]

            return has_modifier and len(non_modifiers) == 1

        except Exception:
            return False
