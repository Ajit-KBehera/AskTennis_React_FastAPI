import SwiftUI

struct LoginView: View {
    @ObservedObject var auth: AuthViewModel
    @State private var isLogin = true
    @State private var username = ""
    @State private var password = ""
    @State private var rememberMe = false
    @State private var isSubmitting = false
    @State private var usernameError = ""
    @State private var passwordError = ""
    @State private var usernameAvailable: Bool?
    @State private var checkingUsername = false
    @State private var showPassword = false
    @State private var successMessage = ""

    var body: some View {
        ZStack {
            backgroundGradient
            VStack(spacing: 0) {
                Spacer()
                card
                Spacer()
            }
        }
        .animation(.easeOut(duration: 0.2), value: isLogin)
    }

    private var backgroundGradient: some View {
        LinearGradient(
            colors: [
                Color(red: 0.06, green: 0.09, blue: 0.16),
                Color(red: 0.06, green: 0.09, blue: 0.16)
            ],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )
        .overlay(
            RadialGradient(
                colors: [
                    Color.blue.opacity(0.15),
                    Color.clear
                ],
                center: .init(x: 0.15, y: 0.5),
                startRadius: 0,
                endRadius: 300
            )
        )
        .overlay(
            RadialGradient(
                colors: [
                    Color(red: 0.13, green: 0.77, blue: 0.37).opacity(0.1),
                    Color.clear
                ],
                center: .init(x: 0.85, y: 0.3),
                startRadius: 0,
                endRadius: 300
            )
        )
        .ignoresSafeArea()
    }

    private var card: some View {
        VStack(spacing: 20) {
            Text(isLogin ? "Welcome Back" : "Create Account")
                .font(.system(size: 28, weight: .bold))
                .foregroundColor(.white)
            Text(isLogin ? "Sign in to access AskTennis AI" : "Join AskTennis AI to explore tennis analytics")
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.6))

            VStack(alignment: .leading, spacing: 16) {
                usernameField
                passwordField
                if isLogin {
                    rememberMeToggle
                }
                if !successMessage.isEmpty {
                    HStack(spacing: 8) {
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundColor(.green)
                        Text(successMessage)
                            .font(.subheadline)
                            .foregroundColor(.green)
                    }
                    .padding(12)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.green.opacity(0.1))
                    .cornerRadius(12)
                }
                if let err = auth.error {
                    HStack(spacing: 8) {
                        Image(systemName: "exclamationmark.circle.fill")
                            .foregroundColor(.red)
                        Text(err)
                            .font(.subheadline)
                            .foregroundColor(.red)
                    }
                    .padding(12)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.red.opacity(0.1))
                    .cornerRadius(12)
                }
                submitButton
            }
            .padding(24)

            Button {
                isLogin.toggle()
                auth.error = nil
                successMessage = ""
                usernameError = ""
                passwordError = ""
                usernameAvailable = nil
                password = ""
            } label: {
                Text(isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in")
                    .font(.subheadline)
                    .foregroundColor(.white.opacity(0.6))
            }
            .disabled(isSubmitting)
        }
        .frame(maxWidth: 400)
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 20, style: .continuous))
        .overlay(RoundedRectangle(cornerRadius: 20, style: .continuous).stroke(.white.opacity(0.2), lineWidth: 1))
        .shadow(color: .black.opacity(0.3), radius: 20, x: 0, y: 10)
        .padding(.horizontal, 24)
    }

    private var usernameField: some View {
        VStack(alignment: .leading, spacing: 6) {
            TextField("Username", text: $username)
                .textContentType(.username)
                .autocapitalization(.none)
                .disableAutocorrection(true)
                .padding(14)
                .background(Color.white.opacity(0.05))
                .cornerRadius(12)
                .foregroundColor(.white)
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(
                            usernameError.isEmpty && usernameAvailable != false
                                ? Color.white.opacity(0.1)
                                : (usernameAvailable == true ? Color.green.opacity(0.5) : Color.red.opacity(0.5)),
                            lineWidth: 1
                        )
                )
                .disabled(isSubmitting)
                .onChange(of: username) { _, _ in
                    if !isLogin {
                        validateUsername()
                        if username.count >= 3, usernameError.isEmpty {
                            Task { await checkUsername() }
                        } else {
                            usernameAvailable = nil
                        }
                    } else {
                        usernameError = ""
                    }
                }
            if !usernameError.isEmpty {
                Text(usernameError)
                    .font(.caption)
                    .foregroundColor(.red)
            }
            if !isLogin, username.count >= 3, usernameError.isEmpty {
                if checkingUsername {
                    Text("Checking availability...")
                        .font(.caption)
                        .foregroundColor(.white.opacity(0.5))
                } else if let avail = usernameAvailable {
                    Text(avail ? "Username available" : "Username already taken")
                        .font(.caption)
                        .foregroundColor(avail ? .green : .red)
                }
            }
        }
    }

    private var passwordField: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                Group {
                    if showPassword {
                        TextField("Password", text: $password)
                    } else {
                        SecureField("Password", text: $password)
                    }
                }
                .textContentType(isLogin ? .password : .newPassword)
                .padding(14)
                .background(Color.white.opacity(0.05))
                .cornerRadius(12)
                .foregroundColor(.white)
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(passwordError.isEmpty ? Color.white.opacity(0.1) : Color.red.opacity(0.5), lineWidth: 1)
                )
                .disabled(isSubmitting)
                .onChange(of: password) { _, _ in
                    if !isLogin { validatePassword() }
                    else { passwordError = "" }
                }
                Button {
                    showPassword.toggle()
                } label: {
                    Image(systemName: showPassword ? "eye.slash" : "eye")
                        .foregroundColor(.white.opacity(0.5))
                }
            }
            if !passwordError.isEmpty {
                Text(passwordError)
                    .font(.caption)
                    .foregroundColor(.red)
            }
        }
    }

    private var rememberMeToggle: some View {
        Toggle(isOn: $rememberMe) {
            Text("Remember me for 30 days")
                .font(.subheadline)
                .foregroundColor(.white.opacity(0.8))
        }
        .tint(Color(red: 0.13, green: 0.77, blue: 0.37))
        .disabled(isSubmitting)
    }

    private var submitButton: some View {
        Button {
            Task {
                guard validateForm() else { return }
                isSubmitting = true
                if isLogin {
                    await auth.login(username: username, password: password, rememberMe: rememberMe)
                } else {
                    await auth.register(username: username, password: password)
                    if auth.error == nil {
                        successMessage = "Account created! Signing you in..."
                    }
                }
                isSubmitting = false
            }
        } label: {
            HStack {
                if isSubmitting {
                    ProgressView()
                        .tint(.white)
                }
                Text(isSubmitting ? (isLogin ? "Signing In..." : "Creating Account...") : (isLogin ? "Sign In" : "Sign Up"))
                    .fontWeight(.semibold)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
            .background(Color.blue)
            .foregroundColor(.white)
            .cornerRadius(12)
        }
        .disabled(isSubmitting || !canSubmit)
    }

    private var canSubmit: Bool {
        guard !username.trimmingCharacters(in: .whitespaces).isEmpty, !password.isEmpty else { return false }
        if !isLogin {
            if !usernameError.isEmpty || !passwordError.isEmpty { return false }
            if username.count >= 3, usernameAvailable == false { return false }
        }
        return true
    }

    private func validateUsername() {
        if username.count < 3 {
            usernameError = "Username must be at least 3 characters"
        } else if username.count > 50 {
            usernameError = "Username must be less than 50 characters"
        } else if !username.allSatisfy({ $0.isLetter || $0.isNumber || $0 == "_" }) {
            usernameError = "Username can only contain letters, numbers, and underscores"
        } else {
            usernameError = ""
        }
    }

    private func validatePassword() {
        if password.count < 8 {
            passwordError = "Password must be at least 8 characters"
        } else if !password.contains(where: { $0.isLetter }) {
            passwordError = "Password must contain at least one letter"
        } else if !password.contains(where: { $0.isNumber }) {
            passwordError = "Password must contain at least one number"
        } else {
            passwordError = ""
        }
    }

    private func validateForm() -> Bool {
        usernameError = ""
        passwordError = ""
        if username.trimmingCharacters(in: .whitespaces).isEmpty {
            usernameError = "Username is required"
            return false
        }
        if password.isEmpty {
            passwordError = "Password is required"
            return false
        }
        if !isLogin {
            validateUsername()
            validatePassword()
            if !usernameError.isEmpty || !passwordError.isEmpty { return false }
            if usernameAvailable == false { return false }
        }
        return true
    }

    private func checkUsername() async {
        checkingUsername = true
        defer { checkingUsername = false }
        do {
            usernameAvailable = try await APIClient.shared.checkUsername(username)
        } catch {
            usernameAvailable = nil
        }
    }
}
