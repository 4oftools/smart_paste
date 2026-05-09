# Smart Paste

macOS 菜单栏剪贴板 **纯文本** 历史工具：常驻右上角图标，本地保存历史，无账号、无云端同步。适合作为 Maccy 等同类工具的轻量替代或自用版本。

---

## 功能概览

| 区域 | 能力 |
|------|------|
| **菜单栏面板** | 展示最近 **10** 条；单击行复制到剪贴板；**向左拖** 露出删除，删除前在 **面板内遮罩确认**（避免系统 alert 在菜单栏窗口无法点击）；主题；主窗口、设置、退出 |
| **主窗口** | 全部记录、**搜索**；**单击** 选中当前行（高亮），**⌘ 单击** 多选/取消；**同一行短时间再点一次** 视为双击进入详情；右键「打开详情」；批量删除与清空 |
| **设置** | 保留条数 **1～50000** 或 **不限制**；**忽略连续重复**；展示 **历史文件绝对路径**；「在 Finder 中显示」 |
| **数据** | JSON 明文保存在本机 `~/Library/Application Support/SmartPaste/history.json`；仅 **App Sandbox** |

---

## 系统要求

- **macOS 15** 或更高（使用 `MenuBarExtra` 的 `.window` 样式、`defaultLaunchBehavior(.suppressed)`、`Window(id:)` 单例窗口等 API）
- **Xcode 16** 或更高（用于开发与 Archive）

若需支持更低系统版本，需评估替换上述 API 并做完整回归测试。

---

## 打包成 DMG（官网分发）

在 Xcode 选好 **Signing Team** 并能 **Archive** 成功后，在仓库根目录执行：

```bash
chmod +x Scripts/make_dmg.sh
./Scripts/make_dmg.sh
```

得到 `build/SmartPaste.dmg`。签名、公证与 Mac App Store 区别见 **[Docs/Distribution_DMG.md](Docs/Distribution_DMG.md)**。

---

## 快速开始

### 命令行构建（Debug）

```bash
cd smart_paste
xcodebuild -scheme SmartPaste -configuration Debug -destination 'platform=macOS' -derivedDataPath ./build/DerivedData build
open ./build/DerivedData/Build/Products/Debug/SmartPaste.app
```

### Xcode

1. 打开根目录下的 **`SmartPaste.xcodeproj`**
2. Scheme 选择 **SmartPaste**，目标为 **My Mac**
3. **Run**（⌘R）运行；**Product → Archive** 可打包用于分发或上传 App Store Connect

### Release 构建

将上文命令中的 `Debug` 改为 `Release`，产物路径中的目录名同为 `Release`。

---

## 工程结构（摘要）

```
smart_paste/
├── SmartPaste.xcodeproj/
├── Docs/
│   └── AppStore_Submission.md    # Mac App Store 上架清单与审核备注模板
├── Scripts/
│   └── GenerateAppIcon.swift      # 生成占位 App 图标（可重复执行）
├── SmartPaste/
│   ├── SmartPasteApp.swift        # 入口：MenuBarExtra、WindowGroup、Settings
│   ├── AppSettings.swift          # UserDefaults：条数、主题、去重
│   ├── ClipboardItem.swift
│   ├── HistoryStore.swift         # 历史 + JSON 持久化 + 监听挂载
│   ├── PasteboardMonitor.swift    # changeCount 轮询
│   ├── WindowAppearanceBridge.swift
│   ├── PrivacyInfo.xcprivacy      # 隐私清单（UserDefaults / C617.1）
│   ├── SmartPaste.entitlements    # App Sandbox
│   ├── Assets.xcassets/
│   └── Views/
│       ├── PopoverContentView.swift
│       ├── MainHistoryView.swift
│       └── SettingsView.swift
└── README.md
```

---

## 行为与隐私说明

- **保留条数**：设置中可调；改为更小上限时会 **立即裁掉** 超出部分。
- **忽略连续重复**：开启后，若新剪贴内容与列表 **最新一条** 文本相同，则不再新增一条。
- **仅菜单栏**：`LSUIElement` 启用，**Dock 无图标**；仅菜单栏显示 SF Symbol 图标。
- **主题**：`environment(\.colorScheme, …)` 由 `NSApp.effectiveAppearance` 解析「跟随系统」；并监听系统外观通知刷新；`NSWindow.appearance` 作 AppKit 侧补充（菜单栏 `.window` 面板对 `preferredColorScheme(nil)` 常无效）。
- **剪贴板内容**：仅 **纯文本**；历史以 **明文 JSON** 落盘，请勿在不可信设备上存放敏感剪贴内容。

隐私清单与出口合规等上架技术项见 **[Docs/AppStore_Submission.md](Docs/AppStore_Submission.md)**。

---

## Mac App Store 上架

Connect 元数据、隐私问卷、截图规格、审核备注英文模板等，见 **[Docs/AppStore_Submission.md](Docs/AppStore_Submission.md)**。

工程已包含：`PrivacyInfo.xcprivacy`、`ITSAppUsesNonExemptEncryption = NO`、占位 **App Icon**（正式发版前请在 `Assets.xcassets/AppIcon` 中替换为正式设计，必要时重新执行 `Scripts/GenerateAppIcon.swift` 仅作本地占位）。

---

## 代码签名与 Bundle ID

- 默认 **自动签名**，`DEVELOPMENT_TEAM` 为空；本地调试可在 Xcode **Signing & Capabilities** 中选择个人或公司 **Team**。
- **Bundle ID** 当前为 `com.smartpaste.SmartPaste`；上架或企业分发前请改为你的域名前缀，并在 Developer / App Store Connect 中 **保持一致**。

---

## 常见问题

- **菜单栏找不到图标**：检查是否被系统菜单栏「隐藏」区域收纳；可按住 **⌘** 拖动图标调整位置。
- **主题切换无效**：请确认已用最新逻辑（`smartPasteColorScheme` + `WindowAppearanceBridge`）；若仍异常，记录系统版本与复现步骤。
- **沙盒与路径**：历史文件在沙盒容器下的 Application Support；设置页可复制路径或 **在 Finder 中显示**。

---

## 相关文档

| 文档 | 说明 |
|------|------|
| [Docs/AppStore_Submission.md](Docs/AppStore_Submission.md) | App Store Connect 填写项、隐私、截图、审核备注、自检列表 |
| [Docs/Distribution_DMG.md](Docs/Distribution_DMG.md) | 打 DMG、`hdiutil`、Developer ID 与公证说明 |

---

## 许可

未随仓库附带许可证文件；若开源或分发，请自行添加 `LICENSE` 并更新本段说明。
