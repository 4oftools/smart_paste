# Mac App Store 上架准备清单（Smart Paste）

本文档汇总 **App Store Connect** 需填写/准备的内容，以及工程内已做的技术项。正式提审前请将占位信息（公司名、域名、Bundle ID）替换为你的正式资料。

---

## 一、工程内已配置项（Xcode / 仓库）

| 项目 | 说明 |
|------|------|
| **Bundle ID** | `com.smartpaste.SmartPaste` — 须在 [Apple Developer](https://developer.apple.com/account) 中注册同名 **App ID**，与 App Store Connect 一致。可按公司域名改为 `com.你的公司.SmartPaste`。 |
| **版本号** | `MARKETING_VERSION` = 对外版本（如 1.0）；`CURRENT_PROJECT_VERSION` = Build 号（每次上传递增）。在 Xcode Target → **General** 中维护。 |
| **最低系统** | macOS **15.0**（`MACOSX_DEPLOYMENT_TARGET`）。若需覆盖更多用户，可降低并回归测试 `MenuBarExtra`、`defaultLaunchBehavior` 等 API。 |
| **类别** | `public.app-category.productivity`（效率）。 |
| **显示名** | `Smart Paste`（`CFBundleDisplayName`）。 |
| **版权** | `NSHumanReadableCopyright` = `Copyright © 2026 Smart Paste. All rights reserved.` — **请改为你的法人或开发者名称**。 |
| **仅菜单栏** | `LSUIElement` = YES（无 Dock 图标）。审核时可在「审核备注」说明为菜单栏工具类应用。 |
| **出口合规** | `ITSAppUsesNonExemptEncryption` = **NO**（未使用需申报的非豁免加密）。在 App Store Connect 提交二进制后，出口合规问卷一般选 **否** / 使用标准 HTTPS 不适用（本应用无网络传输剪贴内容）。 |
| **App Sandbox** | 已启用（`SmartPaste.entitlements`），符合 Mac App Store 要求。 |
| **隐私清单** | `SmartPaste/PrivacyInfo.xcprivacy`：声明访问 **UserDefaults**（原因 **C617.1**，应用内用户偏好：主题、条数上限等）。若后续增加「需申报原因」的 API（如文件时间戳、磁盘空间等），须在此文件补充。 |
| **App 图标** | `Assets.xcassets/AppIcon`：当前为 **占位图**（脚本 `Scripts/GenerateAppIcon.swift` 生成）。上架前请替换为正式设计，并满足 [Human Interface Guidelines / App icons](https://developer.apple.com/design/human-interface-guidelines/app-icons) 与 Xcode 校验。 |

---

## 二、Apple Developer 与签名

1. **Apple Developer Program** 付费账号。
2. Xcode → Target **Signing & Capabilities**：选择 **Team**，勾选 **Automatically manage signing**；**App Store Connect** 创建 App 后，分发证书由 Xcode 管理即可。
3. **App ID**（Capabilities）：与 Bundle ID 一致；当前仅 **App Sandbox**，无 iCloud/Push 等额外能力则不必勾选。

---

## 三、App Store Connect（网页端）需准备资料

### 3.1 新建 App

- **平台**：macOS。
- **名称**：在 App Store 展示的名称（可与 `CFBundleDisplayName` 一致或略长，受字数限制）。
- **主要语言**：如简体中文。
- **Bundle ID**：下拉选择与 Xcode 完全一致的一项。
- **SKU**：内部唯一字符串（如 `smartpaste-macos-001`），用户不可见。

### 3.2 本地化元数据（建议中 + 英各一套）

| 字段 | 建议内容要点 |
|------|----------------|
| **副标题** | 一句话卖点，例如：「菜单栏剪贴板历史，本地保存」。 |
| **描述** | 功能列表：菜单栏入口、最近记录、主窗口搜索与批量删除、设置（条数上限、忽略重复）、主题、数据仅存本机路径等。**勿写**「上传云端」若实际无此功能。 |
| **关键词** | 英文逗号分隔，如 `clipboard,history,paste,productivity,剪贴板`（勿重复应用名称）。 |
| **推广文本** | 可选，可随时改、无需发新版。 |
| **「新功能」** | 每个版本更新说明（与 `MARKETING_VERSION` 对应）。 |

### 3.3 URL（至少一项为强相关）

| 字段 | 要求 |
|------|------|
| **隐私政策 URL** | **强烈建议必填**。须说明：收集何种数据（剪贴板文本历史）、用途（仅本地列表与持久化）、是否分享/出售（否）、保留期限（与用户设置及删除行为一致）、联系方式。 |
| **支持 URL** | 常见问题、联系邮箱或工单入口。 |
| **营销 URL** | 可选；可与官网首页相同。 |

若无独立网站，可使用 GitHub Pages / 极简单页托管隐私政策与支持说明。

### 3.4 App 隐私（App Privacy）

在 **App 隐私** 问卷中如实申报，与本应用行为对齐，例如：

- **剪贴板 / 用户内容**：用户主动复制产生的文本，写入 **设备本地文件**（`Application Support/SmartPaste/history.json`），**不用于跟踪**、**不出售**；是否与用户身份关联选 **否**（若未登录账号）。
- **使用数据**（如仅本地 UserDefaults）：按 Connect 选项勾选「不用于跟踪」等。

若问卷选项与实现不一致，可能导致审核被拒。

### 3.5 截图与预览

- 在 **Mac App Store** 规格下截取：菜单栏图标、弹出面板、主窗口、设置页等。
- 分辨率以 [App Store Connect 帮助](https://help.apple.com/app-store-connect/) 当前要求为准（常见为 **1280×800**、**1440×900**、**2560×1600** 等组合，以 Connect 上传界面提示为准）。
- 勿在截图中展示他人隐私、未授权商标。

### 3.6 年龄分级（问卷）

按剪贴板工具性质如实作答；一般无暴力色情内容，分级通常较低，以问卷结果为准。

### 3.7 定价与供货

- 选择 **价格档位**、**供货国家或地区**。
- 若为免费 App，选择免费即可。

### 3.8 审核信息

- **登录信息**：本应用无账号则填「无需登录」或留空（按 Connect 提示）。
- **审核备注（建议粘贴）**：

```text
Smart Paste is a menu bar utility (LSUIElement). It reads the system pasteboard on a short timer to build a local plain-text history for the user. All history is stored only on disk under ~/Library/Application Support/SmartPaste/history.json. No network APIs are used for clipboard data. App Sandbox is enabled. The user can delete items or clear history in the UI.
```

（可同时附简短中文说明，便于中文审核团队。）

---

## 四、提交流程（简版）

1. Xcode：**Product → Archive** → **Distribute App** → **App Store Connect** → Upload。
2. App Store Connect：在构建版本中选择刚上传的构建，填好元数据、隐私、截图，提交 **审核**。
3. 被拒常见原因：隐私问卷与实现不符、缺少隐私政策链接、剪贴板用途说明不清、占位图标/崩溃。按 Resolution Center 修改后重新提交。

---

## 五、上架前建议你本地再核对

- [ ] Bundle ID、Team、Provisioning 与 Connect 一致  
- [ ] 替换正式 **App Icon** 与 **Copyright** 字符串  
- [ ] 发布 **隐私政策** 页面并填入 URL  
- [ ] **App 隐私** 问卷与真实行为一致  
- [ ] 在干净 macOS 用户上测试：首次启动、权限、沙盒内读写历史、删除与清空  
- [ ] `CURRENT_PROJECT_VERSION` 每次上传 +1  

---

## 六、参考链接

- [App Store Connect](https://appstoreconnect.apple.com/)  
- [App Store 审核指南](https://developer.apple.com/app-store/review/guidelines/)  
- [隐私清单文件说明](https://developer.apple.com/documentation/bundleresources/privacy_manifest_files)  
- [User Defaults 等 Required Reason API](https://developer.apple.com/documentation/bundleresources/privacy_manifest_files/describing_use_of_required_reason_api)  

若你后续增加网络同步、账号登录或分析 SDK，必须同步更新：**隐私政策**、**App 隐私**、**PrivacyInfo.xcprivacy** 与审核备注。
