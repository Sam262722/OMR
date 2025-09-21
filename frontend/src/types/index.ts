// Re-export database types
export * from './database'

// API Response types
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  limit: number
  totalPages: number
}

// File upload types
export interface FileUploadProgress {
  file: File
  progress: number
  status: 'pending' | 'uploading' | 'completed' | 'error'
  error?: string
  result?: any
}

export interface UploadedFile {
  id: string
  filename: string
  originalName: string
  size: number
  mimeType: string
  url: string
  uploadedAt: string
}

// OMR Processing types
export interface OMRProcessingConfig {
  template_id?: string
  answer_key_id?: string
  confidence_threshold: number
  auto_review: boolean
  batch_size: number
  quality_threshold: 'excellent' | 'good' | 'fair' | 'poor'
  enable_manual_review: boolean
  processing_options: {
    enhance_image: boolean
    auto_rotate: boolean
    noise_reduction: boolean
    contrast_adjustment: boolean
  }
}

export interface StudentInfo {
  student_id?: string
  name?: string
  class?: string
  section?: string
  roll_number?: string
  exam_date?: string
  subject?: string
  [key: string]: any
}

export interface DetectedAnswer {
  question_number: number
  selected_option: string | string[]
  confidence: number
  coordinates?: {
    x: number
    y: number
    width: number
    height: number
  }
}

export interface ScoringDetails {
  correct_answers: number
  incorrect_answers: number
  unanswered: number
  partial_credit: number
  bonus_points: number
  penalty_points: number
  question_wise_scores: {
    question_number: number
    is_correct: boolean
    points_awarded: number
    max_points: number
    selected_answer: string | string[]
    correct_answer: string | string[]
  }[]
}

// Dashboard types
export interface DashboardStats {
  total_results: number
  total_sessions: number
  average_score: number
  average_confidence: number
  recent_activity: RecentActivity[]
  processing_trends: ProcessingTrend[]
  quality_distribution: QualityDistribution
}

export interface RecentActivity {
  id: string
  type: 'processing' | 'review' | 'upload' | 'template_created' | 'answer_key_created'
  title: string
  description: string
  timestamp: string
  status: 'success' | 'warning' | 'error' | 'info'
  metadata?: any
}

export interface ProcessingTrend {
  date: string
  total_processed: number
  success_rate: number
  average_score: number
  average_confidence: number
}

export interface QualityDistribution {
  excellent: number
  good: number
  fair: number
  poor: number
  failed: number
}

// Template types
export interface TemplateLayout {
  type: 'grid' | 'column' | 'custom'
  page_width: number
  page_height: number
  margins: {
    top: number
    right: number
    bottom: number
    left: number
  }
  bubble_config: {
    size: number
    spacing: number
    shape: 'circle' | 'square' | 'oval'
  }
  question_areas: QuestionArea[]
  student_info_area?: StudentInfoArea
}

export interface QuestionArea {
  id: string
  start_question: number
  end_question: number
  position: {
    x: number
    y: number
    width: number
    height: number
  }
  layout: {
    rows: number
    columns: number
    options_per_question: number
    direction: 'horizontal' | 'vertical'
  }
}

export interface StudentInfoArea {
  position: {
    x: number
    y: number
    width: number
    height: number
  }
  fields: {
    name: boolean
    id: boolean
    class: boolean
    section: boolean
    roll_number: boolean
    custom_fields: string[]
  }
}

// Answer Key types
export interface AnswerKeyData {
  questions: {
    [question_number: string]: {
      correct_answer: string | string[]
      points: number
      type: 'single' | 'multiple' | 'numerical'
      explanation?: string
    }
  }
  metadata: {
    subject: string
    exam_type: string
    duration?: number
    instructions?: string
    negative_marking?: boolean
    negative_points?: number
  }
}

// Form types
export interface FormField {
  name: string
  label: string
  type: 'text' | 'email' | 'password' | 'number' | 'select' | 'textarea' | 'file' | 'checkbox' | 'radio'
  required?: boolean
  placeholder?: string
  options?: { value: string; label: string }[]
  validation?: {
    min?: number
    max?: number
    pattern?: string
    message?: string
  }
}

// Navigation types
export interface NavItem {
  name: string
  href: string
  icon?: React.ComponentType<any>
  current?: boolean
  children?: NavItem[]
  badge?: string | number
  disabled?: boolean
}

// Theme types
export interface ThemeConfig {
  mode: 'light' | 'dark' | 'system'
  primary_color: string
  accent_color: string
  font_size: 'small' | 'medium' | 'large'
  compact_mode: boolean
  animations: boolean
}

// Notification types
export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
  timestamp: string
  read: boolean
  actions?: NotificationAction[]
}

export interface NotificationAction {
  label: string
  action: () => void
  style?: 'primary' | 'secondary' | 'danger'
}

// Search and Filter types
export interface SearchFilters {
  query?: string
  date_from?: string
  date_to?: string
  status?: string[]
  quality?: string[]
  score_range?: {
    min: number
    max: number
  }
  confidence_range?: {
    min: number
    max: number
  }
  tags?: string[]
  user_id?: string
  session_id?: string
  answer_key_id?: string
  template_id?: string
}

export interface SortOption {
  field: string
  direction: 'asc' | 'desc'
  label: string
}

// Export/Import types
export interface ExportOptions {
  format: 'csv' | 'xlsx' | 'pdf' | 'json'
  include_images: boolean
  include_metadata: boolean
  fields: string[]
  filters?: SearchFilters
}

export interface ImportResult {
  total_records: number
  successful_imports: number
  failed_imports: number
  errors: ImportError[]
  warnings: ImportWarning[]
}

export interface ImportError {
  row: number
  field?: string
  message: string
  data?: any
}

export interface ImportWarning {
  row: number
  field?: string
  message: string
  data?: any
}

// Utility types
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>
export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>

// Component prop types
export interface BaseComponentProps {
  className?: string
  children?: React.ReactNode
}

export interface LoadingState {
  isLoading: boolean
  error?: string | null
  data?: any
}

export interface PaginationProps {
  currentPage: number
  totalPages: number
  onPageChange: (page: number) => void
  showFirstLast?: boolean
  showPrevNext?: boolean
  maxVisiblePages?: number
}