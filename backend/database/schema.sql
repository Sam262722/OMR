-- OMR Evaluation System Database Schema
-- This file contains the complete database schema for Supabase

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Users table (extends Supabase auth.users)
CREATE TABLE public.users (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin', 'teacher')),
    organization TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    preferences JSONB DEFAULT '{}'::jsonb,
    last_login TIMESTAMP WITH TIME ZONE
);

-- OMR Results table
CREATE TABLE public.omr_results (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    filename TEXT NOT NULL,
    original_filename TEXT,
    
    -- Student information extracted from OMR sheet
    student_info JSONB DEFAULT '{}'::jsonb,
    
    -- Processing results
    answers JSONB DEFAULT '{}'::jsonb,
    scores JSONB DEFAULT '{}'::jsonb,
    total_score DECIMAL(5,2) DEFAULT 0,
    max_possible_score DECIMAL(5,2) DEFAULT 100,
    percentage DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE 
            WHEN max_possible_score > 0 THEN (total_score / max_possible_score) * 100
            ELSE 0
        END
    ) STORED,
    
    -- Confidence and quality metrics
    confidence_score DECIMAL(4,3) DEFAULT 0,
    processing_quality TEXT DEFAULT 'good' CHECK (processing_quality IN ('excellent', 'good', 'fair', 'poor')),
    
    -- Processing metadata
    processing_time DECIMAL(8,3) DEFAULT 0,
    template_used TEXT,
    answer_key_version TEXT,
    
    -- File paths and storage
    image_path TEXT,
    result_file_path TEXT,
    
    -- Status and timestamps
    status TEXT DEFAULT 'completed' CHECK (status IN ('processing', 'completed', 'failed', 'review_needed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Additional metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Batch processing reference
    batch_id UUID,
    batch_position INTEGER
);

-- Processing Sessions table (for batch processing tracking)
CREATE TABLE public.processing_sessions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    session_type TEXT DEFAULT 'single' CHECK (session_type IN ('single', 'batch')),
    
    -- Session details
    total_files INTEGER DEFAULT 1,
    processed_files INTEGER DEFAULT 0,
    successful_files INTEGER DEFAULT 0,
    failed_files INTEGER DEFAULT 0,
    
    -- Status tracking
    status TEXT DEFAULT 'processing' CHECK (status IN ('queued', 'processing', 'completed', 'failed', 'cancelled')),
    progress_percentage DECIMAL(5,2) DEFAULT 0,
    
    -- Configuration used
    answer_key JSONB,
    template_config JSONB,
    processing_options JSONB DEFAULT '{}'::jsonb,
    
    -- Timing
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    estimated_completion TIMESTAMP WITH TIME ZONE,
    
    -- Results summary
    average_score DECIMAL(5,2),
    average_confidence DECIMAL(4,3),
    total_processing_time DECIMAL(8,3),
    
    -- Error tracking
    error_message TEXT,
    error_details JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Answer Keys table (for reusable answer key templates)
CREATE TABLE public.answer_keys (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    
    -- Answer key content
    answer_data JSONB NOT NULL,
    subject_config JSONB DEFAULT '{}'::jsonb,
    scoring_rules JSONB DEFAULT '{}'::jsonb,
    
    -- Metadata
    version TEXT DEFAULT '1.0',
    total_questions INTEGER,
    max_score DECIMAL(5,2) DEFAULT 100,
    
    -- Usage tracking
    usage_count INTEGER DEFAULT 0,
    last_used TIMESTAMP WITH TIME ZONE,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_public BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Templates table (for OMR sheet templates)
CREATE TABLE public.omr_templates (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    
    -- Template configuration
    template_config JSONB NOT NULL,
    layout_type TEXT DEFAULT 'standard' CHECK (layout_type IN ('standard', 'custom', 'multi_column')),
    
    -- Dimensions and layout
    page_width INTEGER,
    page_height INTEGER,
    bubble_size INTEGER DEFAULT 20,
    bubble_spacing INTEGER DEFAULT 30,
    
    -- Question configuration
    total_questions INTEGER,
    questions_per_row INTEGER DEFAULT 5,
    answer_options INTEGER DEFAULT 4,
    
    -- Usage and status
    usage_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    is_public BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- System Statistics table (for analytics)
CREATE TABLE public.system_stats (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    date DATE DEFAULT CURRENT_DATE,
    
    -- Processing statistics
    total_sheets_processed INTEGER DEFAULT 0,
    successful_processing INTEGER DEFAULT 0,
    failed_processing INTEGER DEFAULT 0,
    
    -- Performance metrics
    average_processing_time DECIMAL(8,3),
    average_confidence_score DECIMAL(4,3),
    average_accuracy DECIMAL(5,2),
    
    -- User activity
    active_users INTEGER DEFAULT 0,
    new_users INTEGER DEFAULT 0,
    
    -- System health
    system_uptime DECIMAL(8,2),
    error_rate DECIMAL(5,2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(date)
);

-- Create indexes for better performance
CREATE INDEX idx_omr_results_user_id ON public.omr_results(user_id);
CREATE INDEX idx_omr_results_created_at ON public.omr_results(created_at DESC);
CREATE INDEX idx_omr_results_status ON public.omr_results(status);
CREATE INDEX idx_omr_results_batch_id ON public.omr_results(batch_id) WHERE batch_id IS NOT NULL;
CREATE INDEX idx_omr_results_confidence ON public.omr_results(confidence_score DESC);

CREATE INDEX idx_processing_sessions_user_id ON public.processing_sessions(user_id);
CREATE INDEX idx_processing_sessions_status ON public.processing_sessions(status);
CREATE INDEX idx_processing_sessions_created_at ON public.processing_sessions(created_at DESC);

CREATE INDEX idx_answer_keys_user_id ON public.answer_keys(user_id);
CREATE INDEX idx_answer_keys_active ON public.answer_keys(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_answer_keys_public ON public.answer_keys(is_public) WHERE is_public = TRUE;

CREATE INDEX idx_omr_templates_user_id ON public.omr_templates(user_id);
CREATE INDEX idx_omr_templates_active ON public.omr_templates(is_active) WHERE is_active = TRUE;

-- Row Level Security (RLS) Policies

-- Enable RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.omr_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.processing_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.answer_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.omr_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.system_stats ENABLE ROW LEVEL SECURITY;

-- Users table policies
CREATE POLICY "Users can view own profile" ON public.users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Admins can view all users" ON public.users
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- OMR Results table policies
CREATE POLICY "Users can view own results" ON public.omr_results
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own results" ON public.omr_results
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own results" ON public.omr_results
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own results" ON public.omr_results
    FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Admins can view all results" ON public.omr_results
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Processing Sessions table policies
CREATE POLICY "Users can view own sessions" ON public.processing_sessions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own sessions" ON public.processing_sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own sessions" ON public.processing_sessions
    FOR UPDATE USING (auth.uid() = user_id);

-- Answer Keys table policies
CREATE POLICY "Users can view own answer keys" ON public.answer_keys
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can view public answer keys" ON public.answer_keys
    FOR SELECT USING (is_public = TRUE);

CREATE POLICY "Users can insert own answer keys" ON public.answer_keys
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own answer keys" ON public.answer_keys
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own answer keys" ON public.answer_keys
    FOR DELETE USING (auth.uid() = user_id);

-- OMR Templates table policies
CREATE POLICY "Users can view own templates" ON public.omr_templates
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can view public templates" ON public.omr_templates
    FOR SELECT USING (is_public = TRUE);

CREATE POLICY "Users can insert own templates" ON public.omr_templates
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own templates" ON public.omr_templates
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own templates" ON public.omr_templates
    FOR DELETE USING (auth.uid() = user_id);

-- System Stats table policies (admin only)
CREATE POLICY "Only admins can view system stats" ON public.system_stats
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

CREATE POLICY "Only admins can manage system stats" ON public.system_stats
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Functions and Triggers

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to all tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_omr_results_updated_at BEFORE UPDATE ON public.omr_results
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_processing_sessions_updated_at BEFORE UPDATE ON public.processing_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_answer_keys_updated_at BEFORE UPDATE ON public.answer_keys
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_omr_templates_updated_at BEFORE UPDATE ON public.omr_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to handle new user registration
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, email, full_name)
    VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'full_name');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger for new user registration
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Function to calculate processing statistics
CREATE OR REPLACE FUNCTION calculate_user_stats(user_uuid UUID)
RETURNS TABLE (
    total_processed INTEGER,
    average_score DECIMAL(5,2),
    average_confidence DECIMAL(4,3),
    success_rate DECIMAL(5,2),
    total_processing_time DECIMAL(8,3)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INTEGER as total_processed,
        COALESCE(AVG(r.total_score), 0)::DECIMAL(5,2) as average_score,
        COALESCE(AVG(r.confidence_score), 0)::DECIMAL(4,3) as average_confidence,
        COALESCE((COUNT(*) FILTER (WHERE r.status = 'completed')::DECIMAL / NULLIF(COUNT(*), 0)) * 100, 0)::DECIMAL(5,2) as success_rate,
        COALESCE(SUM(r.processing_time), 0)::DECIMAL(8,3) as total_processing_time
    FROM public.omr_results r
    WHERE r.user_id = user_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create views for common queries

-- User dashboard view
CREATE VIEW public.user_dashboard AS
SELECT 
    u.id,
    u.email,
    u.full_name,
    u.organization,
    COUNT(r.id) as total_results,
    COUNT(r.id) FILTER (WHERE r.created_at >= CURRENT_DATE - INTERVAL '30 days') as results_last_30_days,
    COALESCE(AVG(r.total_score), 0) as average_score,
    COALESCE(AVG(r.confidence_score), 0) as average_confidence,
    MAX(r.created_at) as last_processing_date
FROM public.users u
LEFT JOIN public.omr_results r ON u.id = r.user_id
GROUP BY u.id, u.email, u.full_name, u.organization;

-- Recent results view
CREATE VIEW public.recent_results AS
SELECT 
    r.id,
    r.user_id,
    u.full_name as user_name,
    r.filename,
    r.total_score,
    r.confidence_score,
    r.status,
    r.created_at,
    r.processing_time
FROM public.omr_results r
JOIN public.users u ON r.user_id = u.id
ORDER BY r.created_at DESC;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated;

-- Grant read access to views
GRANT SELECT ON public.user_dashboard TO authenticated;
GRANT SELECT ON public.recent_results TO authenticated;