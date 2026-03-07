import SwiftUI

@main
struct AskTennisApp: App {
    @StateObject private var auth = AuthViewModel()

    var body: some Scene {
        WindowGroup {
            Group {
                if auth.isLoading {
                    loadingView
                } else if auth.user == nil {
                    LoginView(auth: auth)
                } else {
                    ContentView(auth: auth)
                }
            }
            .task {
                await auth.checkAuth()
            }
            .preferredColorScheme(.dark)
        }
    }

    private var loadingView: some View {
        ZStack {
            Color(red: 0.06, green: 0.09, blue: 0.16)
                .ignoresSafeArea()
            VStack(spacing: 16) {
                Image(systemName: "figure.tennis")
                    .font(.system(size: 48))
                    .foregroundColor(Color(red: 0.13, green: 0.77, blue: 0.37))
                ProgressView()
                    .tint(.white)
                Text("Loading…")
                    .foregroundColor(.white.opacity(0.7))
            }
        }
    }
}
