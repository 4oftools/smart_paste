import AppKit
import SwiftUI

/// AppKit-backed windows (e.g. `MenuBarExtra` with `.window` style) often ignore SwiftUI-only
/// `preferredColorScheme`. Drive the hosting `NSWindow.appearance` instead.
///
/// Mutating `NSWindow.appearance` too often (including from `updateNSView` on every SwiftUI pass)
/// can still trigger layout recursion. Only schedule work when the preference **changes**, and
/// skip `window.appearance` assignment when already equal.
extension View {
    func windowAppearance(_ preference: ColorSchemePreference) -> some View {
        background(WindowAppearanceBridge(preference: preference))
    }
}

private final class WindowAppearanceAnchorView: NSView {
    var preference: ColorSchemePreference = .system {
        didSet {
            guard preference != oldValue else { return }
            scheduleApply()
        }
    }

    private var pendingApply: DispatchWorkItem?

    deinit {
        pendingApply?.cancel()
    }

    override func viewDidMoveToWindow() {
        super.viewDidMoveToWindow()
        scheduleApply()
    }

    private func scheduleApply() {
        pendingApply?.cancel()
        let work = DispatchWorkItem { [weak self] in
            self?.applyNowIfNeeded()
        }
        pendingApply = work
        DispatchQueue.main.async(execute: work)
    }

    private func applyNowIfNeeded() {
        guard let window else { return }

        switch preference {
        case .system:
            // 与 SwiftUI 一致：显式 Aqua / DarkAqua（LSUIElement 下 `nil` 常仍偏浅）。
            let next = SmartPasteSystemAppearance.userPrefersDarkInterface()
                ? NSAppearance(named: .darkAqua)
                : NSAppearance(named: .aqua)
            guard let next else { return }
            if appearancesEqual(window.appearance, next) { return }
            window.appearance = next
        case .light:
            let next = NSAppearance(named: .aqua)
            if appearancesEqual(window.appearance, next) { return }
            window.appearance = next
        case .dark:
            let next = NSAppearance(named: .darkAqua)
            if appearancesEqual(window.appearance, next) { return }
            window.appearance = next
        }
    }

    private func appearancesEqual(_ a: NSAppearance?, _ b: NSAppearance?) -> Bool {
        switch (a, b) {
        case (nil, nil):
            return true
        case let (x?, y?):
            return x.name == y.name
        default:
            return false
        }
    }
}

private struct WindowAppearanceBridge: NSViewRepresentable {
    var preference: ColorSchemePreference

    func makeNSView(context: Context) -> WindowAppearanceAnchorView {
        let view = WindowAppearanceAnchorView()
        view.preference = preference
        return view
    }

    func updateNSView(_ nsView: WindowAppearanceAnchorView, context: Context) {
        if nsView.preference != preference {
            nsView.preference = preference
        }
    }
}
