export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  public: {
    Tables: {
      users: {
        Row: {
          id: string
          email: string
          full_name: string | null
          role: 'teacher' | 'admin' | 'super_admin'
          institution: string | null
          department: string | null
          phone: string | null
          avatar_url: string | null
          preferences: Json
          subscription_tier: string
          subscription_expires_at: string | null
          is_active: boolean
          last_login: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id: string
          email: string
          full_name?: string | null
          role?: 'teacher' | 'admin' | 'super_admin'
          institution?: string | null
          department?: string | null
          phone?: string | null
          avatar_url?: string | null
          preferences?: Json
          subscription_tier?: string
          subscription_expires_at?: string | null
          is_active?: boolean
          last_login?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          email?: string
          full_name?: string | null
          role?: 'teacher' | 'admin' | 'super_admin'
          institution?: string | null
          department?: string | null
          phone?: string | null
          avatar_url?: string | null
          preferences?: Json
          subscription_tier?: string
          subscription_expires_at?: string | null
          is_active?: boolean
          last_login?: string | null
          created_at?: string
          updated_at?: string
        }
        Relationships: []
      }
      answer_keys: {
        Row: {
          id: string
          user_id: string
          name: string
          description: string | null
          answer_data: Json
          subject_config: Json
          scoring_rules: Json
          total_questions: number
          max_score: number
          usage_count: number
          is_public: boolean
          is_active: boolean
          last_used: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          name: string
          description?: string | null
          answer_data: Json
          subject_config?: Json
          scoring_rules?: Json
          total_questions: number
          max_score: number
          usage_count?: number
          is_public?: boolean
          is_active?: boolean
          last_used?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          name?: string
          description?: string | null
          answer_data?: Json
          subject_config?: Json
          scoring_rules?: Json
          total_questions?: number
          max_score?: number
          usage_count?: number
          is_public?: boolean
          is_active?: boolean
          last_used?: string | null
          created_at?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "answer_keys_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          }
        ]
      }
      omr_templates: {
        Row: {
          id: string
          user_id: string
          name: string
          description: string | null
          template_config: Json
          layout_type: string
          page_width: number
          page_height: number
          bubble_size: number
          bubble_spacing: number
          total_questions: number
          questions_per_row: number
          answer_options: number
          usage_count: number
          is_public: boolean
          is_active: boolean
          last_used: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          name: string
          description?: string | null
          template_config: Json
          layout_type?: string
          page_width: number
          page_height: number
          bubble_size: number
          bubble_spacing: number
          total_questions: number
          questions_per_row?: number
          answer_options?: number
          usage_count?: number
          is_public?: boolean
          is_active?: boolean
          last_used?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          name?: string
          description?: string | null
          template_config?: Json
          layout_type?: string
          page_width?: number
          page_height?: number
          bubble_size?: number
          bubble_spacing?: number
          total_questions?: number
          questions_per_row?: number
          answer_options?: number
          usage_count?: number
          is_public?: boolean
          is_active?: boolean
          last_used?: string | null
          created_at?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "omr_templates_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          }
        ]
      }
      processing_sessions: {
        Row: {
          id: string
          user_id: string
          session_name: string
          answer_key_id: string | null
          template_id: string | null
          total_files: number
          processed_files: number
          successful_files: number
          failed_files: number
          progress_percentage: number
          status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
          processing_config: Json
          error_summary: Json
          started_at: string | null
          completed_at: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          session_name: string
          answer_key_id?: string | null
          template_id?: string | null
          total_files?: number
          processed_files?: number
          successful_files?: number
          failed_files?: number
          progress_percentage?: number
          status?: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
          processing_config?: Json
          error_summary?: Json
          started_at?: string | null
          completed_at?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          session_name?: string
          answer_key_id?: string | null
          template_id?: string | null
          total_files?: number
          processed_files?: number
          successful_files?: number
          failed_files?: number
          progress_percentage?: number
          status?: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
          processing_config?: Json
          error_summary?: Json
          started_at?: string | null
          completed_at?: string | null
          created_at?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "processing_sessions_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "processing_sessions_answer_key_id_fkey"
            columns: ["answer_key_id"]
            isOneToOne: false
            referencedRelation: "answer_keys"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "processing_sessions_template_id_fkey"
            columns: ["template_id"]
            isOneToOne: false
            referencedRelation: "omr_templates"
            referencedColumns: ["id"]
          }
        ]
      }
      omr_results: {
        Row: {
          id: string
          user_id: string
          session_id: string | null
          answer_key_id: string | null
          template_id: string | null
          filename: string
          original_filename: string
          file_path: string
          file_size: number | null
          student_info: Json
          detected_answers: Json
          correct_answers: Json | null
          scoring_details: Json
          total_score: number
          max_possible_score: number
          percentage: number
          confidence_score: number
          processing_quality: 'excellent' | 'good' | 'fair' | 'poor' | 'failed'
          processing_time: number | null
          status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
          error_details: Json
          review_notes: string | null
          is_reviewed: boolean
          reviewed_by: string | null
          reviewed_at: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          user_id: string
          session_id?: string | null
          answer_key_id?: string | null
          template_id?: string | null
          filename: string
          original_filename: string
          file_path: string
          file_size?: number | null
          student_info?: Json
          detected_answers: Json
          correct_answers?: Json | null
          scoring_details?: Json
          total_score?: number
          max_possible_score?: number
          confidence_score?: number
          processing_quality?: 'excellent' | 'good' | 'fair' | 'poor' | 'failed'
          processing_time?: number | null
          status?: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
          error_details?: Json
          review_notes?: string | null
          is_reviewed?: boolean
          reviewed_by?: string | null
          reviewed_at?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          user_id?: string
          session_id?: string | null
          answer_key_id?: string | null
          template_id?: string | null
          filename?: string
          original_filename?: string
          file_path?: string
          file_size?: number | null
          student_info?: Json
          detected_answers?: Json
          correct_answers?: Json | null
          scoring_details?: Json
          total_score?: number
          max_possible_score?: number
          confidence_score?: number
          processing_quality?: 'excellent' | 'good' | 'fair' | 'poor' | 'failed'
          processing_time?: number | null
          status?: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
          error_details?: Json
          review_notes?: string | null
          is_reviewed?: boolean
          reviewed_by?: string | null
          reviewed_at?: string | null
          created_at?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "omr_results_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "omr_results_session_id_fkey"
            columns: ["session_id"]
            isOneToOne: false
            referencedRelation: "processing_sessions"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "omr_results_answer_key_id_fkey"
            columns: ["answer_key_id"]
            isOneToOne: false
            referencedRelation: "answer_keys"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "omr_results_template_id_fkey"
            columns: ["template_id"]
            isOneToOne: false
            referencedRelation: "omr_templates"
            referencedColumns: ["id"]
          }
        ]
      }
      system_stats: {
        Row: {
          id: string
          date: string
          total_sheets_processed: number
          successful_processing: number
          failed_processing: number
          average_processing_time: number
          average_confidence_score: number
          average_accuracy: number
          active_users: number
          new_users: number
          system_uptime: number
          error_rate: number
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          date: string
          total_sheets_processed?: number
          successful_processing?: number
          failed_processing?: number
          average_processing_time?: number
          average_confidence_score?: number
          average_accuracy?: number
          active_users?: number
          new_users?: number
          system_uptime?: number
          error_rate?: number
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          date?: string
          total_sheets_processed?: number
          successful_processing?: number
          failed_processing?: number
          average_processing_time?: number
          average_confidence_score?: number
          average_accuracy?: number
          active_users?: number
          new_users?: number
          system_uptime?: number
          error_rate?: number
          created_at?: string
          updated_at?: string
        }
        Relationships: []
      }
    }
    Views: {
      user_dashboard_stats: {
        Row: {
          user_id: string | null
          full_name: string | null
          total_results: number | null
          total_sessions: number | null
          average_score: number | null
          average_confidence: number | null
          created_answer_keys: number | null
          created_templates: number | null
          last_processing_date: string | null
        }
        Relationships: []
      }
      recent_processing_activity: {
        Row: {
          id: string | null
          filename: string | null
          total_score: number | null
          percentage: number | null
          confidence_score: number | null
          processing_quality: 'excellent' | 'good' | 'fair' | 'poor' | 'failed' | null
          status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled' | null
          created_at: string | null
          user_name: string | null
          answer_key_name: string | null
          session_name: string | null
        }
        Relationships: []
      }
    }
    Functions: {
      get_user_recent_results: {
        Args: {
          user_uuid: string
          limit_count?: number
        }
        Returns: {
          id: string
          filename: string
          total_score: number
          percentage: number
          confidence_score: number
          status: string
          created_at: string
        }[]
      }
      get_public_answer_keys: {
        Args: Record<PropertyKey, never>
        Returns: {
          id: string
          name: string
          description: string
          total_questions: number
          max_score: number
          usage_count: number
        }[]
      }
    }
    Enums: {
      processing_status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled'
      user_role: 'teacher' | 'admin' | 'super_admin'
      processing_quality: 'excellent' | 'good' | 'fair' | 'poor' | 'failed'
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

// Type helpers for easier usage
export type User = Database['public']['Tables']['users']['Row']
export type UserInsert = Database['public']['Tables']['users']['Insert']
export type UserUpdate = Database['public']['Tables']['users']['Update']

export type AnswerKey = Database['public']['Tables']['answer_keys']['Row']
export type AnswerKeyInsert = Database['public']['Tables']['answer_keys']['Insert']
export type AnswerKeyUpdate = Database['public']['Tables']['answer_keys']['Update']

export type OMRTemplate = Database['public']['Tables']['omr_templates']['Row']
export type OMRTemplateInsert = Database['public']['Tables']['omr_templates']['Insert']
export type OMRTemplateUpdate = Database['public']['Tables']['omr_templates']['Update']

export type ProcessingSession = Database['public']['Tables']['processing_sessions']['Row']
export type ProcessingSessionInsert = Database['public']['Tables']['processing_sessions']['Insert']
export type ProcessingSessionUpdate = Database['public']['Tables']['processing_sessions']['Update']

export type OMRResult = Database['public']['Tables']['omr_results']['Row']
export type OMRResultInsert = Database['public']['Tables']['omr_results']['Insert']
export type OMRResultUpdate = Database['public']['Tables']['omr_results']['Update']

export type SystemStats = Database['public']['Tables']['system_stats']['Row']

export type UserDashboardStats = Database['public']['Views']['user_dashboard_stats']['Row']
export type RecentProcessingActivity = Database['public']['Views']['recent_processing_activity']['Row']

export type UserRole = Database['public']['Enums']['user_role']
export type ProcessingStatus = Database['public']['Enums']['processing_status']
export type ProcessingQuality = Database['public']['Enums']['processing_quality']