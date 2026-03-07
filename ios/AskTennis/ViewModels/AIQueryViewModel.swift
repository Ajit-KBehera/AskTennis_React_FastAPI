import Foundation
import SwiftUI

@MainActor
final class AIQueryViewModel: ObservableObject {
    @Published var response: AiQueryResponse?
    @Published var loading = false
    @Published var error: String?
    @Published var retryAfterSeconds: Int?
    @Published var recentQueries: [String] = []

    private let client = APIClient.shared
    private let sessionKey = "asktennis_session_id"

    var hasResponse: Bool { response != nil }

    func submit(_ queryText: String) async {
        response = nil
        error = nil
        loading = true
        defer { loading = false }
        let sessionId = UserDefaults.standard.string(forKey: sessionKey)
        do {
            let r = try await client.query(queryText: queryText, sessionId: sessionId)
            if !r.session_id.isEmpty {
                UserDefaults.standard.set(r.session_id, forKey: sessionKey)
            }
            response = r
            await loadHistory()
        } catch let e as APIError {
            error = e.errorDescription
            if case .http(let code, _) = e, code == 429 {
                retryAfterSeconds = 60
            }
        } catch let err {
            self.error = err.localizedDescription
        }
    }

    func reset() {
        response = nil
        error = nil
        retryAfterSeconds = nil
    }

    func loadHistory() async {
        do {
            let history = try await client.getQueryHistory(limit: 10)
            recentQueries = history.map(\.query_text).filter { !$0.isEmpty }
        } catch {
            recentQueries = []
        }
    }
}

