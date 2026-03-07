import SwiftUI

struct AiResponseView: View {
    let response: String
    let sqlQueries: [String]
    let data: [[String: AnyCodable]]
    let conversationFlow: [ConversationFlowItem]

    @State private var sqlExpanded = false
    @State private var dataExpanded = false
    @State private var flowExpanded = false

    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            // AI Insight card
            VStack(alignment: .leading, spacing: 12) {
                HStack(spacing: 8) {
                    Image(systemName: "lightbulb.fill")
                        .foregroundColor(.yellow)
                    Text("AI INSIGHT")
                        .font(.caption)
                        .fontWeight(.bold)
                        .foregroundColor(Color(red: 0.13, green: 0.77, blue: 0.37))
                }
                MarkdownView(markdown: response)
            }
            .padding(24)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(
                RoundedRectangle(cornerRadius: 24, style: .continuous)
                    .fill(Color.white.opacity(0.06))
                    .overlay(RoundedRectangle(cornerRadius: 24, style: .continuous).stroke(Color.white.opacity(0.1), lineWidth: 1))
            )

            if !sqlQueries.isEmpty {
                DisclosureGroup("Technical Reasoning (SQL)", isExpanded: $sqlExpanded) {
                    VStack(alignment: .leading, spacing: 12) {
                        ForEach(Array(sqlQueries.reversed().enumerated()), id: \.offset) { _, sql in
                            Text(sql)
                                .font(.system(.caption, design: .monospaced))
                                .foregroundColor(Color(red: 0.13, green: 0.77, blue: 0.37))
                                .padding(12)
                                .frame(maxWidth: .infinity, alignment: .leading)
                                .background(Color.black.opacity(0.3))
                                .cornerRadius(8)
                        }
                    }
                    .padding(.top, 8)
                }
                .tint(Color(red: 0.13, green: 0.77, blue: 0.37))
                .foregroundColor(.white)
            }

            if !data.isEmpty {
                DisclosureGroup("Query Results (\(data.count) rows)", isExpanded: $dataExpanded) {
                    DataTableView(rows: data)
                        .frame(maxHeight: 400)
                        .padding(.top, 8)
                }
                .tint(Color(red: 0.13, green: 0.77, blue: 0.37))
                .foregroundColor(.white)
            }

            if conversationFlow.count > 1 {
                DisclosureGroup("💬 Conversational Flow", isExpanded: $flowExpanded) {
                    VStack(alignment: .leading, spacing: 12) {
                        ForEach(Array(conversationFlow.dropLast().enumerated()), id: \.offset) { i, item in
                            VStack(alignment: .leading, spacing: 4) {
                                Text(item.role.capitalized)
                                    .font(.caption)
                                    .fontWeight(.bold)
                                    .foregroundColor(.white.opacity(0.8))
                                Text(item.content)
                                    .font(.caption)
                                    .foregroundColor(.white.opacity(0.7))
                            }
                            .padding(12)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .background(Color.white.opacity(0.05))
                            .cornerRadius(12)
                            if i < conversationFlow.count - 2 {
                                Divider()
                                    .background(Color.white.opacity(0.1))
                            }
                        }
                    }
                    .padding(.top, 8)
                }
                .tint(Color(red: 0.13, green: 0.77, blue: 0.37))
                .foregroundColor(.white)
            }
        }
    }
}

struct MarkdownView: View {
    let markdown: String
    var body: some View {
        if let attr = try? AttributedString(markdown: markdown) {
            Text(attr)
                .font(.body)
                .foregroundColor(.white.opacity(0.9))
        } else {
            Text(markdown)
                .font(.body)
                .foregroundColor(.white.opacity(0.9))
        }
    }
}

struct DataTableView: View {
    let rows: [[String: AnyCodable]]

    var body: some View {
        ScrollView([.horizontal, .vertical]) {
            if let first = rows.first {
                let keys = Array(first.keys).sorted()
                Grid(alignment: .leading, horizontalSpacing: 12, verticalSpacing: 8) {
                    GridRow {
                        ForEach(keys, id: \.self) { key in
                            Text(key)
                                .font(.caption)
                                .fontWeight(.bold)
                                .foregroundColor(.white.opacity(0.8))
                        }
                    }
                    ForEach(Array(rows.enumerated()), id: \.offset) { _, row in
                        GridRow {
                            ForEach(keys, id: \.self) { key in
                                Text(stringValue(row[key]?.value))
                                    .font(.caption)
                                    .foregroundColor(.white.opacity(0.7))
                            }
                        }
                    }
                }
                .padding(12)
            }
        }
        .background(Color.white.opacity(0.05))
        .cornerRadius(12)
    }

    private func stringValue(_ v: Any?) -> String {
        guard let v = v else { return "—" }
        if v is NSNull { return "—" }
        return "\(v)"
    }
}
