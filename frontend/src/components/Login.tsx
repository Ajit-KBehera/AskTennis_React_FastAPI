import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../store/AuthContext';
import { api } from '../api/client';
import { Eye, EyeOff, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';

const Login: React.FC = () => {
    const [isLogin, setIsLogin] = useState(true);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [rememberMe, setRememberMe] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [usernameError, setUsernameError] = useState('');
    const [passwordError, setPasswordError] = useState('');
    const [usernameAvailable, setUsernameAvailable] = useState<boolean | null>(null);
    const [checkingUsername, setCheckingUsername] = useState(false);
    const usernameInputRef = useRef<HTMLInputElement>(null);
    const { login, register } = useAuth();

    // Auto-focus on username field when component mounts or mode changes
    useEffect(() => {
        usernameInputRef.current?.focus();
    }, [isLogin]);

    // Real-time username validation
    useEffect(() => {
        if (username && !isLogin) {
            if (username.length < 3) {
                setUsernameError('Username must be at least 3 characters');
            } else if (username.length > 20) {
                setUsernameError('Username must be less than 20 characters');
            } else if (!/^[a-zA-Z0-9_]+$/.test(username)) {
                setUsernameError('Username can only contain letters, numbers, and underscores');
            } else {
                setUsernameError('');
            }
        } else {
            setUsernameError('');
        }
    }, [username, isLogin]);

    // Debounced username availability check (registration only)
    useEffect(() => {
        if (isLogin || username.length < 3 || usernameError) {
            setUsernameAvailable(null);
            return;
        }
        setUsernameAvailable(null);
        const timeoutId = setTimeout(async () => {
            setCheckingUsername(true);
            try {
                const res = await api.checkUsername(username);
                setUsernameAvailable(res.available);
            } catch {
                setUsernameAvailable(null);
            } finally {
                setCheckingUsername(false);
            }
        }, 500);
        return () => clearTimeout(timeoutId);
    }, [username, isLogin, usernameError]);

    // Real-time password validation
    useEffect(() => {
        if (password && !isLogin) {
            if (password.length < 8) {
                setPasswordError('Password must be at least 8 characters');
            } else if (!/(?=.*[a-z])/.test(password)) {
                setPasswordError('Password must contain at least one lowercase letter');
            } else if (!/(?=.*[A-Z])/.test(password)) {
                setPasswordError('Password must contain at least one uppercase letter');
            } else if (!/(?=.*\d)/.test(password)) {
                setPasswordError('Password must contain at least one number');
            } else {
                setPasswordError('');
            }
        } else {
            setPasswordError('');
        }
    }, [password, isLogin]);

    // Calculate password strength for registration
    const getPasswordStrength = (pwd: string): number => {
        if (!pwd) return 0;
        let strength = 0;
        if (pwd.length >= 8) strength++;
        if (/[a-z]/.test(pwd)) strength++;
        if (/[A-Z]/.test(pwd)) strength++;
        if (/\d/.test(pwd)) strength++;
        if (/[^a-zA-Z\d]/.test(pwd)) strength++;
        return strength;
    };

    const passwordStrength = getPasswordStrength(password);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setSuccess(false);
        setUsernameError('');
        setPasswordError('');

        // Final validation before submit
        if (!username.trim()) {
            setUsernameError('Username is required');
            return;
        }
        if (!password) {
            setPasswordError('Password is required');
            return;
        }
        if (!isLogin && (usernameError || passwordError || usernameAvailable === false)) {
            return;
        }

        setIsSubmitting(true);
        try {
            if (isLogin) {
                await login({ username, password, remember_me: rememberMe });
            } else {
                await register({ username, password });
                setSuccess(true);
                // Auto-switch to login after 2 seconds
                setTimeout(() => {
                    setIsLogin(true);
                    setSuccess(false);
                    setError('');
                    setPassword('');
                }, 2000);
            }
        } catch (err: any) {
            console.error('Auth Error:', err);
            const detail = err.response?.data?.detail;
            
            // Handle rate limiting
            if (err.response?.status === 429) {
                const retryAfter = err.response.headers['retry-after'] || '60';
                setError(`Too many attempts. Please try again in ${retryAfter} seconds.`);
                return;
            }
            
            // Handle validation errors
            if (Array.isArray(detail)) {
                const errorMessages = detail.map((e: any) => e.msg || e.message).join(', ');
                setError(errorMessages);
            } else if (typeof detail === 'string') {
                // Check if it's a username or password specific error
                if (detail.toLowerCase().includes('username')) {
                    setUsernameError(detail);
                } else if (detail.toLowerCase().includes('password')) {
                    setPasswordError(detail);
                } else {
                    setError(detail);
                }
            } else {
                setError('Authentication failed. Please check your credentials and try again.');
            }
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleModeSwitch = () => {
        setIsLogin(!isLogin);
        setError('');
        setSuccess(false);
        setUsernameError('');
        setPasswordError('');
        setUsernameAvailable(null);
        setPassword('');
        setShowPassword(false);
    };

    const registerSubmitDisabled =
        !isLogin &&
        (!!usernameError ||
            !!passwordError ||
            usernameAvailable === false ||
            (username.length >= 3 && usernameAvailable === null && checkingUsername));

    return (
        <div className="flex flex-col items-center justify-center min-h-[400px] p-8 bg-white/10 backdrop-blur-md rounded-2xl border border-white/20 shadow-2xl max-w-md w-full transition-all duration-300 ease-out">
            <h2 className="text-3xl font-bold text-white mb-2 transition-all duration-300">
                {isLogin ? 'Welcome Back' : 'Create Account'}
            </h2>
            <p className="text-white/60 text-sm mb-6 transition-all duration-300">
                {isLogin ? 'Sign in to access AskTennis AI' : 'Join AskTennis AI to explore tennis analytics'}
            </p>

            <form
                key={isLogin ? 'login' : 'register'}
                onSubmit={handleSubmit}
                className="w-full space-y-4 transition-opacity duration-300"
            >
                {/* Username Field */}
                <div className="transition-all duration-200">
                    <label htmlFor="username" className="sr-only">
                        Username
                    </label>
                    <input
                        id="username"
                        ref={usernameInputRef}
                        type="text"
                        placeholder="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        disabled={isSubmitting}
                        className={`w-full px-4 py-3 bg-white/5 border ${
                            usernameError || usernameAvailable === false
                                ? 'border-red-500/50 focus:border-red-500'
                                : usernameAvailable === true
                                ? 'border-green-500/50 focus:border-green-500'
                                : 'border-white/10 focus:border-blue-500'
                        } rounded-xl text-white placeholder-white/40 focus:ring-2 focus:ring-blue-500/50 outline-none transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed`}
                        aria-invalid={!!usernameError || usernameAvailable === false}
                        aria-describedby={
                            usernameError ? 'username-error' : usernameAvailable !== null ? 'username-availability' : undefined
                        }
                        required
                    />
                    {usernameError && (
                        <p
                            id="username-error"
                            role="alert"
                            className="text-red-400 text-xs mt-1 flex items-center gap-1 opacity-100 transition-all duration-200"
                        >
                            <AlertCircle className="w-3 h-3 shrink-0" />
                            {usernameError}
                        </p>
                    )}
                    {!isLogin && !usernameError && username.length >= 3 && (
                        <p
                            id="username-availability"
                            className={`text-xs mt-1 flex items-center gap-1 transition-all duration-200 ${
                                checkingUsername
                                    ? 'text-white/50'
                                    : usernameAvailable === true
                                    ? 'text-green-400'
                                    : usernameAvailable === false
                                    ? 'text-red-400'
                                    : 'text-white/40'
                            }`}
                        >
                            {checkingUsername ? (
                                <>
                                    <Loader2 className="w-3 h-3 shrink-0 animate-spin" />
                                    Checking availability...
                                </>
                            ) : usernameAvailable === true ? (
                                <>
                                    <CheckCircle className="w-3 h-3 shrink-0" />
                                    Username available
                                </>
                            ) : usernameAvailable === false ? (
                                <>
                                    <AlertCircle className="w-3 h-3 shrink-0" />
                                    Username already taken
                                </>
                            ) : null}
                        </p>
                    )}
                </div>

                {/* Password Field */}
                <div>
                    <label htmlFor="password" className="sr-only">
                        Password
                    </label>
                    <div className="relative">
                        <input
                            id="password"
                            type={showPassword ? 'text' : 'password'}
                            placeholder="Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            disabled={isSubmitting}
                            className={`w-full px-4 py-3 pr-12 bg-white/5 border ${
                                passwordError
                                    ? 'border-red-500/50 focus:border-red-500'
                                    : 'border-white/10 focus:border-blue-500'
                            } rounded-xl text-white placeholder-white/40 focus:ring-2 focus:ring-blue-500/50 outline-none transition-all disabled:opacity-50 disabled:cursor-not-allowed`}
                            aria-invalid={!!passwordError}
                            aria-describedby={passwordError ? 'password-error' : undefined}
                            required
                        />
                        <button
                            type="button"
                            onClick={() => setShowPassword(!showPassword)}
                            disabled={isSubmitting}
                            className="absolute right-3 top-1/2 -translate-y-1/2 text-white/40 hover:text-white/60 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            aria-label={showPassword ? 'Hide password' : 'Show password'}
                        >
                            {showPassword ? (
                                <EyeOff className="w-5 h-5" />
                            ) : (
                                <Eye className="w-5 h-5" />
                            )}
                        </button>
                    </div>
                    {passwordError && (
                        <p
                            id="password-error"
                            role="alert"
                            className="text-red-400 text-xs mt-1 flex items-center gap-1"
                        >
                            <AlertCircle className="w-3 h-3" />
                            {passwordError}
                        </p>
                    )}

                    {/* Password Strength Indicator (Registration only) */}
                    {!isLogin && password && (
                        <div className="mt-2">
                            <div className="flex gap-1 mb-1">
                                {[1, 2, 3, 4, 5].map((level) => (
                                    <div
                                        key={level}
                                        className={`h-1.5 flex-1 rounded transition-colors ${
                                            level <= passwordStrength
                                                ? passwordStrength <= 2
                                                    ? 'bg-red-500'
                                                    : passwordStrength <= 4
                                                    ? 'bg-yellow-500'
                                                    : 'bg-green-500'
                                                : 'bg-white/10'
                                        }`}
                                    />
                                ))}
                            </div>
                            <p className="text-xs text-white/60">
                                Strength:{' '}
                                <span
                                    className={
                                        passwordStrength <= 2
                                            ? 'text-red-400'
                                            : passwordStrength <= 4
                                            ? 'text-yellow-400'
                                            : 'text-green-400'
                                    }
                                >
                                    {passwordStrength <= 2
                                        ? 'Weak'
                                        : passwordStrength <= 4
                                        ? 'Medium'
                                        : 'Strong'}
                                </span>
                            </p>
                        </div>
                    )}

                    {/* Password Requirements (Registration only) */}
                    {!isLogin && (
                        <div className="mt-2 text-xs text-white/60 space-y-1">
                            <p className="font-medium mb-1">Password must contain:</p>
                            <ul className="list-disc list-inside space-y-0.5 ml-2">
                                <li
                                    className={
                                        password.length >= 8 ? 'text-green-400' : 'text-white/40'
                                    }
                                >
                                    At least 8 characters
                                </li>
                                <li
                                    className={
                                        /[a-z]/.test(password) ? 'text-green-400' : 'text-white/40'
                                    }
                                >
                                    One lowercase letter
                                </li>
                                <li
                                    className={
                                        /[A-Z]/.test(password) ? 'text-green-400' : 'text-white/40'
                                    }
                                >
                                    One uppercase letter
                                </li>
                                <li
                                    className={
                                        /\d/.test(password) ? 'text-green-400' : 'text-white/40'
                                    }
                                >
                                    One number
                                </li>
                            </ul>
                        </div>
                    )}
                </div>

                {/* Remember Me (Login only) */}
                {isLogin && (
                    <label className="flex items-center gap-2 text-white/70 text-sm cursor-pointer select-none transition-colors hover:text-white/90">
                        <input
                            type="checkbox"
                            checked={rememberMe}
                            onChange={(e) => setRememberMe(e.target.checked)}
                            disabled={isSubmitting}
                            className="w-4 h-4 rounded border-white/30 bg-white/5 text-blue-500 focus:ring-2 focus:ring-blue-500/50 focus:ring-offset-0 transition-all disabled:opacity-50"
                        />
                        Remember me for 30 days
                    </label>
                )}

                {/* Success Message */}
                {success && (
                    <div
                        role="alert"
                        className="bg-green-500/10 border border-green-500/20 rounded-xl p-4 text-green-400 text-sm flex items-center gap-2 transition-all duration-300 opacity-100"
                    >
                        <CheckCircle className="w-5 h-5 shrink-0" />
                        Account created successfully! Redirecting to login...
                    </div>
                )}

                {/* Error Message */}
                {error && (
                    <div
                        role="alert"
                        className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-red-400 text-sm flex items-center gap-2 transition-all duration-300 opacity-100"
                    >
                        <AlertCircle className="w-5 h-5 shrink-0" />
                        <span>{error}</span>
                    </div>
                )}

                {/* Submit Button */}
                <button
                    type="submit"
                    disabled={
                        isSubmitting ||
                        !!usernameError ||
                        !!passwordError ||
                        registerSubmitDisabled
                    }
                    className="w-full py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-400 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-all shadow-lg shadow-blue-900/20 flex items-center justify-center gap-2 hover:scale-[1.02] active:scale-[0.98]"
                >
                    {isSubmitting ? (
                        <>
                            <Loader2 className="w-5 h-5 animate-spin" />
                            <span>{isLogin ? 'Signing In...' : 'Creating Account...'}</span>
                        </>
                    ) : (
                        <span>{isLogin ? 'Sign In' : 'Sign Up'}</span>
                    )}
                </button>
            </form>

            {/* Mode Toggle */}
            <button
                onClick={handleModeSwitch}
                disabled={isSubmitting}
                className="mt-6 text-white/60 hover:text-white text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
                {isLogin ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
            </button>
        </div>
    );
};

export default Login;
