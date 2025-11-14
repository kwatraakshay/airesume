import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const uploadResumes = async (files) => {
  const formData = new FormData()
  files.forEach((file) => {
    formData.append('files', file)
  })
  
  const response = await api.post('/api/candidates/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const getCandidates = async () => {
  const response = await api.get('/api/candidates')
  return response.data
}

export const getCandidateStatus = async (candidateId) => {
  const response = await api.get(`/api/candidates/${candidateId}/status`)
  return response.data
}

export const getCandidateResult = async (candidateId) => {
  const response = await api.get(`/api/candidates/${candidateId}/result`)
  return response.data
}

export const reEvaluateCandidate = async (candidateId) => {
  const response = await api.post(`/api/candidates/${candidateId}/re-evaluate`)
  return response.data
}

export const getJobDescription = async () => {
  const response = await api.get('/api/job-description')
  return response.data
}

export default api

