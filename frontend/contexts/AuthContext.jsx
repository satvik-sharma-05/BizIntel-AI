import { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { api } from '../lib/api';
import toast from 'react-hot-toast';

const AuthContext = createContext();

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        checkAuth();
    }, []);

    const checkAuth = async () => {
        try {
            const token = localStorage.getItem('token');
            if (token) {
                api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
                const response = await api.get('/auth/me');
                setUser(response.data);
            }
        } catch (error) {
            console.error('Auth check failed:', error);
            localStorage.removeItem('token');
            delete api.defaults.headers.common['Authorization'];
        } finally {
            setLoading(false);
        }
    };

    const signup = async (email, password, name) => {
        try {
            const response = await api.post('/auth/signup', { email, password, name });
            const { access_token, user_id, email: userEmail, name: userName } = response.data;

            localStorage.setItem('token', access_token);
            api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

            const userData = {
                user_id,
                email: userEmail,
                name: userName
            };
            setUser(userData);

            toast.success(`Welcome, ${userName}! 🎉`);
            return { success: true };
        } catch (error) {
            const errorMessage = error.response?.data?.detail || 'Signup failed. Please try again.';
            toast.error(errorMessage);
            return {
                success: false,
                error: errorMessage
            };
        }
    };

    const login = async (email, password) => {
        try {
            const response = await api.post('/auth/login', { email, password });
            const { access_token, user_id, email: userEmail, name: userName } = response.data;

            localStorage.setItem('token', access_token);
            api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

            const userData = {
                user_id,
                email: userEmail,
                name: userName
            };
            setUser(userData);

            toast.success(`Welcome back, ${userName}! 👋`);
            return { success: true };
        } catch (error) {
            const errorMessage = error.response?.data?.detail || 'Login failed. Please try again.';
            toast.error(errorMessage);
            return {
                success: false,
                error: errorMessage
            };
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('currentBusinessId');
        delete api.defaults.headers.common['Authorization'];
        setUser(null);
        toast.success('Logged out successfully');
        router.push('/login');
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                loading,
                signup,
                login,
                logout,
                isAuthenticated: !!user,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
}
