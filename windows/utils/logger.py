"""
日志模块
提供应用程序的日志记录功能
支持日志拆分和保存到当前目录
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

from config import settings


class Logger:
    """日志管理类"""

    _instance = None
    _loggers = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True

        # 日志目录（使用当前目录下的 logs）
        self._setup_log_dir()
        self._setup_file_handlers()
        self._setup_root_logger()

    def _setup_log_dir(self) -> None:
        """设置日志目录"""
        # 使用应用目录下的 logs 目录，而不是当前工作目录
        from config import settings
        self.log_dir = settings.app_dir / 'logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def _setup_file_handlers(self) -> None:
        """设置文件处理器"""
        # 按日期分割日志
        today = datetime.now().strftime('%Y-%m-%d')

        # 主日志文件
        log_file = self.log_dir / f'smart_paste_{today}.log'

        # 错误日志文件（只记录错误及以上级别）
        error_log_file = self.log_dir / f'smart_paste_errors.log'

        # 创建文件处理器
        self.file_handler = logging.FileHandler(log_file, encoding='utf-8')
        self.file_handler.setLevel(logging.DEBUG)
        self.file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.file_handler.setFormatter(self.file_formatter)

        self.error_file_handler = logging.FileHandler(error_log_file, encoding='utf-8')
        self.error_file_handler.setLevel(logging.ERROR)
        self.error_file_handler.setFormatter(self.file_formatter)

    def _setup_root_logger(self) -> None:
        """配置根日志器"""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.handlers.clear()

        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

        # 文件处理器
        root_logger.addHandler(self.file_handler)
        root_logger.addHandler(self.error_file_handler)

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        获取指定名称的日志器

        Args:
            name: 日志器名称

        Returns:
            日志器对象
        """
        if name in Logger._loggers:
            return Logger._loggers[name]

        logger = logging.getLogger(name)
        Logger._loggers[name] = logger
        return logger

    @staticmethod
    def debug(message: str, name: str = __name__) -> None:
        """记录调试信息"""
        Logger.get_logger(name).debug(message)

    @staticmethod
    def info(message: str, name: str = __name__) -> None:
        """记录信息"""
        Logger.get_logger(name).info(message)

    @staticmethod
    def warning(message: str, name: str = __name__) -> None:
        """记录警告"""
        Logger.get_logger(name).warning(message)

    @staticmethod
    def error(message: str, name: str = __name__, exc_info: bool = False) -> None:
        """记录错误"""
        Logger.get_logger(name).error(message, exc_info=exc_info)

    @staticmethod
    def critical(message: str, name: str = __name__, exc_info: bool = False) -> None:
        """记录严重错误"""
        Logger.get_logger(name).critical(message, exc_info=exc_info)


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器"""

    # ANSI 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',     # 青色
        'INFO': '\033[32m',      # 绿色
        'WARNING': '\033[33m',   # 黄色
        'ERROR': '\033[31m',     # 红色
        'CRITICAL': '\033[35m',  # 紫色
    }
    RESET = '\033[0m'

    def format(self, record) -> str:
        """格式化日志记录"""
        levelname = record.levelname
        color = self.COLORS.get(levelname, '')

        # 添加颜色到级别名
        if color and hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            record.levelname = f"{color}{levelname}{self.RESET}"

        return super().format(record)


# 创建全局日志实例
_logger = Logger()


def get_logger(name: str) -> logging.Logger:
    """
    获取日志器的便捷函数

    Args:
        name: 日志器名称

    Returns:
        日志器对象
    """
    return Logger.get_logger(name)


# 便捷函数
def debug(message: str, name: str = __name__) -> None:
    """记录调试信息"""
    Logger.debug(message, name)


def info(message: str, name: str = __name__) -> None:
    """记录信息"""
    Logger.info(message, name)


def warning(message: str, name: str = __name__) -> None:
    """记录警告"""
    Logger.warning(message, name)


def error(message: str, name: str = __name__, exc_info: bool = False) -> None:
    """记录错误"""
    Logger.error(message, name, exc_info)


def critical(message: str, name: str = __name__, exc_info: bool = False) -> None:
    """记录严重错误"""
    Logger.critical(message, name, exc_info)


# 导出
__all__ = ['get_logger', 'debug', 'info', 'warning', 'error', 'critical', 'Logger']
