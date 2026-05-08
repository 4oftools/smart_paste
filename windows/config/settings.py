"""
配置管理模块
管理应用程序的所有设置和配置
"""

import json
import os
import threading
from pathlib import Path
from typing import Any, Dict


class Settings:
    """单例配置管理类（线程安全）"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # 双重检查锁定
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        with Settings._lock:
            if hasattr(self, '_initialized'):
                return
            self._initialized = True

            # 应用目录
            self.app_dir = Path.home() / '.smart_paste'
            self.app_dir.mkdir(exist_ok=True)

            # 缓存目录
            self.cache_dir = self.app_dir / 'cache'
            self.cache_dir.mkdir(exist_ok=True)

            # 图片缓存目录
            self.image_cache_dir = self.cache_dir / 'images'
            self.image_cache_dir.mkdir(exist_ok=True)

            # 数据库路径
            self.db_path = self.app_dir / 'clipboard.db'

            # 配置文件路径
            self.config_file = self.app_dir / 'config.json'

            # 默认配置
            self._default_config = {
                'max_history_items': 100,           # 最大历史记录数
                'global_hotkey': 'ctrl+shift+v',    # 全局快捷键
                'auto_hide': True,                  # 失去焦点自动隐藏
                'show_on_copy': False,              # 复制时自动显示（不建议启用）
                'startup_minimized': False,         # 启动时最小化到托盘
                'theme': 'dark',                   # 主题：dark/light
                'window_width': 900,               # 窗口宽度
                'window_height': 600,              # 窗口高度
                'preview_panel_width': 400,        # 预览面板宽度
                'thumbnail_size': 200,             # 缩略图尺寸
                'text_preview_lines': 3,           # 文本预览行数
                'search_debounce_ms': 300,          # 搜索防抖延迟（毫秒）
                # 支持的复制数据类型
                'enable_text': True,               # 启用文本复制
                'enable_image': True,              # 启用图片复制
                'enable_file': True,               # 启用文件复制
                'enable_html': True,               # 启用HTML复制
            }

            # 加载配置
            self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """从文件加载配置"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置（处理新添加的配置项）
                    merged = self._default_config.copy()
                    merged.update(config)
                    return merged
            except Exception:
                pass
        return self._default_config.copy()

    def _save_config(self) -> None:
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        if key in self._default_config or key in self._config:
            self._config[key] = value
            self._save_config()

    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self._config.copy()

    def reset(self) -> None:
        """重置为默认配置"""
        self._config = self._default_config.copy()
        self._save_config()


# 全局配置实例
settings = Settings()
