import React from 'react'
import './StatusIndicator.css'

const StatusIndicator = ({ status }) => {
  const getStatusClass = (status) => {
    switch (status) {
      case 'PENDING':
        return 'status-pending'
      case 'PROCESSING':
        return 'status-processing'
      case 'DONE':
        return 'status-done'
      case 'FAILED':
        return 'status-failed'
      default:
        return 'status-unknown'
    }
  }

  const getStatusLabel = (status) => {
    switch (status) {
      case 'PENDING':
        return 'Pending'
      case 'PROCESSING':
        return 'Processing'
      case 'DONE':
        return 'Done'
      case 'FAILED':
        return 'Failed'
      default:
        return status
    }
  }

  return (
    <span className={`status-indicator ${getStatusClass(status)}`}>
      {getStatusLabel(status)}
    </span>
  )
}

export default StatusIndicator

