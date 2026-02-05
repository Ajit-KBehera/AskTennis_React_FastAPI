import React, { useState } from 'react';
import { useAuth } from '../store/AuthContext';

const Login: React.FC = () => {
    const [isLogin, setIsLogin] = useState(true);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login, register } = useAuth();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        try {
            if (isLogin) {
                await login({ username, password });
            } else {
                await register({ username, password });
                setIsLogin(true);
                setError('Account created! Please login.');
            }
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Authentication failed');
        }
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-[400px] p-8 bg-white/10 backdrop-blur-md rounded-2xl border border-white/20 shadow-2xl">
            <h2 className="text-3xl font-bold text-white mb-6">
                {isLogin ? 'Welcome Back' : 'Create Account'}
            </h2>

            <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-4">
                <div>
                    <input
                        type="text"
                        placeholder="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/40 focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                        required
                    />
                </div>
                <div>
                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-white/40 focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                        required
                    />
                </div>

                {error && <p className="text-red-400 text-sm text-center">{error}</p>}

                <button
                    type="submit"
                    className="w-full py-3 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-xl transition-colors shadow-lg shadow-blue-900/20"
                >
                    {isLogin ? 'Sign In' : 'Sign Up'}
                </button>
            </form>

            <button
                onClick={() => setIsLogin(!isLogin)}
                className="mt-6 text-white/60 hover:text-white text-sm transition-colors"
            >
                {isLogin ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
            </button>
        </div>
    );
};

export default Login;
