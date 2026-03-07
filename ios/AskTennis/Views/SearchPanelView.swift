import SwiftUI

struct SearchPanelView: View {
    @Binding var query: String
    let onSubmit: (String) -> Void
    let disabled: Bool

    private static let placeholders = [
        "e.g. Who won Wimbledon 2023?",
        "e.g. Federer vs Nadal on clay",
        "e.g. Top 10 players in 2024",
        "e.g. Roger Federer vs Nadal stats",
    ]

    @State private var placeholderIndex = 0

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: "magnifyingglass")
                .foregroundColor(disabled ? .white.opacity(0.3) : Color(red: 0.13, green: 0.77, blue: 0.37))
            TextField(Self.placeholders[placeholderIndex], text: $query)
                .textFieldStyle(.plain)
                .foregroundColor(.white)
                .disabled(disabled)
                .onSubmit {
                    if !query.trimmingCharacters(in: .whitespaces).isEmpty {
                        onSubmit(query.trimmingCharacters(in: .whitespaces))
                    }
                }
            Button {
                guard !query.trimmingCharacters(in: .whitespaces).isEmpty else { return }
                onSubmit(query.trimmingCharacters(in: .whitespaces))
            } label: {
                if disabled {
                    ProgressView()
                        .tint(.black)
                        .frame(width: 44, height: 44)
                } else {
                    Text("Analyze")
                        .fontWeight(.bold)
                        .foregroundColor(.black)
                        .padding(.horizontal, 20)
                        .padding(.vertical, 14)
                }
            }
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(disabled ? Color.gray : Color(red: 0.13, green: 0.77, blue: 0.37))
            )
            .disabled(disabled || query.trimmingCharacters(in: .whitespaces).isEmpty)
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 20, style: .continuous)
                .fill(Color.white.opacity(0.06))
                .overlay(RoundedRectangle(cornerRadius: 20, style: .continuous).stroke(Color.white.opacity(0.1), lineWidth: 1))
        )
        .onAppear {
            placeholderIndex = 0
        }
    }
}
