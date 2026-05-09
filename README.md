# Smart Paste

**Smart Paste** 是一个开源的剪贴板历史管理项目：在菜单栏或系统托盘中记录最近复制的内容，便于快速再次复制或检索。

本仓库包含 **两个独立实现**，可按平台分别构建与分发：

| 目录 | 平台 | 技术栈 | 说明 |
|------|------|--------|------|
| [`macos/`](macos/) | macOS 15+ | Swift / SwiftUI | 菜单栏应用，**纯文本**历史，本地 JSON，App Sandbox，无账号与云端 |
| [`windows/`](windows/) | Windows 10/11 | Python 3.10+ / PyQt6 | 桌面客户端，支持文本、图片、文件、HTML 等，多主题与 Fluent 界面 |

两个实现的详细功能、系统要求与构建步骤见各自目录下的 README。

---

## 快速开始

### macOS

在 [`macos/README.md`](macos/README.md) 中查看 Xcode 运行、`xcodebuild` 与 DMG 脚本说明。

```bash
cd macos
open SmartPaste.xcodeproj
```

### Windows

在 [`windows/README.md`](windows/README.md) 中查看依赖安装与运行方式。

```bash
cd windows
# 按 windows/README.md 使用 uv 或 pip 安装依赖后运行
```

---

## 参与贡献

欢迎通过 Issue 讨论缺陷与需求，通过 Pull Request 提交改进。

- 修改前建议在 Issue 中简要说明方向，避免与维护者计划冲突。
- 提交信息请写清楚动机与影响范围；UI 或行为变更可附截图或录屏。
- 请遵守各子目录现有代码风格与最小改动原则。

---

## 隐私与安全

剪贴板可能包含敏感信息。各实现的数据存储位置与沙盒／权限说明见对应 README；请勿在不可信环境长期存放机密内容。

---

## 许可证

本项目以 [**MIT License**](LICENSE)（SPDX：`MIT`）发布。完整条款见仓库根目录的 `LICENSE` 文件。
