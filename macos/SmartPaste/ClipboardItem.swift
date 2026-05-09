import Foundation

struct ClipboardItem: Identifiable, Codable, Equatable, Hashable {
    let id: UUID
    let createdAt: Date
    let text: String

    init(id: UUID = UUID(), createdAt: Date = Date(), text: String) {
        self.id = id
        self.createdAt = createdAt
        self.text = text
    }

    /// 列表行时间：`yyyy-MM-dd HH:mm:ss`（本地时区，POSIX locale 保证格式稳定）。
    static let listDisplayDateFormatter: DateFormatter = {
        let f = DateFormatter()
        f.locale = Locale(identifier: "en_US_POSIX")
        f.dateFormat = "yyyy-MM-dd HH:mm:ss"
        return f
    }()
}
