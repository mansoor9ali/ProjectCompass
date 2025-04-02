import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';

// Layout components
import Navbar from './components/layout/Navbar';
import Sidebar from './components/layout/Sidebar';

// Pages
import Dashboard from './pages/Dashboard';
import Inquiries from './pages/Inquiries';
import SubmitInquiry from './pages/SubmitInquiry';
import Departments from './pages/Departments';
import Categories from './pages/Categories';

const App: React.FC = () => {
  return (
    <Router>
      <div className="app-container">
        <Navbar />
        <div className="content-container">
          <Sidebar />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/inquiries" element={<Inquiries />} />
              <Route path="/submit" element={<SubmitInquiry />} />
              <Route path="/departments" element={<Departments />} />
              <Route path="/categories" element={<Categories />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
