import SwiftUI

struct QuickInsightsView: View {
    let onInsightClick: (String) -> Void
    let recentQueries: [String]

    private static let insightsByCategory: [(String, [String])] = [
        ("Head to head", [
            "Federer vs Nadal head to head on clay",
            "Djokovic vs Nadal at Roland Garros",
            "Federer vs Djokovic at Wimbledon",
        ]),
        ("Grand Slams", [
            "Who won Wimbledon 2023?",
            "Most US Open titles in the Open Era",
            "French Open winners in the last 10 years",
        ]),
        ("Rankings & records", [
            "Top 10 players in 2024",
            "Who has the most aces in a single match?",
            "Longest winning streak in ATP history",
        ]),
    ]

    private static var allInsights: [String] {
        insightsByCategory.flatMap { $0.1 }
    }

    var body: some View {
        VStack(spacing: 20) {
            Text("Ask anything about 147 years of tennis—players, matches, rankings.")
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.6))
                .multilineTextAlignment(.center)

            if !recentQueries.isEmpty {
                VStack(alignment: .leading, spacing: 8) {
                    Text("YOU RECENTLY ASKED")
                        .font(.caption2)
                        .fontWeight(.semibold)
                        .foregroundColor(.white.opacity(0.5))
                    FlowLayout(spacing: 8) {
                        ForEach(Array(recentQueries.prefix(3).enumerated()), id: \.offset) { _, q in
                            Button {
                                onInsightClick(q)
                            } label: {
                                Text(q.count > 45 ? String(q.prefix(45)) + "…" : q)
                                    .font(.caption)
                                    .foregroundColor(.white.opacity(0.85))
                                    .padding(.horizontal, 14)
                                    .padding(.vertical, 10)
                                    .background(Color.white.opacity(0.05))
                                    .cornerRadius(20)
                            }
                            .buttonStyle(.plain)
                        }
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }

            VStack(alignment: .leading, spacing: 8) {
                Text("TRY AN INSIGHT")
                    .font(.caption2)
                    .fontWeight(.semibold)
                    .foregroundColor(.white.opacity(0.5))
                FlowLayout(spacing: 8) {
                    ForEach(Self.allInsights, id: \.self) { q in
                        Button {
                            onInsightClick(q)
                        } label: {
                            HStack(spacing: 6) {
                                Image(systemName: "info.circle")
                                    .font(.caption2)
                                    .opacity(0.6)
                                Text(q)
                                    .font(.caption)
                            }
                            .foregroundColor(.white.opacity(0.85))
                            .padding(.horizontal, 14)
                            .padding(.vertical, 10)
                            .background(Color.white.opacity(0.05))
                            .cornerRadius(20)
                        }
                        .buttonStyle(.plain)
                    }
                    Button {
                        let q = Self.allInsights.randomElement() ?? Self.allInsights[0]
                        onInsightClick(q)
                    } label: {
                        HStack(spacing: 6) {
                            Image(systemName: "shuffle")
                            Text("Surprise me")
                                .font(.caption)
                                .fontWeight(.medium)
                        }
                        .foregroundColor(Color(red: 0.13, green: 0.77, blue: 0.37))
                        .padding(.horizontal, 14)
                        .padding(.vertical, 10)
                        .background(Color(red: 0.13, green: 0.77, blue: 0.37).opacity(0.2))
                        .cornerRadius(20)
                    }
                    .buttonStyle(.plain)
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
        }
    }
}

struct FlowLayout: Layout {
    var spacing: CGFloat = 8
    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let result = arrange(proposal: proposal, subviews: subviews)
        return result.size
    }
    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        let result = arrange(proposal: proposal, subviews: subviews)
        for (i, frame) in result.frames.enumerated() {
            subviews[i].place(at: CGPoint(x: bounds.minX + frame.minX, y: bounds.minY + frame.minY), proposal: .unspecified)
        }
    }
    private func arrange(proposal: ProposedViewSize, subviews: Subviews) -> (size: CGSize, frames: [CGRect]) {
        let maxWidth = proposal.width ?? .infinity
        var x: CGFloat = 0
        var y: CGFloat = 0
        var rowHeight: CGFloat = 0
        var frames: [CGRect] = []
        for subview in subviews {
            let size = subview.sizeThatFits(.unspecified)
            if x + size.width > maxWidth && x > 0 {
                x = 0
                y += rowHeight + spacing
                rowHeight = 0
            }
            frames.append(CGRect(origin: CGPoint(x: x, y: y), size: size))
            rowHeight = max(rowHeight, size.height)
            x += size.width + spacing
        }
        return (CGSize(width: maxWidth, height: y + rowHeight), frames)
    }
}
