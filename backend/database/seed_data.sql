-- Seed data for OMR Evaluation System
-- This file contains initial data for development and testing

-- Sample Answer Keys
INSERT INTO public.answer_keys (
    id,
    user_id,
    name,
    description,
    answer_data,
    subject_config,
    scoring_rules,
    total_questions,
    max_score,
    is_public
) VALUES 
(
    '550e8400-e29b-41d4-a716-446655440001',
    '00000000-0000-0000-0000-000000000000', -- System user
    'Mathematics Grade 10 - Sample Test',
    'Standard mathematics test for grade 10 students covering algebra, geometry, and basic calculus',
    '{
        "1": "A", "2": "B", "3": "C", "4": "D", "5": "A",
        "6": "B", "7": "C", "8": "D", "9": "A", "10": "B",
        "11": "C", "12": "D", "13": "A", "14": "B", "15": "C",
        "16": "D", "17": "A", "18": "B", "19": "C", "20": "D"
    }',
    '{
        "subjects": {
            "mathematics": {
                "name": "Mathematics",
                "questions": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
                "max_score": 100
            }
        }
    }',
    '{
        "scoring_method": "standard",
        "points_per_question": 5,
        "negative_marking": false,
        "partial_credit": false,
        "bonus_questions": []
    }',
    20,
    100.00,
    true
),
(
    '550e8400-e29b-41d4-a716-446655440002',
    '00000000-0000-0000-0000-000000000000',
    'Science Comprehensive Test',
    'Multi-subject science test covering Physics, Chemistry, and Biology',
    '{
        "1": "A", "2": "B", "3": "C", "4": "D", "5": "A",
        "6": "B", "7": "C", "8": "D", "9": "A", "10": "B",
        "11": "C", "12": "D", "13": "A", "14": "B", "15": "C",
        "16": "D", "17": "A", "18": "B", "19": "C", "20": "D",
        "21": "A", "22": "B", "23": "C", "24": "D", "25": "A",
        "26": "B", "27": "C", "28": "D", "29": "A", "30": "B"
    }',
    '{
        "subjects": {
            "physics": {
                "name": "Physics",
                "questions": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "max_score": 50
            },
            "chemistry": {
                "name": "Chemistry", 
                "questions": [11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
                "max_score": 50
            },
            "biology": {
                "name": "Biology",
                "questions": [21, 22, 23, 24, 25, 26, 27, 28, 29, 30],
                "max_score": 50
            }
        }
    }',
    '{
        "scoring_method": "weighted",
        "points_per_question": 5,
        "negative_marking": true,
        "negative_points": -1,
        "partial_credit": false,
        "subject_weights": {
            "physics": 1.0,
            "chemistry": 1.0,
            "biology": 1.0
        }
    }',
    30,
    150.00,
    true
),
(
    '550e8400-e29b-41d4-a716-446655440003',
    '00000000-0000-0000-0000-000000000000',
    'English Language Test',
    'Comprehensive English test covering grammar, vocabulary, and reading comprehension',
    '{
        "1": "B", "2": "A", "3": "D", "4": "C", "5": "B",
        "6": "A", "7": "D", "8": "C", "9": "B", "10": "A",
        "11": "D", "12": "C", "13": "B", "14": "A", "15": "D",
        "16": "C", "17": "B", "18": "A", "19": "D", "20": "C",
        "21": "B", "22": "A", "23": "D", "24": "C", "25": "B"
    }',
    '{
        "subjects": {
            "english": {
                "name": "English Language",
                "questions": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
                "max_score": 100
            }
        }
    }',
    '{
        "scoring_method": "standard",
        "points_per_question": 4,
        "negative_marking": false,
        "partial_credit": true,
        "partial_credit_percentage": 0.5
    }',
    25,
    100.00,
    true
);

-- Sample OMR Templates
INSERT INTO public.omr_templates (
    id,
    user_id,
    name,
    description,
    template_config,
    layout_type,
    page_width,
    page_height,
    bubble_size,
    bubble_spacing,
    total_questions,
    questions_per_row,
    answer_options,
    is_public
) VALUES
(
    '660e8400-e29b-41d4-a716-446655440001',
    '00000000-0000-0000-0000-000000000000',
    'Standard 20-Question Template',
    'Standard OMR template for 20 questions with 4 answer options each',
    '{
        "layout": {
            "type": "grid",
            "columns": 2,
            "question_spacing": 30,
            "bubble_spacing": 25
        },
        "answer_area": {
            "start_x": 100,
            "start_y": 200,
            "width": 400,
            "height": 600
        },
        "student_info": {
            "name_area": {"x": 100, "y": 100, "width": 300, "height": 30},
            "id_area": {"x": 100, "y": 140, "width": 200, "height": 30}
        },
        "alignment_marks": [
            {"x": 50, "y": 50},
            {"x": 550, "y": 50},
            {"x": 50, "y": 750},
            {"x": 550, "y": 750}
        ],
        "questions": {
            "total": 20,
            "options": ["A", "B", "C", "D"],
            "arrangement": "two_column"
        }
    }',
    'standard',
    600,
    800,
    20,
    30,
    20,
    5,
    4,
    true
),
(
    '660e8400-e29b-41d4-a716-446655440002',
    '00000000-0000-0000-0000-000000000000',
    'Extended 30-Question Template',
    'Extended OMR template for 30 questions with 4 answer options each',
    '{
        "layout": {
            "type": "grid",
            "columns": 3,
            "question_spacing": 25,
            "bubble_spacing": 20
        },
        "answer_area": {
            "start_x": 80,
            "start_y": 180,
            "width": 440,
            "height": 700
        },
        "student_info": {
            "name_area": {"x": 80, "y": 80, "width": 300, "height": 25},
            "id_area": {"x": 80, "y": 115, "width": 200, "height": 25},
            "class_area": {"x": 80, "y": 150, "width": 150, "height": 25}
        },
        "alignment_marks": [
            {"x": 40, "y": 40},
            {"x": 560, "y": 40},
            {"x": 40, "y": 920},
            {"x": 560, "y": 920}
        ],
        "questions": {
            "total": 30,
            "options": ["A", "B", "C", "D"],
            "arrangement": "three_column"
        }
    }',
    'multi_column',
    600,
    960,
    18,
    25,
    30,
    10,
    4,
    true
),
(
    '660e8400-e29b-41d4-a716-446655440003',
    '00000000-0000-0000-0000-000000000000',
    'Custom 50-Question Template',
    'Large format template for comprehensive tests with 50 questions',
    '{
        "layout": {
            "type": "grid",
            "columns": 2,
            "question_spacing": 20,
            "bubble_spacing": 18
        },
        "answer_area": {
            "start_x": 60,
            "start_y": 160,
            "width": 680,
            "height": 900
        },
        "student_info": {
            "name_area": {"x": 60, "y": 60, "width": 350, "height": 25},
            "id_area": {"x": 60, "y": 95, "width": 200, "height": 25},
            "class_area": {"x": 280, "y": 95, "width": 130, "height": 25},
            "date_area": {"x": 430, "y": 95, "width": 130, "height": 25}
        },
        "alignment_marks": [
            {"x": 30, "y": 30},
            {"x": 770, "y": 30},
            {"x": 30, "y": 1090},
            {"x": 770, "y": 1090}
        ],
        "questions": {
            "total": 50,
            "options": ["A", "B", "C", "D", "E"],
            "arrangement": "two_column_dense"
        }
    }',
    'custom',
    800,
    1120,
    16,
    20,
    50,
    25,
    5,
    true
);

-- Sample System Statistics (for demonstration)
INSERT INTO public.system_stats (
    date,
    total_sheets_processed,
    successful_processing,
    failed_processing,
    average_processing_time,
    average_confidence_score,
    average_accuracy,
    active_users,
    new_users,
    system_uptime,
    error_rate
) VALUES 
(
    CURRENT_DATE - INTERVAL '7 days',
    150,
    145,
    5,
    2.45,
    0.892,
    94.50,
    25,
    3,
    99.8,
    3.33
),
(
    CURRENT_DATE - INTERVAL '6 days',
    180,
    175,
    5,
    2.38,
    0.898,
    95.20,
    28,
    2,
    99.9,
    2.78
),
(
    CURRENT_DATE - INTERVAL '5 days',
    220,
    215,
    5,
    2.42,
    0.905,
    95.80,
    32,
    4,
    99.7,
    2.27
),
(
    CURRENT_DATE - INTERVAL '4 days',
    195,
    190,
    5,
    2.35,
    0.912,
    96.10,
    30,
    1,
    99.9,
    2.56
),
(
    CURRENT_DATE - INTERVAL '3 days',
    240,
    235,
    5,
    2.28,
    0.918,
    96.50,
    35,
    5,
    99.8,
    2.08
),
(
    CURRENT_DATE - INTERVAL '2 days',
    210,
    205,
    5,
    2.31,
    0.915,
    96.30,
    33,
    2,
    99.9,
    2.38
),
(
    CURRENT_DATE - INTERVAL '1 day',
    185,
    180,
    5,
    2.40,
    0.908,
    95.90,
    31,
    3,
    99.8,
    2.70
);

-- Create some sample processing sessions for demonstration
-- Note: These would typically be created by the application during actual processing

-- Update usage counts for public templates and answer keys
UPDATE public.answer_keys SET 
    usage_count = FLOOR(RANDOM() * 50) + 10,
    last_used = NOW() - (RANDOM() * INTERVAL '30 days')
WHERE is_public = true;

UPDATE public.omr_templates SET 
    usage_count = FLOOR(RANDOM() * 30) + 5,
    last_used = NOW() - (RANDOM() * INTERVAL '30 days')
WHERE is_public = true;

-- Create some sample configuration data
INSERT INTO public.answer_keys (
    user_id,
    name,
    description,
    answer_data,
    subject_config,
    scoring_rules,
    total_questions,
    max_score,
    is_public
) VALUES 
(
    '00000000-0000-0000-0000-000000000000',
    'Quick Quiz Template',
    'Simple 10-question quiz template for quick assessments',
    '{
        "1": "A", "2": "B", "3": "C", "4": "A", "5": "B",
        "6": "C", "7": "A", "8": "B", "9": "C", "10": "A"
    }',
    '{
        "subjects": {
            "general": {
                "name": "General Knowledge",
                "questions": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "max_score": 50
            }
        }
    }',
    '{
        "scoring_method": "standard",
        "points_per_question": 5,
        "negative_marking": false,
        "partial_credit": false
    }',
    10,
    50.00,
    true
);

-- Add some helpful comments and documentation
COMMENT ON TABLE public.users IS 'Extended user profiles linked to Supabase auth.users';
COMMENT ON TABLE public.omr_results IS 'Stores all OMR processing results with detailed scoring and metadata';
COMMENT ON TABLE public.processing_sessions IS 'Tracks batch processing sessions and their progress';
COMMENT ON TABLE public.answer_keys IS 'Reusable answer key templates for different tests';
COMMENT ON TABLE public.omr_templates IS 'OMR sheet layout templates for different question formats';
COMMENT ON TABLE public.system_stats IS 'Daily system statistics for monitoring and analytics';

COMMENT ON COLUMN public.omr_results.confidence_score IS 'Processing confidence score (0.0 to 1.0)';
COMMENT ON COLUMN public.omr_results.processing_quality IS 'Qualitative assessment of processing quality';
COMMENT ON COLUMN public.omr_results.percentage IS 'Calculated percentage score (auto-generated)';
COMMENT ON COLUMN public.processing_sessions.progress_percentage IS 'Batch processing progress (0.0 to 100.0)';

-- Create some utility functions for common operations
CREATE OR REPLACE FUNCTION get_user_recent_results(user_uuid UUID, limit_count INTEGER DEFAULT 10)
RETURNS TABLE (
    id UUID,
    filename TEXT,
    total_score DECIMAL(5,2),
    percentage DECIMAL(5,2),
    confidence_score DECIMAL(4,3),
    status TEXT,
    created_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        r.id,
        r.filename,
        r.total_score,
        r.percentage,
        r.confidence_score,
        r.status,
        r.created_at
    FROM public.omr_results r
    WHERE r.user_id = user_uuid
    ORDER BY r.created_at DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION get_public_answer_keys()
RETURNS TABLE (
    id UUID,
    name TEXT,
    description TEXT,
    total_questions INTEGER,
    max_score DECIMAL(5,2),
    usage_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ak.id,
        ak.name,
        ak.description,
        ak.total_questions,
        ak.max_score,
        ak.usage_count
    FROM public.answer_keys ak
    WHERE ak.is_public = true AND ak.is_active = true
    ORDER BY ak.usage_count DESC, ak.name;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permissions on utility functions
GRANT EXECUTE ON FUNCTION get_user_recent_results(UUID, INTEGER) TO authenticated;
GRANT EXECUTE ON FUNCTION get_public_answer_keys() TO authenticated, anon;