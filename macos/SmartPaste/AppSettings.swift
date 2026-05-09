import AppKit
import Combine
import CoreFoundation
import Foundation
import SwiftUI

/// `LSUIElement` 下 `NSApp.effectiveAppearance` 常误报为浅色；沙盒内 `UserDefaults.standard` 也可能读不到全局「外观」。
/// 顺序：`CFPreferences`（全局）→ 多种 `UserDefaults` 域 → `effectiveAppearance` 名称 / `bestMatch`。
enum SmartPasteSystemAppearance {
    private static let darkInterfaceNames: Set<NSAppearance.Name> = [
        .darkAqua,
        .vibrantDark,
        .accessibilityHighContrastDarkAqua,
    ]

    private static let globalDomainName = "Apple Global Domain"

    static func userPrefersDarkInterface() -> Bool {
        if let explicit = readAppleInterfaceStyleExplicit() {
            return explicit
        }
        if let inferred = inferFromEffectiveAppearanceName() {
            return inferred
        }
        return inferFromBestMatch()
    }

    /// `Dark` / `Light`；`nil` 表示未配置（如「自动」或未写入），交给后续启发式。
    private static func readAppleInterfaceStyleExplicit() -> Bool? {
        for value in cfPreferencesAppleInterfaceStyleValues() {
            if let b = interpretAppleInterfaceStyle(value) {
                return b
            }
        }
        if let s = UserDefaults.standard.string(forKey: "AppleInterfaceStyle") {
            return interpretAppleInterfaceStyle(s)
        }
        if let g = UserDefaults.standard.persistentDomain(forName: UserDefaults.globalDomain),
           let any = g["AppleInterfaceStyle"] {
            return interpretAppleInterfaceStyle(any)
        }
        if let s = UserDefaults(suiteName: globalDomainName)?.string(forKey: "AppleInterfaceStyle") {
            return interpretAppleInterfaceStyle(s)
        }
        return nil
    }

    private static func cfPreferencesAppleInterfaceStyleValues() -> [Any] {
        var out: [Any] = []
        let key = "AppleInterfaceStyle" as CFString
        if let v = CFPreferencesCopyAppValue(key, kCFPreferencesAnyApplication) {
            out.append(v)
        }
        if let v = CFPreferencesCopyValue(
            key,
            kCFPreferencesAnyApplication,
            kCFPreferencesCurrentUser,
            kCFPreferencesAnyHost
        ) {
            out.append(v)
        }
        return out
    }

    private static func interpretAppleInterfaceStyle(_ any: Any) -> Bool? {
        if let s = any as? String, !s.isEmpty {
            if s.caseInsensitiveCompare("Dark") == .orderedSame { return true }
            if s.caseInsensitiveCompare("Light") == .orderedSame { return false }
        }
        if let n = any as? NSNumber {
            if n.intValue == 1 { return true }
            if n.intValue == 0 { return false }
        }
        if let b = any as? Bool { return b }
        return nil
    }

    /// 仅在名称明显为深色时返回 `true`；`Aqua` 等不当作「用户浅色」（LSUIElement 常误报 Aqua）。
    private static func inferFromEffectiveAppearanceName() -> Bool? {
        let raw = NSApp.effectiveAppearance.name.rawValue
        let lower = raw.lowercased()
        if lower.contains("dark") || lower.contains("black") {
            return true
        }
        return nil
    }

    private static func inferFromBestMatch() -> Bool {
        let candidates: [NSAppearance.Name] = [
            .darkAqua, .vibrantDark, .accessibilityHighContrastDarkAqua, .aqua,
        ]
        guard let best = NSApp.effectiveAppearance.bestMatch(from: candidates) else {
            return false
        }
        return darkInterfaceNames.contains(best)
    }
}

enum ColorSchemePreference: String, CaseIterable, Identifiable {
    case system
    case light
    case dark

    var id: String { rawValue }

    var displayName: String {
        switch self {
        case .system: return "跟随系统"
        case .light: return "浅色"
        case .dark: return "深色"
        }
    }

    var colorScheme: ColorScheme? {
        switch self {
        case .system: return nil
        case .light: return .light
        case .dark: return .dark
        }
    }

    /// 映射为明确的 `ColorScheme`；「跟随系统」用 `SmartPasteSystemAppearance`（见文件顶部说明）。
    func resolvedSwiftUIColorScheme() -> ColorScheme {
        switch self {
        case .light: return .light
        case .dark: return .dark
        case .system:
            return SmartPasteSystemAppearance.userPrefersDarkInterface() ? .dark : .light
        }
    }
}

/// 用 `environment(\.colorScheme, …)` 注入明确浅/深，并监听系统外观变化以刷新（菜单栏 `.window` 面板尤其依赖）。
private struct SmartPasteColorSchemeModifier: ViewModifier {
    @ObservedObject var appSettings: AppSettings
    @State private var displayTick = 0

    private static let appleInterfaceThemeChanged = Notification.Name("AppleInterfaceThemeChangedNotification")
    private static let effectiveAppearanceChanged = Notification.Name("NSApplicationDidChangeEffectiveAppearanceNotification")

    func body(content: Content) -> some View {
        content
            .environment(\.colorScheme, appSettings.colorSchemePreference.resolvedSwiftUIColorScheme())
            .id("SmartPasteColorScheme-\(appSettings.colorSchemePreference.rawValue)-\(displayTick)")
            .onReceive(NotificationCenter.default.publisher(for: Self.effectiveAppearanceChanged)) { _ in
                guard appSettings.colorSchemePreference == .system else { return }
                displayTick &+= 1
            }
            .onReceive(DistributedNotificationCenter.default().publisher(for: Self.appleInterfaceThemeChanged)) { _ in
                guard appSettings.colorSchemePreference == .system else { return }
                displayTick &+= 1
            }
            .onChange(of: appSettings.colorSchemePreference) { _, _ in
                displayTick &+= 1
            }
            .onAppear {
                if appSettings.colorSchemePreference == .system {
                    displayTick &+= 1
                }
            }
    }
}

extension View {
    func smartPasteColorScheme(_ appSettings: AppSettings) -> some View {
        modifier(SmartPasteColorSchemeModifier(appSettings: appSettings))
    }
}

/// Central app preferences backed by `UserDefaults`.
/// `maxHistoryItems == nil` means unlimited; otherwise cap at this positive count.
@MainActor
final class AppSettings: ObservableObject {
    private let defaults = UserDefaults.standard

    private enum Keys {
        static let maxHistoryItems = "maxHistoryItems" // absent or -1 => unlimited; else positive Int
        static let colorSchemePreference = "colorSchemePreference"
        static let skipAdjacentDuplicates = "skipAdjacentDuplicates"
    }

    @Published var maxHistoryItems: Int? {
        didSet { persistMaxHistory() }
    }

    @Published var colorSchemePreference: ColorSchemePreference {
        didSet { defaults.set(colorSchemePreference.rawValue, forKey: Keys.colorSchemePreference) }
    }

    @Published var skipAdjacentDuplicates: Bool {
        didSet { defaults.set(skipAdjacentDuplicates, forKey: Keys.skipAdjacentDuplicates) }
    }

    init() {
        if let stored = defaults.object(forKey: Keys.maxHistoryItems) as? Int {
            if stored < 0 {
                maxHistoryItems = nil
            } else {
                maxHistoryItems = max(1, stored)
            }
        } else {
            maxHistoryItems = 100
        }

        if let raw = defaults.string(forKey: Keys.colorSchemePreference),
           let parsed = ColorSchemePreference(rawValue: raw) {
            colorSchemePreference = parsed
        } else {
            colorSchemePreference = .system
        }

        if defaults.object(forKey: Keys.skipAdjacentDuplicates) != nil {
            skipAdjacentDuplicates = defaults.bool(forKey: Keys.skipAdjacentDuplicates)
        } else {
            skipAdjacentDuplicates = true
        }
    }

    private func persistMaxHistory() {
        if let maxHistoryItems {
            defaults.set(maxHistoryItems, forKey: Keys.maxHistoryItems)
        } else {
            defaults.set(-1, forKey: Keys.maxHistoryItems)
        }
    }

    func resolvedMaxCount() -> Int? {
        maxHistoryItems
    }
}
