# OMR Evaluation System - Setup Guide

## Prerequisites

Before setting up the OMR Evaluation System, ensure you have the following installed:

- **Python 3.8+** - For the OMR processing engine and backend
- **Node.js 16+** - For the Next.js frontend
- **Git** - For version control
- **Supabase Account** - For database and authentication

## Project Structure Overview

```
OMR evaluator 2/
├── backend/                 # FastAPI backend application
├── frontend/               # Next.js frontend application  
├── omr_engine/             # Core OMR processing engine
├── data/                   # Sample data and uploads
└── docs/                   # Documentation
```

## Setup Instructions

### 1. Clone and Navigate to Project

```bash
git clone <repository-url>
cd "OMR evaluator 2"
```

### 2. Backend Setup (FastAPI)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
copy .env.example .env

# Edit .env file with your Supabase credentials
```

### 3. Frontend Setup (Next.js)

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies (already done during creation)
npm install

# Copy environment template
copy .env.local.example .env.local

# Edit .env.local with your configuration
```

### 4. Supabase Setup

1. **Create a new Supabase project** at [supabase.com](https://supabase.com)

2. **Get your project credentials:**
   - Project URL
   - Anon/Public Key
   - Service Role Key (for backend)

3. **Update environment files:**
   - Backend: Update `backend/.env`
   - Frontend: Update `frontend/.env.local`

4. **Database Schema** (will be created in Phase 3):
   ```sql
   -- Tables will be created for:
   -- - omr_sheets (uploaded sheets)
   -- - processing_results (evaluation results)
   -- - users (evaluator accounts)
   -- - audit_logs (system activity)
   ```

### 5. OMR Engine Setup

```bash
# From project root, install OMR processing dependencies
pip install -r requirements.txt
```

## Running the Application

### Development Mode

1. **Start the Backend:**
   ```bash
   cd backend
   python main.py
   # Backend will run on http://localhost:8000
   ```

2. **Start the Frontend:**
   ```bash
   cd frontend
   npm run dev
   # Frontend will run on http://localhost:3000
   ```

### Testing the Setup

1. **Backend API:** Visit http://localhost:8000/docs for API documentation
2. **Frontend:** Visit http://localhost:3000 for the web application
3. **Health Check:** Visit http://localhost:8000/health

## Development Workflow

### Phase 1: Current Status ✅
- [x] Project structure created
- [x] Backend FastAPI setup
- [x] Frontend Next.js setup
- [x] Basic API routes
- [x] Environment configuration
- [x] Version control initialized

### Phase 2: Next Steps
- [ ] Implement image preprocessing module
- [ ] Develop bubble detection algorithms
- [ ] Create scoring and evaluation logic
- [ ] Add comprehensive testing

### Phase 3: Integration
- [ ] Connect frontend to backend
- [ ] Implement Supabase authentication
- [ ] Create database schema
- [ ] Build user interface components

## Troubleshooting

### Common Issues

1. **Port conflicts:** Ensure ports 3000 and 8000 are available
2. **Python dependencies:** Use virtual environment to avoid conflicts
3. **Node.js version:** Ensure Node.js 16+ is installed
4. **Supabase connection:** Verify credentials in environment files

### Getting Help

- Check the API documentation at `/docs` endpoint
- Review error logs in terminal output
- Ensure all environment variables are properly set

## Next Steps

After completing the setup:

1. **Phase 2:** Implement core OMR processing engine
2. **Phase 3:** Build web application with Supabase integration
3. **Phase 4:** Integration testing and optimization
4. **Phase 5:** Deployment and production setup