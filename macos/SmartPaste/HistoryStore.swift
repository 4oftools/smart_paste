import AppKit
import Combine
import Foundation

@MainActor
final class HistoryStore: ObservableObject {
    @Published private(set) var items: [ClipboardItem] = []

    private let fileURL: URL
    /// Resolved JSON path shown in Settings (same file read/write uses).
    var historyPersistenceURL: URL { fileURL }
    private let encoder = JSONEncoder()
    private let decoder = JSONDecoder()
    private let settings: AppSettings
    private let monitor: PasteboardMonitor

    init(settings: AppSettings) {
        self.settings = settings
        self.monitor = PasteboardMonitor()
        let support = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first
            ?? FileManager.default.temporaryDirectory
        let dir = support.appendingPathComponent("SmartPaste", isDirectory: true)
        try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        fileURL = dir.appendingPathComponent("history.json")
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        encoder.dateEncodingStrategy = .iso8601
        decoder.dateDecodingStrategy = .iso8601
        loadFromDisk()
        monitor.history = self
        monitor.start()
    }

    func loadFromDisk() {
        guard FileManager.default.fileExists(atPath: fileURL.path) else {
            items = []
            return
        }
        do {
            let data = try Data(contentsOf: fileURL)
            items = try decoder.decode([ClipboardItem].self, from: data)
            applyRetentionCap()
        } catch {
            items = []
        }
    }

    private func saveToDisk() {
        do {
            let data = try encoder.encode(items)
            try data.write(to: fileURL, options: [.atomic])
        } catch {
            // Intentionally quiet; avoid crashing menu bar app on disk errors.
        }
    }

    /// Append plain text from the pasteboard if it passes duplicate / retention rules.
    func recordPlainText(_ text: String) {
        let trimmed = text
        guard !trimmed.isEmpty else { return }

        if settings.skipAdjacentDuplicates, items.first?.text == trimmed {
            return
        }

        let entry = ClipboardItem(text: trimmed)
        items.insert(entry, at: 0)
        applyRetentionCap()
        saveToDisk()
    }

    func copyToPasteboard(_ item: ClipboardItem) {
        let pb = NSPasteboard.general
        pb.clearContents()
        pb.setString(item.text, forType: .string)
    }

    func delete(_ item: ClipboardItem) {
        delete(id: item.id)
    }

    func delete(id: ClipboardItem.ID) {
        items.removeAll { $0.id == id }
        saveToDisk()
    }

    func deleteAll(withIDs ids: Set<ClipboardItem.ID>) {
        guard !ids.isEmpty else { return }
        items.removeAll { ids.contains($0.id) }
        saveToDisk()
    }

    func clearAll() {
        items = []
        saveToDisk()
    }

    func applyRetentionCap() {
        guard let cap = settings.resolvedMaxCount() else {
            saveToDisk()
            return
        }
        if items.count > cap {
            items = Array(items.prefix(cap))
            saveToDisk()
        }
    }

    /// Call after settings change the max count downward.
    func enforceRetentionFromSettings() {
        guard let cap = settings.resolvedMaxCount() else { return }
        if items.count > cap {
            items = Array(items.prefix(cap))
            saveToDisk()
        }
    }
}
