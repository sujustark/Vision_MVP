import { createContext, useContext, useState } from "react";
import api from '../api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));

    const login = async (email, password) => {
        try {
            const response = await api.post('/auth/login', { email, password });
            const { access_token, user_id, full_name, role } = response.data;
            const userData = { user_id, email: response.data.email, full_name, role };
            localStorage.setItem('token', access_token);
            setToken(access_token);
            setUser(userData);
            return { success: true, data: response.data };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.detail || 'Login failed. Please check your credentials.'
            };
        }
    };

    const signup = async (email, password, fullName, role) => {
        try {
            await api.post('/auth/signup', {
                email,
                password,
                full_name: fullName,  // Convert to snake_case for backend
                role,
            });
            // Auto-login after successful signup to get token and user data
            return await login(email, password);
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.detail || 'Signup failed. Please try again.'
            };
        }
    };

    const logout = () => {
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                token,
                login,
                signup,
                logout,
                isAuthenticated: !!token,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => useContext(AuthContext);