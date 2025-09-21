'use client'

import { useState, useRef } from 'react'
import { useAuth } from '@/lib/auth'
import { 
  CloudArrowUpIcon, 
  DocumentTextIcon, 
  ChartBarIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  EyeIcon,
  TrashIcon,
  ArrowDownTrayIcon
} from '@heroicons/react/24/outline'
import { toast } from 'react-hot-toast'

interface ProcessingJob {
  id: string
  fileName: string
  status: 'pending' | 'processing' | 'completed' | 'error'
  uploadedAt: Date
  completedAt?: Date
  results?: {
    totalQuestions: number
    correctAnswers: number
    score: number
    accuracy: number
  }
  error?: string
}

export default function DashboardPage() {
  const { user, profile, signOut } = useAuth()
  const [jobs, setJobs] = useState<ProcessingJob[]>([
    {
      id: '1',
      fileName: 'exam_sheet_001.pdf',
      status: 'completed',
      uploadedAt: new Date('2024-01-15T10:30:00'),
      completedAt: new Date('2024-01-15T10:32:00'),
      results: {
        totalQuestions: 50,
        correctAnswers: 42,
        score: 84,
        accuracy: 84
      }
    },
    {
      id: '2',
      fileName: 'quiz_batch_a.pdf',
      status: 'processing',
      uploadedAt: new Date('2024-01-15T11:15:00')
    },
    {
      id: '3',
      fileName: 'midterm_sheets.pdf',
      status: 'pending',
      uploadedAt: new Date('2024-01-15T11:45:00')
    }
  ])
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault()
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files)
    }
  }

  const handleFiles = (files: FileList) => {
    Array.from(files).forEach(file => {
      if (file.type === 'application/pdf' || file.type.startsWith('image/')) {
        const newJob: ProcessingJob = {
          id: Date.now().toString(),
          fileName: file.name,
          status: 'pending',
          uploadedAt: new Date()
        }
        setJobs(prev => [newJob, ...prev])
        toast.success(`${file.name} uploaded successfully`)
        
        // Simulate processing
        setTimeout(() => {
          setJobs(prev => prev.map(job => 
            job.id === newJob.id ? { ...job, status: 'processing' } : job
          ))
        }, 1000)
        
        setTimeout(() => {
          setJobs(prev => prev.map(job => 
            job.id === newJob.id ? { 
              ...job, 
              status: 'completed',
              completedAt: new Date(),
              results: {
                totalQuestions: Math.floor(Math.random() * 50) + 10,
                correctAnswers: Math.floor(Math.random() * 40) + 5,
                score: Math.floor(Math.random() * 40) + 60,
                accuracy: Math.floor(Math.random() * 40) + 60
              }
            } : job
          ))
        }, 5000)
      } else {
        toast.error('Please upload PDF or image files only')
      }
    })
  }

  const onButtonClick = () => {
    fileInputRef.current?.click()
  }

  const getStatusIcon = (status: ProcessingJob['status']) => {
    switch (status) {
      case 'pending':
        return <ClockIcon className="h-5 w-5 text-yellow-500" />
      case 'processing':
        return <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500"></div>
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />
      case 'error':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />
    }
  }

  const getStatusText = (status: ProcessingJob['status']) => {
    switch (status) {
      case 'pending':
        return 'Pending'
      case 'processing':
        return 'Processing...'
      case 'completed':
        return 'Completed'
      case 'error':
        return 'Error'
    }
  }

  const completedJobs = jobs.filter(job => job.status === 'completed')
  const totalQuestions = completedJobs.reduce((sum, job) => sum + (job.results?.totalQuestions || 0), 0)
  const totalCorrect = completedJobs.reduce((sum, job) => sum + (job.results?.correctAnswers || 0), 0)
  const averageScore = completedJobs.length > 0 
    ? completedJobs.reduce((sum, job) => sum + (job.results?.score || 0), 0) / completedJobs.length 
    : 0

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                OMR Dashboard
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600 dark:text-gray-300">
                Welcome, {profile?.full_name || user?.email}
              </span>
              <button
                onClick={signOut}
                className="text-sm text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Analytics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center">
              <DocumentTextIcon className="h-8 w-8 text-blue-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Processed</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{completedJobs.length}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center">
              <ChartBarIcon className="h-8 w-8 text-green-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Questions Analyzed</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{totalQuestions}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center">
              <CheckCircleIcon className="h-8 w-8 text-emerald-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Correct Answers</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{totalCorrect}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <div className="flex items-center">
              <ChartBarIcon className="h-8 w-8 text-purple-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Average Score</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{averageScore.toFixed(1)}%</p>
              </div>
            </div>
          </div>
        </div>

        {/* File Upload Area */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow mb-8">
          <div className="p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Upload OMR Sheets</h2>
            <div
              className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                dragActive
                  ? 'border-blue-400 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                <button
                  type="button"
                  className="font-medium text-blue-600 hover:text-blue-500"
                  onClick={onButtonClick}
                >
                  Click to upload
                </button>{' '}
                or drag and drop
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">PDF or image files up to 10MB</p>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,image/*"
                onChange={handleChange}
                className="hidden"
              />
            </div>
          </div>
        </div>

        {/* Processing Jobs */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
          <div className="p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Processing Queue</h2>
            <div className="space-y-4">
              {jobs.length === 0 ? (
                <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                  No files uploaded yet. Upload your first OMR sheet to get started!
                </p>
              ) : (
                jobs.map((job) => (
                  <div
                    key={job.id}
                    className="flex flex-col sm:flex-row sm:items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg space-y-3 sm:space-y-0"
                  >
                    <div className="flex items-center space-x-3 sm:space-x-4 min-w-0 flex-1">
                      {getStatusIcon(job.status)}
                      <div className="min-w-0 flex-1">
                        <p className="font-medium text-gray-900 dark:text-white truncate">{job.fileName}</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          Uploaded {job.uploadedAt.toLocaleString()}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
                      <div className="flex items-center justify-between sm:justify-start space-x-2 sm:space-x-4">
                        <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
                          {getStatusText(job.status)}
                        </span>
                        
                        {job.status === 'completed' && job.results && (
                          <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
                            <span className="hidden sm:inline">Score: {job.results.score}%</span>
                            <span className="sm:hidden">{job.results.score}%</span>
                            <span className="hidden sm:inline">•</span>
                            <span>{job.results.correctAnswers}/{job.results.totalQuestions}</span>
                          </div>
                        )}
                      
                      <div className="flex items-center space-x-1 sm:space-x-2">
                        {job.status === 'completed' && (
                          <>
                            {/* Preview Button */}
                            <button 
                              className="group relative flex items-center justify-center p-2 sm:p-1 text-gray-400 hover:text-blue-500 transition-colors duration-200 rounded-md hover:bg-blue-50 dark:hover:bg-blue-900/20"
                              title="Preview Results"
                            >
                              <EyeIcon className="h-4 w-4 sm:h-4 sm:w-4" />
                              <span className="sr-only sm:not-sr-only sm:ml-1 text-xs hidden sm:inline">Preview</span>
                              {/* Tooltip for mobile */}
                              <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 text-xs text-white bg-gray-900 rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none sm:hidden">
                                Preview
                              </div>
                            </button>
                            
                            {/* Download Button */}
                            <button 
                              className="group relative flex items-center justify-center p-2 sm:p-1 text-gray-400 hover:text-green-500 transition-colors duration-200 rounded-md hover:bg-green-50 dark:hover:bg-green-900/20"
                              title="Download Results"
                            >
                              <ArrowDownTrayIcon className="h-4 w-4 sm:h-4 sm:w-4" />
                              <span className="sr-only sm:not-sr-only sm:ml-1 text-xs hidden sm:inline">Download</span>
                              {/* Tooltip for mobile */}
                              <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 text-xs text-white bg-gray-900 rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none sm:hidden">
                                Download
                              </div>
                            </button>
                          </>
                        )}
                        
                        {/* Delete Button */}
                        <button 
                          className="group relative flex items-center justify-center p-2 sm:p-1 text-gray-400 hover:text-red-500 transition-colors duration-200 rounded-md hover:bg-red-50 dark:hover:bg-red-900/20"
                          title="Delete File"
                        >
                          <TrashIcon className="h-4 w-4 sm:h-4 sm:w-4" />
                          <span className="sr-only sm:not-sr-only sm:ml-1 text-xs hidden sm:inline">Delete</span>
                          {/* Tooltip for mobile */}
                          <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 text-xs text-white bg-gray-900 rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none sm:hidden">
                            Delete
                          </div>
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}