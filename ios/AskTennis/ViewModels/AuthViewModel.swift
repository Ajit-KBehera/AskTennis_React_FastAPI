import Foundation
import SwiftUI

@MainActor
final class AuthViewModel: ObservableObject {
    @Published var user: String?
    @Published var isLoading = true
    @Published var error: String?

    private let client = APIClient.shared

    func checkAuth() async {
        isLoading = true
        defer { isLoading = false }
        do {
            let me = try await client.getMe()
            user = me.username
        } catch {
            user = nil
        }
    }

    func login(username: String, password: String, rememberMe: Bool) async {
        error = nil
        do {
            _ = try await client.login(username: username, password: password, rememberMe: rememberMe)
            let me = try await client.getMe()
            user = me.username
        } catch let e as APIError {
            error = e.errorDescription
        } catch let err {
            error = err.localizedDescription
        }
    }

    func register(username: String, password: String) async {
        error = nil
        do {
            _ = try await client.register(username: username, password: password)
            await login(username: username, password: password, rememberMe: false)
        } catch let e as APIError {
            error = e.errorDescription
        } catch let err {
            error = err.localizedDescription
        }
    }

    func logout() async {
        try? await client.logout()
        user = nil
    }
}
