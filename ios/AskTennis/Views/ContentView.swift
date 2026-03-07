import SwiftUI

struct ContentView: View {
    @ObservedObject var auth: AuthViewModel
    @State private var queryText = ""
    @State private var lastSubmittedQuery = ""
    @StateObject private var ai = AIQueryViewModel()

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                HeaderView(user: auth.user ?? "", onLogout: {
                    Task { await auth.logout() }
                })

                SearchPanelView(
                    query: $queryText,
                    onSubmit: submitQuery,
                    disabled: ai.loading
                )

                if !ai.loading && !ai.hasResponse && ai.error == nil {
                    QuickInsightsView(onInsightClick: submitQuery, recentQueries: ai.recentQueries)
                }

                if ai.loading {
                    loadingCard
                }

                if let err = ai.error {
                    errorCard(err)
                }

                if !ai.loading && ai.hasResponse, let r = ai.response {
                    AiResponseView(response: r.answer, sqlQueries: r.sql_queries, data: r.data, conversationFlow: r.conversation_flow)
                }
            }
            .padding()
        }
        .background(backgroundGradient)
        .task { await ai.loadHistory() }
    }

    private var loadingCard: some View {
        VStack(spacing: 16) {
            ProgressView()
                .tint(Color(red: 0.13, green: 0.77, blue: 0.37))
            Text("Analyzing tennis data…")
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.6))
        }
        .frame(maxWidth: .infinity)
        .padding(40)
        .background(glassCard)
    }

    private func errorCard(_ message: String) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack(spacing: 8) {
                Image(systemName: "exclamationmark.circle.fill")
                    .foregroundColor(.red)
                Text("Analysis Error")
                    .font(.headline)
                    .foregroundColor(.red)
            }
            Text(message)
                .font(.subheadline)
                .foregroundColor(.red.opacity(0.9))
            HStack(spacing: 12) {
                Button("Retry") {
                    ai.reset()
                    submitQuery(lastSubmittedQuery)
                }
                .foregroundColor(.red)
                Button("Edit question") {
                    ai.reset()
                    queryText = lastSubmittedQuery
                }
                .foregroundColor(.white.opacity(0.8))
            }
        }
        .padding(20)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color.red.opacity(0.1))
        .cornerRadius(16)
        .overlay(RoundedRectangle(cornerRadius: 16).stroke(Color.red.opacity(0.2), lineWidth: 1))
    }

    private var backgroundGradient: some View {
        Color(red: 0.06, green: 0.09, blue: 0.16)
            .overlay(
                RadialGradient(
                    colors: [Color.blue.opacity(0.15), Color.clear],
                    center: .init(x: 0.15, y: 0.5),
                    startRadius: 0,
                    endRadius: 400
                )
            )
            .overlay(
                RadialGradient(
                    colors: [Color(red: 0.13, green: 0.77, blue: 0.37).opacity(0.08), Color.clear],
                    center: .init(x: 0.85, y: 0.3),
                    startRadius: 0,
                    endRadius: 400
                )
            )
            .ignoresSafeArea()
    }

    private var glassCard: some View {
        RoundedRectangle(cornerRadius: 20, style: .continuous)
            .fill(Color.white.opacity(0.05))
            .overlay(RoundedRectangle(cornerRadius: 20, style: .continuous).stroke(Color.white.opacity(0.1), lineWidth: 1))
    }

    private func submitQuery(_ q: String) {
        let trimmed = q.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        lastSubmittedQuery = trimmed
        Task {
            await ai.submit(trimmed)
        }
    }
}
