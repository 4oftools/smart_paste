import SwiftUI

@main
struct SmartPasteApp: App {
    @StateObject private var appSettings: AppSettings
    @StateObject private var historyStore: HistoryStore

    init() {
        let settings = AppSettings()
        let history = HistoryStore(settings: settings)
        _appSettings = StateObject(wrappedValue: settings)
        _historyStore = StateObject(wrappedValue: history)
    }

    var body: some Scene {
        MenuBarExtra("Smart Paste", systemImage: "doc.on.clipboard") {
            PopoverContentView()
                .environmentObject(historyStore)
                .environmentObject(appSettings)
        }
        .menuBarExtraStyle(.window)

        // `Window`（非 `WindowGroup`）保证每个 id 仅一个实例；重复 `openWindow` 会前置已存在窗口。
        Window("全部记录", id: "main") {
            MainHistoryView()
                .environmentObject(historyStore)
                .environmentObject(appSettings)
        }
        .defaultLaunchBehavior(.suppressed)

        Window("设置", id: "settings") {
            SettingsView(appSettings: appSettings, historyStore: historyStore)
        }
        .defaultSize(width: SettingsWindowLayout.width, height: SettingsWindowLayout.defaultHeight)
        .defaultLaunchBehavior(.suppressed)
    }
}
