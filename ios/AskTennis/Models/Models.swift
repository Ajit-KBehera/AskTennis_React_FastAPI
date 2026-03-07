import Foundation

// MARK: - Auth
struct UserResponse: Codable {
    let id: Int
    let username: String
    let created_at: String
    let last_login: String?
}

struct AuthResponse: Codable {
    let message: String
    let username: String
}

struct LoginRequest: Codable {
    let username: String
    let password: String
    let remember_me: Bool?
}

// MARK: - Filters
struct FilterOptionsResponse: Codable {
    let players: [String]
    let tournaments: [String]
    let opponents: [String]?
    let surfaces: [String]?
    let year_range: YearRange?
}

struct YearRange: Codable {
    let min: Int
    let max: Int
}

struct StatsRequest: Codable {
    let player_name: String
    var opponent: String?
    var tournament: String?
    var surface: [String]?
    var year: String?
}

// MARK: - Query
struct QueryRequest: Codable {
    let query: String
    let session_id: String?
}

struct AiQueryResponse: Codable {
    let answer: String
    let sql_queries: [String]
    let data: [[String: AnyCodable]]
    let conversation_flow: [ConversationFlowItem]
    let session_id: String
}

struct ConversationFlowItem: Codable {
    let role: String
    let content: String
}

struct QueryHistoryItem: Codable {
    let id: Int
    let query_text: String
    let sql_queries: [String]
    let answer: String
    let data: [[String: AnyCodable]]
    let conversation_flow: [ConversationFlowItem]
    let created_at: String?
}

struct QueryHistoryResponse: Codable {
    let history: [QueryHistoryItem]
}

// MARK: - Stats
struct ServeStatsResponse: Codable {
    let timeline_chart: PlotlyChart?
    let ace_df_chart: PlotlyChart?
    let bp_chart: PlotlyChart?
    let radar_chart: PlotlyChart?
    let matches: [AnyCodable]?
    let aggregated_stats: [String: Double?]?
    let error: String?
}

struct ReturnStatsResponse: Codable {
    let return_points_chart: PlotlyChart?
    let bp_conversion_chart: PlotlyChart?
    let radar_chart: PlotlyChart?
    let matches: [AnyCodable]?
    let error: String?
}

struct RankingStatsResponse: Codable {
    let ranking_chart: PlotlyChart?
    let ranking_data: [AnyCodable]?
    let error: String?
    let reasons: [String]?
}

struct PlotlyChart: Codable {
    let data: [AnyCodable]?
    let layout: [String: AnyCodable]?
}

struct Match: Codable, Identifiable {
    var id: String { "\(event_year)-\(tourney_date)-\(winner_name)-\(loser_name)" }
    let event_year: Int
    let tourney_date: String
    let tourney_name: String
    let round: String
    let winner_name: String
    let loser_name: String
    let surface: String
    let score: String
}

struct MatchesResponse: Codable {
    let matches: [Match]
    let count: Int
}

// Type-erased Codable for dynamic JSON
struct AnyCodable: Codable {
    let value: Any
    init(_ value: Any) { self.value = value }
    init(from decoder: Decoder) throws {
        let c = try decoder.singleValueContainer()
        if let b = try? c.decode(Bool.self) { value = b }
        else if let i = try? c.decode(Int.self) { value = i }
        else if let d = try? c.decode(Double.self) { value = d }
        else if let s = try? c.decode(String.self) { value = s }
        else if let a = try? c.decode([AnyCodable].self) { value = a.map(\.value) }
        else if let m = try? c.decode([String: AnyCodable].self) { value = m.mapValues(\.value) }
        else { value = NSNull() }
    }
    func encode(to encoder: Encoder) throws {
        var c = encoder.singleValueContainer()
        switch value {
        case let b as Bool: try c.encode(b)
        case let i as Int: try c.encode(i)
        case let d as Double: try c.encode(d)
        case let s as String: try c.encode(s)
        case let a as [Any]: try c.encode(a.map { AnyCodable($0) })
        case let m as [String: Any]: try c.encode(m.mapValues { AnyCodable($0) })
        default: try c.encodeNil()
        }
    }
}
