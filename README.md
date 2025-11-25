# Vision MVP

AI-powered photo matching application using face recognition.

## Features

- **Studio Portal**: Register events, upload photos, generate QR codes
- **User Portal**: Scan QR codes, upload selfies, find matching photos
- **Authentication**: Role-based access (Studio/Customer)
- **Face Recognition**: InsightFace AI with 70-95% accuracy
- **Real-time Matching**: Fast face matching with similarity scores

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- Windows (or adjust commands for Linux/Mac)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python migrate_database.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`

### Test Accounts

- **Admin**: admin@vision-mvp.com / admin (Studio role)

## Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed deployment instructions.

### Quick Deploy

**Backend** (Railway):
```bash
railway login
railway link
railway up
```

**Frontend** (Vercel):
```bash
vercel login
cd frontend
vercel --prod
```

## Project Structure

```
Vision_MVP/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── models.py     # Database models
│   │   ├── db.py         # Database config
│   │   └── utils/        # Auth & embeddings
│   ├── requirements.txt
│   └── Procfile
├── frontend/
│   ├── src/
│   │   ├── pages/        # React pages
│   │   ├── components/   # React components
│   │   ├── context/      # Auth context
│   │   └── api.js        # API client
│   └── package.json
└── worker/
    └── indexer.py        # Background photo indexing
```

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, InsightFace, JWT
- **Frontend**: React, Vite, Axios
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **AI**: InsightFace buffalo_l model

## Documentation

- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Testing Guide](TESTING_GUIDE.md)
- [Accuracy Improvements](ACCURACY_IMPROVEMENTS.md)
- [Manual Testing Guide](MANUAL_TESTING_GUIDE.md)

## License

MIT
