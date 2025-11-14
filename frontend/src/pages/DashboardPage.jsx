import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getCandidates } from '../services/api'
import StatusIndicator from '../components/StatusIndicator'
import './DashboardPage.css'

const DashboardPage = () => {
  const [candidates, setCandidates] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  const fetchCandidates = async () => {
    try {
      const data = await getCandidates()
      setCandidates(data)
      setError(null)
    } catch (err) {
      setError(err.message || 'Failed to fetch candidates')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCandidates()
    
    // Auto-refresh every 2.5 seconds
    const interval = setInterval(fetchCandidates, 2500)
    
    return () => clearInterval(interval)
  }, [])

  const handleViewResult = (candidateId) => {
    navigate(`/candidate/${candidateId}`)
  }

  const getStatusCounts = () => {
    const counts = {
      PENDING: 0,
      PROCESSING: 0,
      DONE: 0,
      FAILED: 0
    }
    candidates.forEach(c => {
      counts[c.status] = (counts[c.status] || 0) + 1
    })
    return counts
  }

  const statusCounts = getStatusCounts()

  if (loading) {
    return <div className="dashboard-page loading">Loading...</div>
  }

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <h1>Candidate Dashboard</h1>
        <div className="status-summary">
          <div className="status-summary-item">
            <span className="status-label">Pending:</span>
            <span className="status-count">{statusCounts.PENDING}</span>
          </div>
          <div className="status-summary-item">
            <span className="status-label">Processing:</span>
            <span className="status-count">{statusCounts.PROCESSING}</span>
          </div>
          <div className="status-summary-item">
            <span className="status-label">Done:</span>
            <span className="status-count">{statusCounts.DONE}</span>
          </div>
          <div className="status-summary-item">
            <span className="status-label">Failed:</span>
            <span className="status-count">{statusCounts.FAILED}</span>
          </div>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      {candidates.length === 0 ? (
        <div className="empty-state">
          <p>No candidates yet. Upload resumes to get started.</p>
        </div>
      ) : (
        <div className="candidates-table">
          <table>
            <thead>
              <tr>
                <th>Filename</th>
                <th>Status</th>
                <th>Fit Score</th>
                <th>Recommendation</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {candidates.map((candidate) => (
                <tr key={candidate.id}>
                  <td>{candidate.original_filename}</td>
                  <td>
                    <StatusIndicator status={candidate.status} />
                  </td>
                  <td>
                    {candidate.fit_score !== null && candidate.fit_score !== undefined
                      ? candidate.fit_score.toFixed(1)
                      : '-'}
                  </td>
                  <td>{candidate.recommendation || '-'}</td>
                  <td>{new Date(candidate.created_at).toLocaleString()}</td>
                  <td>
                    <button
                      className="view-btn"
                      onClick={() => handleViewResult(candidate.id)}
                      disabled={candidate.status === 'PENDING' || candidate.status === 'PROCESSING'}
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default DashboardPage

