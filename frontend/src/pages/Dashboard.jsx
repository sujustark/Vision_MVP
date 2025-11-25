import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../index.css';

function Dashboard() {
    const { user, logout, isStudio } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <div className="container">
            <div className="card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                    <div>
                        <h1>Welcome, {user?.full_name}!</h1>
                        <p className="subtitle">
                            Role: <strong>{user?.role === 'studio' ? 'Studio' : 'Customer'}</strong>
                        </p>
                    </div>
                    <button onClick={handleLogout} className="btn-secondary">
                        Logout
                    </button>
                </div>

                {isStudio ? (
                    <div>
                        <h2>Studio Dashboard</h2>
                        <p>Manage your events and photos here.</p>
                        <div style={{ marginTop: '2rem' }}>
                            <button
                                onClick={() => navigate('/studio')}
                                className="btn-primary"
                            >
                                Go to Studio Portal
                            </button>
                        </div>
                    </div>
                ) : (
                    <div>
                        <h2>Customer Dashboard</h2>
                        <p>Find your photos from events you attended.</p>
                        <div style={{ marginTop: '2rem' }}>
                            <button
                                onClick={() => navigate('/user')}
                                className="btn-primary"
                            >
                                Find My Photos
                            </button>
                        </div>
                    </div>
                )}

                <div style={{ marginTop: '3rem', padding: '1.5rem', background: '#f5f5f5', borderRadius: '8px' }}>
                    <h3>Account Information</h3>
                    <p><strong>Email:</strong> {user?.email}</p>
                    <p><strong>User ID:</strong> {user?.user_id}</p>
                    <p><strong>Account Status:</strong> {user?.is_active ? 'Active' : 'Inactive'}</p>
                </div>
            </div>
        </div>
    );
}

export default Dashboard;
