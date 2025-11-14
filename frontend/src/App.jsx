import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import UploadPage from './pages/UploadPage'
import DashboardPage from './pages/DashboardPage'
import ResultPage from './pages/ResultPage'
import './App.css'

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="nav-container">
            <Link to="/" className="nav-logo">
              Resume AI
            </Link>
            <div className="nav-links">
              <Link to="/">Upload</Link>
              <Link to="/dashboard">Dashboard</Link>
            </div>
          </div>
        </nav>
        
        <main className="main-content">
          <Routes>
            <Route path="/" element={<UploadPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/candidate/:id" element={<ResultPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App

