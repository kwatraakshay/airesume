import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getCandidateResult } from '../services/api'
import StatusIndicator from '../components/StatusIndicator'
import './ResultPage.css'

const ResultPage = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchResult = async () => {
      try {
        const data = await getCandidateResult(id)
        setResult(data)
        setError(null)
      } catch (err) {
        setError(err.message || 'Failed to fetch candidate result')
      } finally {
        setLoading(false)
      }
    }

    fetchResult()
    
    // Poll for updates if still processing
    const interval = setInterval(() => {
      if (result && (result.status === 'PENDING' || result.status === 'PROCESSING')) {
        fetchResult()
      }
    }, 2000)
    
    return () => clearInterval(interval)
  }, [id, result?.status])

  if (loading) {
    return <div className="result-page loading">Loading...</div>
  }

  if (error) {
    return (
      <div className="result-page">
        <div className="error-message">{error}</div>
        <button onClick={() => navigate('/dashboard')} className="back-btn">
          Back to Dashboard
        </button>
      </div>
    )
  }

  if (!result) {
    return <div className="result-page">Candidate not found</div>
  }

  return (
    <div className="result-page">
      <div className="result-header">
        <button onClick={() => navigate('/dashboard')} className="back-btn">
          ← Back to Dashboard
        </button>
        <h1>Candidate Evaluation Result</h1>
        <StatusIndicator status={result.status} />
      </div>

      {result.status === 'PENDING' || result.status === 'PROCESSING' ? (
        <div className="processing-message">
          <p>Processing candidate resume. This may take a few minutes...</p>
          <div className="spinner"></div>
        </div>
      ) : result.status === 'FAILED' ? (
        <div className="error-message">
          <h2>Processing Failed</h2>
          <p>There was an error processing this candidate's resume.</p>
        </div>
      ) : (
        <div className="result-content">
          <div className="result-summary">
            <div className="summary-card">
              <h2>Fit Score</h2>
              <div className="fit-score">
                {result.fit_score !== null && result.fit_score !== undefined
                  ? result.fit_score.toFixed(1)
                  : 'N/A'}
                <span className="score-out-of">/ 10</span>
              </div>
            </div>
            
            <div className="summary-card">
              <h2>Recommendation</h2>
              <div className={`recommendation ${result.recommendation?.toLowerCase()}`}>
                {result.recommendation || 'N/A'}
              </div>
            </div>
          </div>

          {result.summary_text && (
            <div className="result-section">
              <h2>AI Summary</h2>
              <div className="summary-text">
                {result.summary_text.split('\n').map((paragraph, index) => (
                  <p key={index}>{paragraph}</p>
                ))}
              </div>
            </div>
          )}

          {result.structured_data && (
            <div className="result-section">
              <h2>Extracted Information</h2>
              <div className="structured-data">
                <div className="data-item">
                  <strong>Name:</strong> {result.structured_data.name || 'N/A'}
                </div>
                <div className="data-item">
                  <strong>Email:</strong> {result.structured_data.email || 'N/A'}
                </div>
                <div className="data-item">
                  <strong>Phone:</strong> {result.structured_data.phone || 'N/A'}
                </div>
                {result.structured_data.skills && result.structured_data.skills.length > 0 && (
                  <div className="data-item">
                    <strong>Skills:</strong>
                    <div className="skills-list">
                      {result.structured_data.skills.map((skill, index) => (
                        <span key={index} className="skill-tag">{skill}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {result.raw_text && (
            <div className="result-section">
              <h2>Extracted Text</h2>
              <div className="raw-text">
                <pre>{result.raw_text}</pre>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ResultPage

