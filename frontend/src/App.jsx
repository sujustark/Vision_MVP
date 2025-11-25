import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import Studio from './pages/Studio';
import User from './pages/User';
import './index.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="app-wrapper">
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />

            {/* Protected routes */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />

            <Route
              path="/studio"
              element={
                <ProtectedRoute requireRole="studio">
                  <Studio />
                </ProtectedRoute>
              }
            />

            {/* User page - accessible without auth for QR code scans */}
            <Route path="/user" element={<User />} />
            <Route path="/e/:eventCode/:token" element={<User />} />

            {/* Default route */}
            <Route
              path="/"
              element={
                <div className="landing">
                  <h1>Vision MVP</h1>
                  <p>Find your event photos with AI-powered face recognition</p>
                  <div style={{ marginTop: '2rem' }}>
                    <a href="/login" style={{ marginRight: '1rem' }}>
                      <button className="btn-primary">Login</button>
                    </a>
                    <a href="/signup">
                      <button className="btn-secondary">Sign Up</button>
                    </a>
                  </div>
                </div>
              }
            />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
