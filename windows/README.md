# Smart Paste - 智能剪贴板历史管理器

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.0+-green.svg)
![PyQt-Fluent-Widgets](https://img.shields.io/badge/PyQt--Fluent--Widgets-1.6.0+-purple.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**高效、美观、多功能的剪贴板历史管理工具**

支持 Fluent 设计风格升级！查看 [FLUENT_UPGRADE.md](FLUENT_UPGRADE.md) 了解更多。

</div>

---

## 📖 简介

Smart Paste 是一款功能强大的剪贴板历史管理工具，支持文本、图片、文件等多种内容类型的记录和管理。采用现代化的 UI 设计，提供 8 种精美主题，让您的剪贴板管理更加高效和愉悦。

## ✨ 主要功能

### 📋 剪贴板历史管理
- **自动记录**：自动捕获剪贴板内容变化
- **多种类型支持**：文本、图片、文件、HTML 富文本
- **智能去重**：相同内容不会重复记录
- **收藏功能**：重要内容可以标记为收藏
- **搜索过滤**：快速查找历史记录

### 🎨 主题系统
提供 4 种精品主题，每种都经过精心调优：
- **暗夜极光** - 深色专业主题，适合长时间编程（对比度 15.8:1 AAA 级）
- **云端漫步** - 浅色商务主题，全浅色调清新明亮（对比度 14.2:1 AAA 级）
- **复古留声机** - 暖色怀旧主题，温暖舒适适合创意工作（对比度 12.8:1 AAA 级）
- **拿铁艺术** - 柔和治愈主题，温柔治愈适合艺术设计（对比度 13.5:1 AAA 级）

详见：[THEMES_GUIDE.md](THEMES_GUIDE.md)

### 🚀 便捷操作
- **全局快捷键**：`Ctrl+Shift+V` 快速唤起
- **托盘菜单**：右键托盘图标快速访问最近记录
- **拖拽窗口**：按住顶部栏可拖动窗口位置
- **键盘导航**：↑↓选择，Enter 复制，Esc 关闭

### 🛠️ 丰富设置
- **历史记录数量**：自定义最大记录数（10-1000）
- **数据类型控制**：选择性启用文本/图片/文件/HTML
- **行为设置**：自动隐藏、复制时显示、启动最小化
- **快捷键自定义**：录制新的快捷键组合

## 📦 安装

### 环境要求
- Python 3.10+
- Windows 10/11
- PyQt6

### 安装依赖

#### 方式一：使用 UV（推荐）
```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 同步依赖
uv sync
```

#### 方式二：使用 pip
```bash
pip install -r requirements.txt
```

### 运行应用

#### 使用 UV
```bash
# Classic 版本
uv run main.py

# Fluent 版本
uv run main_fluent.py
```

#### 使用 Python
```bash
# Classic 版本
python main.py

# Fluent 版本
python main_fluent.py

# 或使用启动脚本
run.bat        # Classic
run_fluent.bat # Fluent
```

### 打包为可执行文件
```bash
# 使用 PyInstaller 打包
pyinstaller SmartPaste.spec
```

## 📸 界面预览

### 主界面
- 顶部搜索栏和设置按钮
- 类型过滤面板（全部/文本/图片/文件/收藏）
- 左侧历史记录列表
- 右侧内容预览面板

### 系统托盘
- 显示主窗口
- **最近记录**（最近 20 条，动态更新）
- 主题切换
- 清空历史
- 设置
- 退出

## 🎯 使用指南

### 基本操作
1. **复制内容**：在任何应用中复制文本、图片或文件
2. **查看历史**：按 `Ctrl+Shift+V` 或右键托盘图标
3. **搜索过滤**：在搜索框输入关键词，或点击类型按钮
4. **复制内容**：点击历史项，按 Enter 或点击复制按钮
5. **收藏内容**：点击历史项的星标按钮

### 快捷键
| 快捷键 | 功能 |
|--------|------|
| `Ctrl+Shift+V` | 唤起/隐藏主窗口 |
| `↑` / `↓` | 选择上一项/下一项 |
| `Enter` | 复制选中项 |
| `Esc` | 关闭窗口 |
| `Delete` | 删除选中项 |

### 托盘菜单
- **显示主窗口**：打开主界面
- **最近记录**：快速访问最近 20 条记录（动态更新）
- **主题**：快速切换 8 种主题
- **清空历史**：删除所有历史记录
- **设置**：打开设置对话框
- **退出**：退出应用

## 🗂️ 项目结构

```
smart_paste/
├── main.py                 # Classic 版本入口
├── main_fluent.py          # Fluent 版本入口
├── pyproject.toml          # 项目配置 (UV)
├── uv.lock                 # UV 依赖锁定
├── requirements.txt        # 依赖列表
├── config/                 # 配置模块
│   ├── settings.py         # 设置管理
│   └── database.py         # 数据库配置
├── core/                   # 核心功能
│   ├── clipboard_monitor.py # 剪贴板监听
│   ├── storage.py          # 数据存储
│   └── hotkey_manager.py   # 快捷键管理
├── models/                 # 数据模型
│   └── clipboard_item.py   # 剪贴板项模型
├── ui/                     # 用户界面
│   ├── classic/            # Classic 版本 UI
│   └── fluent/             # Fluent 版本 UI
├── utils/                  # 工具模块
│   ├── theme.py            # 主题管理
│   ├── fluent_icons.py     # Fluent 图标
│   ├── logger.py           # 日志管理
│   └── fluent_theme.py     # Fluent 主题管理
├── resources/              # 资源文件
└── ...
```

## 📚 文档

- [UV_GUIDE.md](UV_GUIDE.md) - UV 包管理使用指南
- [THEMES_GUIDE.md](THEMES_GUIDE.md) - 主题系统说明

## 🔧 配置说明

配置文件位于：`C:\Users\<用户名>\.smart_paste\config.json`

### 可配置项
```json
{
  "max_history_items": 100,
  "global_hotkey": "ctrl+shift+v",
  "auto_hide": true,
  "show_on_copy": false,
  "startup_minimized": false,
  "theme": "dark",
  "enable_text": true,
  "enable_image": true,
  "enable_file": true,
  "enable_html": true
}
```

## 📝 更新日志

### v3.0 精简版 (最新)
- 🎨 **4 大精品主题** - 合并相似主题，保留最精华配色
  - 暗夜极光（深色专业）
  - 云端漫步（浅色商务）
  - 复古留声机（暖色怀旧）
  - 拿铁艺术（柔和治愈）
- ✨ **AAA 级对比度** - 所有主题符合 WCAG AAA 无障碍标准
- 📚 **精简文档** - 新增主题选择指南 THEMES_GUIDE.md

### v2.0 Fluent Edition
- ✨ **Fluent 设计风格** - 现代化的卡片式设计
- 🎨 **Fluent 设置对话框** - 使用 SettingCard 组件
- 💬 **InfoBar 通知** - 即时操作反馈
- 🎯 **Fluent 主题系统** - 深色/浅色主题优化
- 📱 **响应式布局** - 适配不同屏幕尺寸
- 🎭 **平滑动画** - 窗口显示/隐藏动画优化
- 📚 **完善文档** - 新增 4 个指南文档

### v1.1.0
- ✨ 主题切换功能
- 🎨 Material Icons 图标
- 📋 剪贴板历史管理
- 🔍 搜索和过滤
- ⭐ 收藏功能
- 🎯 托盘快速访问
- ⌨️ 全局快捷键
- 🖼️ 图片缩略图
- 📁 文件列表
- 🎭 窗口拖拽

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，请提交 Issue。
