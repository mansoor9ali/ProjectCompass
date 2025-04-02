import React from 'react';
import { NavLink } from 'react-router-dom';
import { FaHome, FaInbox, FaFileAlt, FaUsers, FaChartPie } from 'react-icons/fa';
import './Layout.css';

const Sidebar: React.FC = () => {
  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h5>Navigation</h5>
      </div>
      <div className="sidebar-menu">
        <NavLink to="/" className={({ isActive }) => 
          isActive ? 'sidebar-link active' : 'sidebar-link'
        }>
          <FaHome className="icon" /> Dashboard
        </NavLink>
        <NavLink to="/inquiries" className={({ isActive }) => 
          isActive ? 'sidebar-link active' : 'sidebar-link'
        }>
          <FaInbox className="icon" /> Inquiries
        </NavLink>
        <NavLink to="/submit" className={({ isActive }) => 
          isActive ? 'sidebar-link active' : 'sidebar-link'
        }>
          <FaFileAlt className="icon" /> Submit Inquiry
        </NavLink>
        <NavLink to="/departments" className={({ isActive }) => 
          isActive ? 'sidebar-link active' : 'sidebar-link'
        }>
          <FaUsers className="icon" /> Departments
        </NavLink>
        <NavLink to="/categories" className={({ isActive }) => 
          isActive ? 'sidebar-link active' : 'sidebar-link'
        }>
          <FaChartPie className="icon" /> Categories
        </NavLink>
      </div>
    </div>
  );
};

export default Sidebar;
