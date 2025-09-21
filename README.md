# OMR Evaluation System

A scalable, automated OMR (Optical Mark Recognition) evaluation system that processes OMR sheets captured via mobile phone camera with <0.5% error tolerance.

## Project Structure

```
OMR evaluator 2/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── core/           # Core OMR processing engine
│   │   ├── api/            # API endpoints
│   │   ├── models/         # Database models
│   │   └── utils/          # Utility functions
│   ├── requirements.txt
│   └── main.py
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Next.js pages
│   │   └── utils/          # Frontend utilities
│   ├── package.json
│   └── next.config.js
├── omr_engine/             # Core Python OMR processing
│   ├── preprocessing/      # Image preprocessing
│   ├── detection/          # Bubble detection
│   ├── scoring/           # Scoring logic
│   └── utils/             # OMR utilities
├── data/                   # Sample data and templates
│   ├── sample_sheets/      # Sample OMR sheets
│   └── answer_keys/        # Answer key templates
└── docs/                   # Documentation
```

## Tech Stack

- **Core OMR Engine**: Python with OpenCV, NumPy, SciPy, Pillow
- **Backend**: FastAPI
- **Frontend**: Next.js (React)
- **Database & Auth**: Supabase (PostgreSQL + Authentication)
- **Version Control**: Git

## Features

- Mobile camera OMR sheet processing
- Real-time processing dashboard
- Batch upload support
- Interactive review interface for flagged sheets
- Secure authentication and data access
- Export results as CSV/Excel
- Per-subject scoring (0-20) and total score (0-100)

## Development Phases

1. **Phase 1**: Environment setup and data preparation
2. **Phase 2**: Core OMR engine development
3. **Phase 3**: Web application with Supabase integration
4. **Phase 4**: Integration and testing
5. **Phase 5**: Deployment and training

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- Git

### Setup Instructions

1. Clone the repository
2. Set up the Python environment for OMR processing
3. Initialize the Next.js frontend
4. Configure FastAPI backend
5. Set up Supabase project

Detailed setup instructions will be provided in each component's directory.

## Error Tolerance Target

< 0.5% error rate with proper image quality and lighting conditions.