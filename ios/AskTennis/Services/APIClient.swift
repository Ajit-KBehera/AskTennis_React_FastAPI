import Foundation

/// Single shared URLSession that stores cookies for the backend domain (required for auth).
final class APIClient {
    static let shared = APIClient()
    private let baseURL: URL
    private let session: URLSession

    private init() {
        self.baseURL = Config.backendBaseURL
        let config = URLSessionConfiguration.default
        config.httpCookieStorage = .shared
        config.httpShouldSetCookies = true
        config.httpCookieAcceptPolicy = .always
        self.session = URLSession(configuration: config)
    }

    private func url(path: String, query: [String: String]? = nil) -> URL {
        var c = URLComponents(url: baseURL.appendingPathComponent(path), resolvingAgainstBaseURL: false)!
        if let q = query, !q.isEmpty {
            c.queryItems = q.map { URLQueryItem(name: $0.key, value: $0.value) }
        }
        return c.url!
    }

    private func request(_ method: String, path: String, query: [String: String]? = nil, body: Data? = nil) -> URLRequest {
        var req = URLRequest(url: url(path: path, query: query))
        req.httpMethod = method
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.setValue("application/json", forHTTPHeaderField: "Accept")
        req.httpBody = body
        return req
    }

    func dataTask(_ request: URLRequest) async throws -> (Data, HTTPURLResponse) {
        let (data, res) = try await session.data(for: request)
        guard let http = res as? HTTPURLResponse else { throw APIError.invalidResponse }
        if http.statusCode >= 400 {
            let detail = (try? JSONDecoder().decode(ErrorDetail.self, from: data))?.detail ?? "Request failed (\(http.statusCode))"
            throw APIError.http(statusCode: http.statusCode, detail: detail)
        }
        return (data, http)
    }

    // MARK: - Auth
    func login(username: String, password: String, rememberMe: Bool) async throws -> AuthResponse {
        let body = LoginRequest(username: username, password: password, remember_me: rememberMe)
        let data = try JSONEncoder().encode(body)
        let req = request("POST", path: "auth/login", body: data)
        let (responseData, _) = try await dataTask(req)
        return try JSONDecoder().decode(AuthResponse.self, from: responseData)
    }

    func register(username: String, password: String) async throws -> UserResponse {
        let body = ["username": username, "password": password]
        let data = try JSONSerialization.data(withJSONObject: body)
        let req = request("POST", path: "auth/register", body: data)
        let (responseData, _) = try await dataTask(req)
        return try JSONDecoder().decode(UserResponse.self, from: responseData)
    }

    func logout() async throws {
        let req = request("POST", path: "auth/logout")
        _ = try await dataTask(req)
    }

    func getMe() async throws -> UserResponse {
        let req = request("GET", path: "auth/me")
        let (data, _) = try await dataTask(req)
        return try JSONDecoder().decode(UserResponse.self, from: data)
    }

    func checkUsername(_ username: String) async throws -> Bool {
        let req = request("GET", path: "auth/check-username", query: ["username": username])
        let (data, _) = try await dataTask(req)
        let decoded = try JSONDecoder().decode(CheckUsernameResponse.self, from: data)
        return decoded.available
    }

    // MARK: - API (require auth cookie)
    func getFilters(playerName: String? = nil) async throws -> FilterOptionsResponse {
        var q: [String: String]?
        if let p = playerName, !p.isEmpty, p != "All Players" { q = ["player_name": p] }
        let req = request("GET", path: "api/filters", query: q)
        let (data, _) = try await dataTask(req)
        return try JSONDecoder().decode(FilterOptionsResponse.self, from: data)
    }

    func query(queryText: String, sessionId: String?) async throws -> AiQueryResponse {
        let body = QueryRequest(query: queryText, session_id: sessionId)
        let data = try JSONEncoder().encode(body)
        let req = request("POST", path: "api/query", body: data)
        let (responseData, _) = try await dataTask(req)
        return try JSONDecoder().decode(AiQueryResponse.self, from: responseData)
    }

    func getQueryHistory(limit: Int = 10) async throws -> [QueryHistoryItem] {
        let req = request("GET", path: "api/query/history", query: ["limit": "\(limit)"])
        let (data, _) = try await dataTask(req)
        let decoded = try JSONDecoder().decode(QueryHistoryResponse.self, from: data)
        return decoded.history
    }

    func getServeStats(_ filters: StatsRequest) async throws -> ServeStatsResponse {
        let data = try JSONEncoder().encode(filters)
        let req = request("POST", path: "api/stats/serve", body: data)
        let (responseData, _) = try await dataTask(req)
        return try JSONDecoder().decode(ServeStatsResponse.self, from: responseData)
    }

    func getReturnStats(_ filters: StatsRequest) async throws -> ReturnStatsResponse {
        let data = try JSONEncoder().encode(filters)
        let req = request("POST", path: "api/stats/return", body: data)
        let (responseData, _) = try await dataTask(req)
        return try JSONDecoder().decode(ReturnStatsResponse.self, from: responseData)
    }

    func getRankingStats(_ filters: StatsRequest) async throws -> RankingStatsResponse {
        let data = try JSONEncoder().encode(filters)
        let req = request("POST", path: "api/stats/ranking", body: data)
        let (responseData, _) = try await dataTask(req)
        return try JSONDecoder().decode(RankingStatsResponse.self, from: responseData)
    }

    func getMatches(_ filters: StatsRequest) async throws -> MatchesResponse {
        let data = try JSONEncoder().encode(filters)
        let req = request("POST", path: "api/matches", body: data)
        let (responseData, _) = try await dataTask(req)
        return try JSONDecoder().decode(MatchesResponse.self, from: responseData)
    }
}

struct CheckUsernameResponse: Codable { let available: Bool }
struct ErrorDetail: Codable { let detail: String }
enum APIError: LocalizedError {
    case invalidResponse
    case http(statusCode: Int, detail: String)
    var errorDescription: String? {
        switch self {
        case .invalidResponse: return "Invalid response"
        case .http(let code, let detail): return "\(detail) (HTTP \(code))"
        }
    }
}
