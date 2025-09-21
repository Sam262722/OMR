# OMR Evaluator System

A comprehensive Optical Mark Recognition (OMR) evaluation platform built with Next.js frontend and Python backend, featuring role-based access control and automated deployment.

## 🚀 Live Demo

**Production URL**: https://v0-exam-taking-platform-b1jwukx4g-sams-projects-d1727290.vercel.app

## 📋 Features

- **Role-Based Access Control**: Teacher, Admin, and Super Admin roles
- **OMR Processing**: Automated bubble sheet evaluation
- **Modern UI**: Built with Next.js 15, React 19, and Tailwind CSS
- **Authentication**: Secure user management with Supabase
- **Real-time Updates**: Live dashboard and results
- **Responsive Design**: Works on desktop and mobile devices

## 🛠 Tech Stack

### Frontend
- **Framework**: Next.js 15 with React 19
- **Styling**: Tailwind CSS
- **Authentication**: Supabase Auth
- **Database**: Supabase PostgreSQL
- **Deployment**: Vercel with automatic deployments

### Backend
- **Language**: Python
- **OMR Engine**: Custom bubble detection and scoring
- **Image Processing**: OpenCV and PIL
- **API**: RESTful endpoints

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- Python 3.8+
- Supabase account

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Sam262722/OMR.git
   cd OMR
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   cp .env.example .env.local
   # Add your Supabase credentials to .env.local
   npm run dev
   ```

3. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.example .env
   # Configure your environment variables
   python main.py
   ```

## 📁 Project Structure

```
OMR/
├── frontend/           # Next.js application
│   ├── src/
│   │   ├── app/       # App router pages
│   │   ├── components/ # Reusable components
│   │   └── types/     # TypeScript definitions
│   └── vercel.json    # Vercel configuration
├── backend/           # Python API server
│   ├── app/          # Application modules
│   ├── database/     # Database schema and migrations
│   └── main.py       # Entry point
├── omr_engine/       # OMR processing engine
│   ├── detection/    # Bubble detection algorithms
│   ├── preprocessing/ # Image processing
│   └── scoring/      # Score calculation
└── data/             # Sample data and templates
```

## 🔧 Configuration

### Environment Variables

**Frontend (.env.local)**
```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

**Backend (.env)**
```env
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
```

## 🚀 Deployment

### Automatic Deployment
- **GitHub Integration**: Connected to https://github.com/Sam262722/OMR.git
- **Auto-Deploy**: Every push to `main` branch triggers automatic Vercel deployment
- **Preview Deployments**: Pull requests create preview deployments

### Manual Deployment
```bash
# Deploy to Vercel
cd frontend
vercel --prod
```

For detailed deployment instructions, see [VERCEL_DEPLOYMENT.md](./VERCEL_DEPLOYMENT.md)

## 👥 User Roles

- **Teacher**: Create and manage exams, view results
- **Admin**: Manage users and system settings
- **Super Admin**: Full system access and configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the [setup guide](./docs/setup_guide.md)
- Review the [deployment documentation](./VERCEL_DEPLOYMENT.md)

---

**Built with ❤️ for educational institutions**