import AppKit
import SwiftUI

struct PopoverContentView: View {
    @EnvironmentObject private var historyStore: HistoryStore
    @EnvironmentObject private var appSettings: AppSettings
    @Environment(\.openWindow) private var openWindow

    /// At most one row shows the delete lane at a time.
    @State private var revealedSwipeItemID: UUID?
    /// Store id only so alert/dialog does not hold a stale `ClipboardItem` while the list updates.
    @State private var itemIDPendingDelete: ClipboardItem.ID?
    @State private var showDeleteConfirmation = false
    @State private var showCopyToast = false
    @State private var copyToastEpoch = 0

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            header
            Divider()
            recentList
            Divider()
            footer
        }
        .frame(minWidth: 320, maxWidth: 400, minHeight: 280, maxHeight: 480)
        .smartPasteColorScheme(appSettings)
        .windowAppearance(appSettings.colorSchemePreference)
        // 系统 `alert` / `confirmationDialog` 在 MenuBarExtra `.window` 里常无法点到按钮；改为本窗内 overlay。
        .overlay {
            if showDeleteConfirmation {
                deleteConfirmationOverlay
            }
        }
        .copyToastOverlay(isPresented: showCopyToast)
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

    @ViewBuilder
    private var deleteConfirmationOverlay: some View {
        ZStack {
            Color.black.opacity(0.38)
                .ignoresSafeArea()
                .contentShape(Rectangle())
                .onTapGesture {
                    cancelPendingDelete()
                }

            VStack(alignment: .leading, spacing: 14) {
                Text("确定删除这条记录？")
                    .font(.headline)

                Text(pendingDeleteMessage)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .lineLimit(5)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .textSelection(.enabled)

                HStack(spacing: 12) {
                    Button("取消") {
                        cancelPendingDelete()
                    }
                    .keyboardShortcut(.cancelAction)

                    Spacer(minLength: 0)

                    Button("删除", role: .destructive) {
                        if let id = itemIDPendingDelete {
                            historyStore.delete(id: id)
                        }
                        itemIDPendingDelete = nil
                        revealedSwipeItemID = nil
                        showDeleteConfirmation = false
                    }
                    .keyboardShortcut(.defaultAction)
                }
                .buttonStyle(.bordered)
            }
            .padding(18)
            .frame(width: 300)
            .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 12, style: .continuous))
            .shadow(color: .black.opacity(0.2), radius: 18, y: 8)
        }
        .allowsHitTesting(true)
    }

    private func cancelPendingDelete() {
        itemIDPendingDelete = nil
        showDeleteConfirmation = false
    }

    private var pendingDeleteMessage: String {
        guard let id = itemIDPendingDelete,
              let text = historyStore.items.first(where: { $0.id == id })?.text
        else { return "（无预览）" }
        let maxLen = 280
        if text.count <= maxLen { return text }
        return String(text.prefix(maxLen)) + "…"
    }

    /// LSUIElement + MenuBarExtra 下同步 `openWindow` 常被挡在后面；先激活应用并在下一拍打开。
    private func presentAuxiliaryWindow(id: String) {
        Task { @MainActor in
            await Task.yield()
            NSApp.activate(ignoringOtherApps: true)
            openWindow(id: id)
        }
    }

    private var header: some View {
        HStack {
            Text("Smart Paste")
                .font(.headline)
            Spacer()
            Picker(
                "",
                selection: Binding(
                    get: { appSettings.colorSchemePreference },
                    set: { appSettings.colorSchemePreference = $0 }
                )
            ) {
                ForEach(ColorSchemePreference.allCases) { pref in
                    Text(pref.displayName).tag(pref)
                }
            }
            .labelsHidden()
            .frame(maxWidth: 140)
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 10)
    }

    private var recentList: some View {
        Group {
            if historyStore.items.isEmpty {
                ContentUnavailableView("暂无记录", systemImage: "tray", description: Text("复制任意文本后将出现在这里"))
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 0) {
                        ForEach(Array(historyStore.items.prefix(10))) { item in
                            PopoverPasteSwipeRow(
                                item: item,
                                timeText: ClipboardItem.listDisplayDateFormatter.string(from: item.createdAt),
                                revealedSwipeItemID: $revealedSwipeItemID,
                                onCopy: {
                                    historyStore.copyToPasteboard(item)
                                    flashCopyToast()
                                },
                                onDeleteTap: {
                                    itemIDPendingDelete = item.id
                                    showDeleteConfirmation = true
                                }
                            )
                            Divider()
                        }
                    }
                }
            }
        }
    }

    private var footer: some View {
        VStack(spacing: 8) {
            HStack(spacing: 10) {
                Button("主面板…") {
                    presentAuxiliaryWindow(id: "main")
                }
                .keyboardShortcut("o", modifiers: [.command])

                Button("设置…") {
                    presentAuxiliaryWindow(id: "settings")
                }
                .keyboardShortcut(",", modifiers: [.command])
            }
            Button("退出 Smart Paste") {
                NSApplication.shared.terminate(nil)
            }
            .foregroundStyle(.secondary)
        }
        .padding(12)
        .frame(maxWidth: .infinity)
    }
}

// MARK: - Swipe row

private struct PopoverPasteSwipeRow: View {
    let item: ClipboardItem
    let timeText: String
    @Binding var revealedSwipeItemID: UUID?
    let onCopy: () -> Void
    let onDeleteTap: () -> Void

    private let deleteLaneWidth: CGFloat = 72

    @State private var offset: CGFloat = 0
    @State private var gestureStartOffset: CGFloat = 0
    @State private var dragActive = false

    var body: some View {
        ZStack(alignment: .trailing) {
            HStack(spacing: 0) {
                Spacer(minLength: 0)
                Button {
                    onDeleteTap()
                } label: {
                    Text("删除")
                        .font(.body.weight(.medium))
                        .foregroundStyle(.white)
                        .frame(width: deleteLaneWidth)
                        .frame(maxHeight: .infinity)
                        .background(Color.red.opacity(0.92))
                }
                .buttonStyle(.plain)
            }

            rowForeground
                .background(Color(nsColor: .windowBackgroundColor))
                .offset(x: offset)
                .simultaneousGesture(
                    DragGesture(minimumDistance: 12, coordinateSpace: .local)
                        .onChanged { value in
                            if !dragActive {
                                dragActive = true
                                gestureStartOffset = offset
                                if revealedSwipeItemID != item.id {
                                    revealedSwipeItemID = item.id
                                }
                            }
                            let raw = gestureStartOffset + value.translation.width
                            offset = min(0, max(-deleteLaneWidth, raw))
                        }
                        .onEnded { _ in
                            dragActive = false
                            let shouldOpen = offset < -deleteLaneWidth * 0.45
                                || (gestureStartOffset < -deleteLaneWidth * 0.45 && offset < -deleteLaneWidth * 0.2)
                            withAnimation(.spring(response: 0.32, dampingFraction: 0.86)) {
                                if shouldOpen {
                                    offset = -deleteLaneWidth
                                    revealedSwipeItemID = item.id
                                } else {
                                    offset = 0
                                    if revealedSwipeItemID == item.id {
                                        revealedSwipeItemID = nil
                                    }
                                }
                            }
                        }
                )
        }
        .clipped()
        .onChange(of: revealedSwipeItemID) { _, newValue in
            guard newValue != item.id, offset != 0 else { return }
            withAnimation(.spring(response: 0.28, dampingFraction: 0.9)) {
                offset = 0
            }
        }
    }

    private var rowForeground: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(item.text)
                .font(.body)
                .lineLimit(1)
                .truncationMode(.tail)
                .multilineTextAlignment(.leading)
                .foregroundStyle(.primary)
            Text(timeText)
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .contentShape(Rectangle())
        .onTapGesture {
            if offset == 0 {
                onCopy()
            } else {
                withAnimation(.spring(response: 0.28, dampingFraction: 0.9)) {
                    offset = 0
                    if revealedSwipeItemID == item.id {
                        revealedSwipeItemID = nil
                    }
                }
            }
        }
    }
}
