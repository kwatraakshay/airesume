import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { uploadResumes, getJobDescription } from '../services/api'
import './UploadPage.css'

const UploadPage = () => {
  const [files, setFiles] = useState([])
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [jobDescription, setJobDescription] = useState('')
  const [showJD, setShowJD] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    // Fetch job description on component mount
    getJobDescription()
      .then(data => setJobDescription(data.job_description))
      .catch(err => console.error('Failed to load job description:', err))
  }, [])

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files)
    
    // Validate file count
    if (selectedFiles.length > 10) {
      setError('Maximum 10 files allowed')
      return
    }
    
    // Validate file types
    const invalidFiles = selectedFiles.filter(file => !file.name.toLowerCase().endsWith('.pdf'))
    if (invalidFiles.length > 0) {
      setError('Only PDF files are allowed')
      return
    }
    
    setFiles(selectedFiles)
    setError(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (files.length === 0) {
      setError('Please select at least one PDF file')
      return
    }
    
    setUploading(true)
    setError(null)
    setSuccess(null)
    
    try {
      const result = await uploadResumes(files)
      setSuccess(`Successfully uploaded ${result.candidates.length} resume(s)`)
      setFiles([])
      
      // Navigate to dashboard after a short delay
      setTimeout(() => {
        navigate('/dashboard')
      }, 2000)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index))
  }

  return (
    <div className="upload-page">
      <div className="upload-container">
        <h1>Upload Resumes</h1>
        <p className="upload-description">
          Upload 1-10 PDF resume files for AI evaluation
        </p>
        
        {jobDescription && (
          <div className="job-description-panel">
            <button
              type="button"
              className="jd-toggle-btn"
              onClick={() => setShowJD(!showJD)}
            >
              {showJD ? '▼' : '▶'} Job Description
            </button>
            {showJD && (
              <div className="jd-content">
                <pre>{jobDescription}</pre>
              </div>
            )}
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="upload-form">
          <div className="file-input-wrapper">
            <input
              type="file"
              id="file-input"
              multiple
              accept=".pdf"
              onChange={handleFileChange}
              className="file-input"
              disabled={uploading}
            />
            <label htmlFor="file-input" className="file-input-label">
              {files.length > 0
                ? `${files.length} file(s) selected`
                : 'Choose PDF files...'}
            </label>
          </div>
          
          {files.length > 0 && (
            <div className="file-list">
              <h3>Selected Files:</h3>
              <ul>
                {files.map((file, index) => (
                  <li key={index} className="file-item">
                    <span>{file.name}</span>
                    <button
                      type="button"
                      onClick={() => removeFile(index)}
                      className="remove-file-btn"
                      disabled={uploading}
                    >
                      ×
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}
          
          <button
            type="submit"
            className="submit-btn"
            disabled={uploading || files.length === 0}
          >
            {uploading ? 'Uploading...' : 'Upload & Process'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default UploadPage

