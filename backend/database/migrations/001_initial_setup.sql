-- Migration: 001_initial_setup.sql
-- Description: Initial database setup for OMR Evaluation System
-- Created: 2024-01-01
-- Author: OMR System

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create custom types
DO $$ BEGIN
    CREATE TYPE processing_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('teacher', 'admin', 'super_admin');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE processing_quality AS ENUM ('excellent', 'good', 'fair', 'poor', 'failed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    role user_role DEFAULT 'teacher',
    institution TEXT,
    department TEXT,
    phone TEXT,
    avatar_url TEXT,
    preferences JSONB DEFAULT '{}',
    subscription_tier TEXT DEFAULT 'free',
    subscription_expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create answer_keys table
CREATE TABLE IF NOT EXISTS public.answer_keys (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    answer_data JSONB NOT NULL,
    subject_config JSONB DEFAULT '{}',
    scoring_rules JSONB DEFAULT '{}',
    total_questions INTEGER NOT NULL CHECK (total_questions > 0),
    max_score DECIMAL(5,2) NOT NULL CHECK (max_score > 0),
    usage_count INTEGER DEFAULT 0,
    is_public BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    last_used TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create omr_templates table
CREATE TABLE IF NOT EXISTS public.omr_templates (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    template_config JSONB NOT NULL,
    layout_type TEXT NOT NULL DEFAULT 'standard',
    page_width INTEGER NOT NULL CHECK (page_width > 0),
    page_height INTEGER NOT NULL CHECK (page_height > 0),
    bubble_size INTEGER NOT NULL CHECK (bubble_size > 0),
    bubble_spacing INTEGER NOT NULL CHECK (bubble_spacing > 0),
    total_questions INTEGER NOT NULL CHECK (total_questions > 0),
    questions_per_row INTEGER DEFAULT 5,
    answer_options INTEGER DEFAULT 4 CHECK (answer_options BETWEEN 2 AND 10),
    usage_count INTEGER DEFAULT 0,
    is_public BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    last_used TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create processing_sessions table
CREATE TABLE IF NOT EXISTS public.processing_sessions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    session_name TEXT NOT NULL,
    answer_key_id UUID REFERENCES public.answer_keys(id) ON DELETE SET NULL,
    template_id UUID REFERENCES public.omr_templates(id) ON DELETE SET NULL,
    total_files INTEGER NOT NULL DEFAULT 0,
    processed_files INTEGER DEFAULT 0,
    successful_files INTEGER DEFAULT 0,
    failed_files INTEGER DEFAULT 0,
    progress_percentage DECIMAL(5,2) DEFAULT 0.00,
    status processing_status DEFAULT 'pending',
    processing_config JSONB DEFAULT '{}',
    error_summary JSONB DEFAULT '[]',
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create omr_results table
CREATE TABLE IF NOT EXISTS public.omr_results (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
    session_id UUID REFERENCES public.processing_sessions(id) ON DELETE CASCADE,
    answer_key_id UUID REFERENCES public.answer_keys(id) ON DELETE SET NULL,
    template_id UUID REFERENCES public.omr_templates(id) ON DELETE SET NULL,
    filename TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    student_info JSONB DEFAULT '{}',
    detected_answers JSONB NOT NULL,
    correct_answers JSONB,
    scoring_details JSONB DEFAULT '{}',
    total_score DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    max_possible_score DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    percentage DECIMAL(5,2) GENERATED ALWAYS AS (
        CASE 
            WHEN max_possible_score > 0 THEN (total_score / max_possible_score) * 100
            ELSE 0
        END
    ) STORED,
    confidence_score DECIMAL(4,3) NOT NULL DEFAULT 0.000 CHECK (confidence_score BETWEEN 0.000 AND 1.000),
    processing_quality processing_quality DEFAULT 'good',
    processing_time DECIMAL(6,3),
    status processing_status DEFAULT 'completed',
    error_details JSONB DEFAULT '{}',
    review_notes TEXT,
    is_reviewed BOOLEAN DEFAULT false,
    reviewed_by UUID REFERENCES public.users(id) ON DELETE SET NULL,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create system_stats table
CREATE TABLE IF NOT EXISTS public.system_stats (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    total_sheets_processed INTEGER DEFAULT 0,
    successful_processing INTEGER DEFAULT 0,
    failed_processing INTEGER DEFAULT 0,
    average_processing_time DECIMAL(6,3) DEFAULT 0.000,
    average_confidence_score DECIMAL(4,3) DEFAULT 0.000,
    average_accuracy DECIMAL(5,2) DEFAULT 0.00,
    active_users INTEGER DEFAULT 0,
    new_users INTEGER DEFAULT 0,
    system_uptime DECIMAL(5,2) DEFAULT 100.00,
    error_rate DECIMAL(5,2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON public.users(role);
CREATE INDEX IF NOT EXISTS idx_users_institution ON public.users(institution);
CREATE INDEX IF NOT EXISTS idx_users_active ON public.users(is_active);

CREATE INDEX IF NOT EXISTS idx_answer_keys_user_id ON public.answer_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_answer_keys_public ON public.answer_keys(is_public, is_active);
CREATE INDEX IF NOT EXISTS idx_answer_keys_usage ON public.answer_keys(usage_count DESC);

CREATE INDEX IF NOT EXISTS idx_omr_templates_user_id ON public.omr_templates(user_id);
CREATE INDEX IF NOT EXISTS idx_omr_templates_public ON public.omr_templates(is_public, is_active);
CREATE INDEX IF NOT EXISTS idx_omr_templates_layout ON public.omr_templates(layout_type);

CREATE INDEX IF NOT EXISTS idx_processing_sessions_user_id ON public.processing_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_processing_sessions_status ON public.processing_sessions(status);
CREATE INDEX IF NOT EXISTS idx_processing_sessions_created ON public.processing_sessions(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_omr_results_user_id ON public.omr_results(user_id);
CREATE INDEX IF NOT EXISTS idx_omr_results_session_id ON public.omr_results(session_id);
CREATE INDEX IF NOT EXISTS idx_omr_results_status ON public.omr_results(status);
CREATE INDEX IF NOT EXISTS idx_omr_results_created ON public.omr_results(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_omr_results_score ON public.omr_results(total_score DESC);
CREATE INDEX IF NOT EXISTS idx_omr_results_confidence ON public.omr_results(confidence_score DESC);

CREATE INDEX IF NOT EXISTS idx_system_stats_date ON public.system_stats(date DESC);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON public.users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_answer_keys_updated_at 
    BEFORE UPDATE ON public.answer_keys 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_omr_templates_updated_at 
    BEFORE UPDATE ON public.omr_templates 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_processing_sessions_updated_at 
    BEFORE UPDATE ON public.processing_sessions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_omr_results_updated_at 
    BEFORE UPDATE ON public.omr_results 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_stats_updated_at 
    BEFORE UPDATE ON public.system_stats 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.answer_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.omr_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.processing_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.omr_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.system_stats ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can only see and modify their own profile
CREATE POLICY "Users can view own profile" ON public.users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.users
    FOR UPDATE USING (auth.uid() = id);

-- Answer keys policies
CREATE POLICY "Users can view own answer keys" ON public.answer_keys
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can view public answer keys" ON public.answer_keys
    FOR SELECT USING (is_public = true AND is_active = true);

CREATE POLICY "Users can create answer keys" ON public.answer_keys
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own answer keys" ON public.answer_keys
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own answer keys" ON public.answer_keys
    FOR DELETE USING (auth.uid() = user_id);

-- OMR templates policies
CREATE POLICY "Users can view own templates" ON public.omr_templates
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can view public templates" ON public.omr_templates
    FOR SELECT USING (is_public = true AND is_active = true);

CREATE POLICY "Users can create templates" ON public.omr_templates
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own templates" ON public.omr_templates
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own templates" ON public.omr_templates
    FOR DELETE USING (auth.uid() = user_id);

-- Processing sessions policies
CREATE POLICY "Users can view own sessions" ON public.processing_sessions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create sessions" ON public.processing_sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own sessions" ON public.processing_sessions
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own sessions" ON public.processing_sessions
    FOR DELETE USING (auth.uid() = user_id);

-- OMR results policies
CREATE POLICY "Users can view own results" ON public.omr_results
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create results" ON public.omr_results
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own results" ON public.omr_results
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own results" ON public.omr_results
    FOR DELETE USING (auth.uid() = user_id);

-- System stats policies (admin only)
CREATE POLICY "Admins can view system stats" ON public.system_stats
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id = auth.uid() AND role IN ('admin', 'super_admin')
        )
    );

-- Create views for common queries
CREATE OR REPLACE VIEW user_dashboard_stats AS
SELECT 
    u.id as user_id,
    u.full_name,
    COUNT(DISTINCT r.id) as total_results,
    COUNT(DISTINCT s.id) as total_sessions,
    AVG(r.total_score) as average_score,
    AVG(r.confidence_score) as average_confidence,
    COUNT(DISTINCT ak.id) as created_answer_keys,
    COUNT(DISTINCT t.id) as created_templates,
    MAX(r.created_at) as last_processing_date
FROM public.users u
LEFT JOIN public.omr_results r ON u.id = r.user_id
LEFT JOIN public.processing_sessions s ON u.id = s.user_id
LEFT JOIN public.answer_keys ak ON u.id = ak.user_id
LEFT JOIN public.omr_templates t ON u.id = t.user_id
GROUP BY u.id, u.full_name;

CREATE OR REPLACE VIEW recent_processing_activity AS
SELECT 
    r.id,
    r.filename,
    r.total_score,
    r.percentage,
    r.confidence_score,
    r.processing_quality,
    r.status,
    r.created_at,
    u.full_name as user_name,
    ak.name as answer_key_name,
    s.session_name
FROM public.omr_results r
JOIN public.users u ON r.user_id = u.id
LEFT JOIN public.answer_keys ak ON r.answer_key_id = ak.id
LEFT JOIN public.processing_sessions s ON r.session_id = s.id
WHERE r.created_at >= NOW() - INTERVAL '7 days'
ORDER BY r.created_at DESC;

-- Grant permissions
GRANT USAGE ON SCHEMA public TO authenticated, anon;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated;

-- Grant select on views
GRANT SELECT ON user_dashboard_stats TO authenticated;
GRANT SELECT ON recent_processing_activity TO authenticated;

-- Create function to handle new user registration
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, email, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email)
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger for new user registration
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION handle_new_user();

-- Insert migration record
INSERT INTO public.system_stats (date, total_sheets_processed) 
VALUES (CURRENT_DATE, 0) 
ON CONFLICT (date) DO NOTHING;

-- Add helpful comments
COMMENT ON DATABASE postgres IS 'OMR Evaluation System Database';
COMMENT ON SCHEMA public IS 'Main schema for OMR Evaluation System';

-- Migration completed successfully
SELECT 'Migration 001_initial_setup completed successfully' as status;