import AppKit
import SwiftUI

struct MainHistoryView: View {
    @EnvironmentObject private var historyStore: HistoryStore
    @EnvironmentObject private var appSettings: AppSettings
    @State private var query = ""
    @State private var selection = Set<ClipboardItem.ID>()
    @State private var confirmBatchDelete = false
    @State private var detailItem: ClipboardItem?
    /// 用于识别「同一行短时间第二次点击」为双击，避免使用 `TapGesture(count:2)` 抢占 List 单击选择。
    @State private var lastClick: (id: ClipboardItem.ID, time: Date)?
    @State private var showCopyToast = false
    @State private var copyToastEpoch = 0

    private static let doubleTapMaxInterval: TimeInterval = 0.38
    private static let dateFormatter: DateFormatter = {
        let f = DateFormatter()
        f.dateStyle = .medium
        f.timeStyle = .short
        f.locale = Locale(identifier: "zh-Hans")
        return f
    }()

    private var filtered: [ClipboardItem] {
        let q = query.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !q.isEmpty else { return historyStore.items }
        return historyStore.items.filter { $0.text.localizedCaseInsensitiveContains(q) }
    }

    var body: some View {
        NavigationStack {
            // 不用 `List(selection:)` + `TapGesture(count:2)`：后者会干扰系统对单击选中的处理。
            List {
                ForEach(filtered) { item in
                    row(for: item)
                        .listRowBackground(
                            selection.contains(item.id)
                                ? Color.accentColor.opacity(0.14)
                                : Color.clear
                        )
                        .contentShape(Rectangle())
                        .onTapGesture {
                            handleRowTap(item)
                        }
                        .contextMenu {
                            Button("打开详情") {
                                detailItem = item
                            }
                            Button("复制") {
                                historyStore.copyToPasteboard(item)
                                flashCopyToast()
                            }
                            Button("删除", role: .destructive) {
                                historyStore.delete(item)
                                selection.remove(item.id)
                                if detailItem?.id == item.id {
                                    detailItem = nil
                                }
                            }
                        }
                }
                .onDelete { indexSet in
                    let targets = indexSet.map { filtered[$0] }
                    targets.forEach { historyStore.delete($0) }
                    let removed = Set(targets.map(\.id))
                    selection.subtract(removed)
                    if let d = detailItem, removed.contains(d.id) {
                        detailItem = nil
                    }
                }
            }
            .navigationTitle(selection.isEmpty ? "全部记录" : "已选 \(selection.count) 条")
            .searchable(text: $query, prompt: "搜索")
            .navigationDestination(item: $detailItem) { item in
                detailContent(for: item)
            }
            .confirmationDialog(
                "确定删除所选的 \(selection.count) 条记录？",
                isPresented: $confirmBatchDelete,
                titleVisibility: .visible
            ) {
                Button("删除", role: .destructive) {
                    let deletedIDs = selection
                    historyStore.deleteAll(withIDs: deletedIDs)
                    selection.removeAll()
                    if let d = detailItem, deletedIDs.contains(d.id) {
                        detailItem = nil
                    }
                }
                Button("取消", role: .cancel) {}
            } message: {
                Text("此操作无法撤销。")
            }
            .toolbar {
                ToolbarItemGroup(placement: .primaryAction) {
                    Button("全选当前列表") {
                        selection = Set(filtered.map(\.id))
                    }
                    .disabled(filtered.isEmpty)

                    Button("取消选择") {
                        selection.removeAll()
                    }
                    .disabled(selection.isEmpty)
                }
                ToolbarItemGroup(placement: .destructiveAction) {
                    Button("删除所选") {
                        confirmBatchDelete = true
                    }
                    .disabled(selection.isEmpty)

                    Button("清空", role: .destructive) {
                        historyStore.clearAll()
                        selection.removeAll()
                        detailItem = nil
                    }
                    .disabled(historyStore.items.isEmpty)
                }
            }
            .onChange(of: historyStore.items) { _, newItems in
                if let d = detailItem, !newItems.contains(where: { $0.id == d.id }) {
                    detailItem = nil
                }
            }
        }
        .frame(minWidth: 420, minHeight: 520)
        .copyToastOverlay(isPresented: showCopyToast)
        .smartPasteColorScheme(appSettings)
        .windowAppearance(appSettings.colorSchemePreference)
        .onChange(of: query) { _, _ in
            let visible = Set(filtered.map(\.id))
            selection = selection.intersection(visible)
        }
    }

    private func flashCopyToast() {
        copyToastEpoch += 1
        let token = copyToastEpoch
        showCopyToast = true
        Task { @MainActor in
            try? await Task.sleep(for: .milliseconds(1250))
            guard token == copyToastEpoch else { return }
            showCopyToast = false
        }
    }

    private func handleRowTap(_ item: ClipboardItem) {
        let now = Date()
        let flags = NSEvent.modifierFlags

        if flags.contains(.command) {
            lastClick = nil
            if selection.contains(item.id) {
                selection.remove(item.id)
            } else {
                selection.insert(item.id)
            }
            return
        }

        if let last = lastClick,
           last.id == item.id,
           now.timeIntervalSince(last.time) < Self.doubleTapMaxInterval {
            lastClick = nil
            detailItem = item
            return
        }

        lastClick = (item.id, now)
        selection = [item.id]
    }

    private func row(for item: ClipboardItem) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(item.text)
                .lineLimit(1)
                .truncationMode(.tail)
            Text(Self.dateFormatter.string(from: item.createdAt))
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .padding(.vertical, 4)
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    private func detailContent(for item: ClipboardItem) -> some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 12) {
                Text(Self.dateFormatter.string(from: item.createdAt))
                    .font(.caption)
                    .foregroundStyle(.secondary)
                Text(item.text)
                    .font(.body)
                    .textSelection(.enabled)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding()
        }
        .navigationTitle("详情")
        .toolbar {
            ToolbarItemGroup(placement: .primaryAction) {
                Button("复制") {
                    historyStore.copyToPasteboard(item)
                    flashCopyToast()
                }
                Button("删除", role: .destructive) {
                    historyStore.delete(item)
                    selection.remove(item.id)
                    detailItem = nil
                }
            }
        }
    }
}
