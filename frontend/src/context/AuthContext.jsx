import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(null);
    const [loading, setLoading] = useState(true);

    // Load user from localStorage on mount
    useEffect(() => {
        const storedToken = localStorage.getItem('token');
        const storedUser = localStorage.getItem('user');

        if (storedToken && storedUser) {
            setToken(storedToken);
            setUser(JSON.parse(storedUser));
        }
        setLoading(false);
    }, []);

    const login = async (email, password) => {
        try {
            const response = await axios.post('http://localhost:8000/api/v1/auth/login', {
                email,
                password
            });

            const { access_token, ...userData } = response.data;

            setToken(access_token);
            setUser(userData);

            localStorage.setItem('token', access_token);
            localStorage.setItem('user', JSON.stringify(userData));

            return { success: true };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.detail || 'Login failed'
            };
        }
    };

    const signup = async (email, password, fullName, role) => {
        try {
            const response = await axios.post('http://localhost:8000/api/v1/auth/signup', {
                email,
                password,
                full_name: fullName,
                role
            });

            const { access_token, ...userData } = response.data;

            setToken(access_token);
            setUser(userData);

            localStorage.setItem('token', access_token);
            localStorage.setItem('user', JSON.stringify(userData));

            return { success: true };
        } catch (error) {
            return {
                success: false,
                error: error.response?.data?.detail || 'Signup failed'
            };
        }
    };

    const logout = () => {
        setToken(null);
        setUser(null);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
    };

    const value = {
        user,
        token,
        loading,
        login,
        signup,
        logout,
        isAuthenticated: !!token,
        isStudio: user?.role === 'studio',
        isCustomer: user?.role === 'customer'
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};
