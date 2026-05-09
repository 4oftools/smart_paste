# 将 Smart Paste 打成 DMG

DMG 适合 **官网 / 网盘分发**（不走 Mac App Store）。若只上架 App Store，用 Xcode **Archive → Distribute App** 即可，不必做 DMG。

---

## 一键脚本（推荐）

前置：**Xcode 已安装**，工程能 **Archive 成功**（在 Xcode 里选好 **Signing Team**，与分发证书一致）。

在仓库根目录执行：

```bash
chmod +x Scripts/make_dmg.sh
./Scripts/make_dmg.sh
```

产物：

- `build/SmartPaste.xcarchive` — Xcode 归档  
- `build/SmartPaste.dmg` — 压缩磁盘映像（内含 `SmartPaste.app` 与指向 `/Applications` 的替身，方便拖拽）

自定义 DMG 文件名（不含 `.dmg` 后缀）：

```bash
DMG_NAME="SmartPaste-1.0" ./Scripts/make_dmg.sh
```

---

## 手动步骤（理解原理）

1. **Xcode**：`Product → Archive`，Organizer 里 **Distribute App** → **Copy App** 导出 `SmartPaste.app`；或命令行 `xcodebuild archive`（与脚本相同思路）。  
2. **准备文件夹**：例如 `dmg_staging/SmartPaste.app`，可选 `ln -s /Applications dmg_staging/Applications`。  
3. **生成 DMG**：

```bash
hdiutil create -volname "Smart Paste" -srcfolder dmg_staging -ov -format UDZO SmartPaste.dmg
```

`UDZO` 为压缩格式，体积较小；也可用 `ULFO` 等，以 `man hdiutil` 为准。

---

## 签名与公证（对外分发强烈建议）

- **Developer ID Application**：在 Xcode **Signing** 中选团队，Archive 后用 **Organizer → Distribute App → Direct Distribution**（或命令行 `notarytool`）做 **公证（notarize）**，否则用户会看到「无法验证开发者」类提示。  
- 公证需 Apple ID、**App 专用密码**、在 Apple Developer 开通 **Notary** 权限；具体以 [Apple 文档](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution) 为准。  
- **沙盒**：当前工程已启用 App Sandbox；直接分发的 DMG 与 MAS 包可以是同一套代码，但 **证书类型** 不同（MAS 用 **3rd Party Mac Developer Application**，网发常用 **Developer ID Application**）。

脚本 **不包含** 公证；公证一般在导出已签名的 `.app` 或 `.dmg` 后用 `xcrun notarytool` 提交。

---

## 与 Mac App Store 的区别

| 方式 | 典型用途 |
|------|-----------|
| **DMG / 官网** | 自行托管下载、更新节奏自控；需 Developer ID + 公证体验更好。 |
| **Mac App Store** | 走 Connect 审核；见 [AppStore_Submission.md](AppStore_Submission.md)。 |

---

## 常见问题

- **Archive 失败 / 无签名**：在 Xcode Target → **Signing & Capabilities** 选择 **Team**，先用 Xcode 手动 Archive 一次确认通过。  
- **脚本里 generic/platform=macOS**：用于打 **通用** 归档；若仅需本机架构，可在 Xcode 里改 `Excluded Architectures` 后再试。  
- **Gatekeeper**：未公证的 app，用户可在 **系统设置 → 隐私与安全性** 里点「仍要打开」；公证后体验更顺畅。
