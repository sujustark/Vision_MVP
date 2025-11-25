import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function ProtectedRoute({ children, requireRole }) {
    const { isAuthenticated, user, loading } = useAuth();

    if (loading) {
        return (
            <div className="container">
                <div className="card">
                    <p>Loading...</p>
                </div>
            </div>
        );
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    if (requireRole && user?.role !== requireRole) {
        return (
            <div className="container">
                <div className="card">
                    <h2>Access Denied</h2>
                    <p>You don't have permission to access this page.</p>
                    <p>Required role: {requireRole}</p>
                    <p>Your role: {user?.role}</p>
                </div>
            </div>
        );
    }

    return children;
}

export default ProtectedRoute;
