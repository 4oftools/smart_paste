import SwiftUI

/// 点击复制后的简短底部提示。
struct CopyToastBanner: View {
    var body: some View {
        Text("已复制到剪贴板")
            .font(.callout.weight(.medium))
            .foregroundStyle(.primary)
            .padding(.horizontal, 16)
            .padding(.vertical, 10)
            .background(.ultraThinMaterial, in: Capsule(style: .continuous))
            .shadow(color: .black.opacity(0.14), radius: 10, y: 4)
    }
}

extension View {
    func copyToastOverlay(isPresented: Bool) -> some View {
        overlay(alignment: .bottom) {
            if isPresented {
                CopyToastBanner()
                    .padding(.bottom, 14)
                    .transition(.move(edge: .bottom).combined(with: .opacity))
            }
        }
        .animation(.spring(response: 0.32, dampingFraction: 0.88), value: isPresented)
    }
}
