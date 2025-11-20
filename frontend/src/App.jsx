import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Studio from './pages/Studio';
import User from './pages/User';
import './index.css';

function App() {
  return (
    <Router>
      <div className="app-wrapper">
        <Routes>
          <Route path="/studio" element={<Studio />} />
          <Route path="/user" element={<User />} />
          <Route path="/e/:eventCode/:token" element={<User />} />
          <Route path="/" element={<div className="landing"><h1>Vision MVP</h1><p>Go to <a href="/studio">/studio</a> to start.</p></div>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
