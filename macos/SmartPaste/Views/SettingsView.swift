import AppKit
import SwiftUI

/// 设置窗口固定宽度；与 `SettingsWindowWidthLock`、Scene 的 `defaultSize` 保持一致。
enum SettingsWindowLayout {
    static let width: CGFloat = 300
    static let defaultHeight: CGFloat = 400
}

struct SettingsView: View {
    @ObservedObject var appSettings: AppSettings
    @ObservedObject var historyStore: HistoryStore

    @State private var unlimited = false
    @State private var limitValue: Int = 100

    var body: some View {
        Form {
            Section("历史记录") {
                Toggle("不限制条数", isOn: $unlimited)
                    .onChange(of: unlimited) { _, newValue in
                        if newValue {
                            appSettings.maxHistoryItems = nil
                        } else {
                            appSettings.maxHistoryItems = max(1, limitValue)
                        }
                        historyStore.enforceRetentionFromSettings()
                    }

                if !unlimited {
                    Stepper(value: $limitValue, in: 1 ... 50_000, step: 1) {
                        Text("最多保留：\(limitValue) 条")
                    }
                    .onChange(of: limitValue) { _, newValue in
                        guard !unlimited else { return }
                        appSettings.maxHistoryItems = max(1, newValue)
                        historyStore.enforceRetentionFromSettings()
                    }
                }

                Toggle("忽略连续重复", isOn: $appSettings.skipAdjacentDuplicates)
            }

            Section("关于") {
                Text("剪贴板内容以 JSON 明文保存在本机，请勿在公共电脑上存放敏感信息。")
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }

            Section("存储位置") {
                Text(historyStore.historyPersistenceURL.path)
                    .font(.system(.footnote, design: .monospaced))
                    .foregroundStyle(.primary)
                    .textSelection(.enabled)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .lineLimit(nil)
                    .fixedSize(horizontal: false, vertical: true)

                Button("在 Finder 中显示") {
                    NSWorkspace.shared.activateFileViewerSelecting([historyStore.historyPersistenceURL])
                }
            }
        }
        .formStyle(.grouped)
        .frame(width: SettingsWindowLayout.width)
        .frame(minHeight: 360)
        .background(SettingsWindowWidthLock())
        .smartPasteColorScheme(appSettings)
        .windowAppearance(appSettings.colorSchemePreference)
        .onAppear {
            syncLocalStateFromSettings()
        }
        .onChange(of: appSettings.maxHistoryItems) { _, _ in
            syncLocalStateFromSettings()
        }
    }

    private func syncLocalStateFromSettings() {
        if let max = appSettings.maxHistoryItems {
            unlimited = false
            if limitValue != max {
                limitValue = max
            }
        } else {
            unlimited = true
        }
    }
}

// MARK: - 固定设置窗口水平尺寸，避免可横向拉伸时两侧露出窗口底色

private final class SettingsWindowWidthAnchorView: NSView {
    override func viewDidMoveToWindow() {
        super.viewDidMoveToWindow()
        DispatchQueue.main.async { [weak self] in self?.applyWidthLock() }
    }

    private func applyWidthLock() {
        guard let window else { return }
        let w = SettingsWindowLayout.width
        window.contentMinSize = NSSize(width: w, height: 260)
        window.contentMaxSize = NSSize(width: w, height: 12_000)

        let rect = window.contentLayoutRect
        let targetH = max(rect.height, 360)
        guard abs(rect.width - w) > 0.5 else { return }
        window.setContentSize(NSSize(width: w, height: targetH))
    }
}

private struct SettingsWindowWidthLock: NSViewRepresentable {
    func makeNSView(context: Context) -> SettingsWindowWidthAnchorView {
        SettingsWindowWidthAnchorView()
    }

    func updateNSView(_ nsView: SettingsWindowWidthAnchorView, context: Context) {}
}
