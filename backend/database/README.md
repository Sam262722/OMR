# OMR Evaluation System Database

This directory contains the database schema, migrations, and seed data for the OMR Evaluation System built with Supabase PostgreSQL.

## 📁 Directory Structure

```
database/
├── README.md              # This file - database documentation
├── schema.sql             # Complete database schema
├── seed_data.sql          # Sample data for development/testing
└── migrations/
    └── 001_initial_setup.sql  # Initial database setup migration
```

## 🚀 Quick Setup

### 1. Supabase Project Setup

1. Create a new Supabase project at [supabase.com](https://supabase.com)
2. Note your project URL and anon key
3. Go to the SQL Editor in your Supabase dashboard

### 2. Database Initialization

Execute the files in this order:

1. **Initial Setup**: Run `migrations/001_initial_setup.sql`
2. **Sample Data** (optional): Run `seed_data.sql` for development

```sql
-- In Supabase SQL Editor, run these files in order:
-- 1. migrations/001_initial_setup.sql
-- 2. seed_data.sql (optional)
```

### 3. Environment Configuration

Update your backend `.env` file with Supabase credentials:

```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
```

## 📊 Database Schema Overview

### Core Tables

#### `users`
Extended user profiles linked to Supabase auth.users
- **Purpose**: Store additional user information beyond basic auth
- **Key Fields**: role, institution, preferences, subscription_tier
- **RLS**: Users can only access their own profile

#### `answer_keys`
Reusable answer key templates for different tests
- **Purpose**: Store correct answers and scoring configurations
- **Key Fields**: answer_data (JSONB), scoring_rules, subject_config
- **Features**: Public/private sharing, usage tracking

#### `omr_templates`
OMR sheet layout templates for different question formats
- **Purpose**: Define bubble positions and sheet layouts
- **Key Fields**: template_config (JSONB), layout_type, dimensions
- **Features**: Flexible layout configuration, reusable templates

#### `omr_results`
Stores all OMR processing results with detailed scoring
- **Purpose**: Individual sheet processing results
- **Key Fields**: detected_answers, scoring_details, confidence_score
- **Features**: Auto-calculated percentage, quality assessment

#### `processing_sessions`
Tracks batch processing sessions and their progress
- **Purpose**: Manage bulk processing operations
- **Key Fields**: progress_percentage, status, error_summary
- **Features**: Real-time progress tracking, error handling

#### `system_stats`
Daily system statistics for monitoring and analytics
- **Purpose**: Track system performance and usage
- **Key Fields**: processing_metrics, user_activity, error_rates
- **Access**: Admin users only

### Key Features

#### 🔐 Row Level Security (RLS)
- All tables have RLS enabled
- Users can only access their own data
- Public resources (templates, answer keys) have special policies
- Admin-only access for system statistics

#### 🔄 Automatic Triggers
- `updated_at` timestamps automatically maintained
- New user profiles created on auth registration
- Usage counters updated automatically

#### 📈 Performance Optimizations
- Strategic indexes on frequently queried columns
- Materialized views for dashboard statistics
- Efficient JSONB operations for flexible data

#### 🎯 Data Integrity
- Foreign key constraints maintain referential integrity
- Check constraints ensure valid data ranges
- Generated columns for calculated fields

## 🛠️ Common Operations

### Creating Answer Keys

```sql
INSERT INTO answer_keys (
    user_id,
    name,
    description,
    answer_data,
    total_questions,
    max_score
) VALUES (
    auth.uid(),
    'Math Test Chapter 5',
    'Algebra and geometry questions',
    '{"1": "A", "2": "B", "3": "C", "4": "D", "5": "A"}',
    5,
    25.00
);
```

### Querying User Results

```sql
SELECT 
    filename,
    total_score,
    percentage,
    confidence_score,
    created_at
FROM omr_results 
WHERE user_id = auth.uid()
ORDER BY created_at DESC
LIMIT 10;
```

### Batch Processing Status

```sql
SELECT 
    session_name,
    progress_percentage,
    status,
    processed_files,
    total_files
FROM processing_sessions 
WHERE user_id = auth.uid() 
AND status = 'processing';
```

## 🔍 Useful Views

### `user_dashboard_stats`
Aggregated statistics for user dashboard
```sql
SELECT * FROM user_dashboard_stats WHERE user_id = auth.uid();
```

### `recent_processing_activity`
Recent processing activity across all users (last 7 days)
```sql
SELECT * FROM recent_processing_activity LIMIT 20;
```

## 🛡️ Security Considerations

### Authentication
- Uses Supabase Auth for user management
- JWT tokens for API authentication
- Role-based access control (teacher, admin, super_admin)

### Data Protection
- Row Level Security prevents unauthorized access
- Sensitive data encrypted at rest
- API keys and secrets managed through environment variables

### Privacy
- Users can only access their own data
- Public resources clearly marked and controlled
- Admin access logged and monitored

## 📊 Monitoring & Analytics

### System Statistics
Daily metrics tracked automatically:
- Processing volume and success rates
- Average processing time and confidence scores
- User activity and growth
- System uptime and error rates

### Performance Monitoring
- Query performance through database indexes
- Connection pooling for scalability
- Automated backup and recovery

## 🔧 Maintenance

### Regular Tasks
1. **Monitor disk usage** - Large file uploads can consume space
2. **Review error logs** - Check processing_sessions for failed batches
3. **Update statistics** - System stats updated daily via triggers
4. **Backup verification** - Ensure Supabase backups are working

### Scaling Considerations
- Database connection limits (Supabase tier dependent)
- File storage limits for uploaded OMR sheets
- Processing queue management for high volume

## 🐛 Troubleshooting

### Common Issues

#### RLS Policy Errors
```sql
-- Check if user exists in users table
SELECT * FROM auth.users WHERE id = auth.uid();
SELECT * FROM public.users WHERE id = auth.uid();
```

#### Migration Failures
- Ensure proper order: migrations before seed data
- Check for existing tables/constraints
- Verify Supabase project permissions

#### Performance Issues
- Check query execution plans
- Monitor index usage
- Review connection pool settings

### Debug Queries

```sql
-- Check table sizes
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats 
WHERE schemaname = 'public';

-- Monitor active connections
SELECT * FROM pg_stat_activity WHERE state = 'active';

-- Check RLS policies
SELECT * FROM pg_policies WHERE schemaname = 'public';
```

## 📚 Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [JSONB Operations](https://www.postgresql.org/docs/current/functions-json.html)

## 🤝 Contributing

When making database changes:

1. Create new migration files with incremental numbers
2. Test migrations on development environment first
3. Update this README with schema changes
4. Consider backward compatibility
5. Update seed data if needed

---

**Note**: This database schema is designed for high-performance OMR processing with security and scalability in mind. All sensitive operations are protected by Row Level Security policies.