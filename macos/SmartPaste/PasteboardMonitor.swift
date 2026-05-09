import AppKit
import Foundation

@MainActor
final class PasteboardMonitor {
    weak var history: HistoryStore?

    private var timer: Timer?
    private var lastChangeCount: Int

    init() {
        self.lastChangeCount = NSPasteboard.general.changeCount
    }

    func start() {
        stop()
        let t = Timer.scheduledTimer(withTimeInterval: 0.35, repeats: true) { [weak self] _ in
            Task { @MainActor in
                self?.poll()
            }
        }
        RunLoop.main.add(t, forMode: .common)
        timer = t
    }

    func stop() {
        timer?.invalidate()
        timer = nil
    }

    private func poll() {
        guard let history else { return }
        let pb = NSPasteboard.general
        let current = pb.changeCount
        guard current != lastChangeCount else { return }
        lastChangeCount = current

        guard let text = pb.string(forType: .string) else { return }
        history.recordPlainText(text)
    }
}
