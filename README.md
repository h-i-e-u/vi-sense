# Vi-Sense: Vietnamese Sentiment Analysis System

A modern fullstack application for analyzing Vietnamese sentiment from YouTube comments, Shopee/Tiki reviews, text inputs, and uploaded files.

## Features

- **Multi-source Analysis**: Analyze sentiment from YouTube, Shopee, Tiki, text, and files
- **Real-time Processing**: Live sentiment prediction for text input
- **Dashboard Analytics**: Visualize sentiment data with charts and word clouds
- **Modern UI**: Glassmorphism design with dark mode
- **AI-Powered**: Uses PhoBERT model for Vietnamese sentiment analysis
- **Secure**: JWT authentication and input validation

## Tech Stack

### Frontend
- React 18 + Vite
- TypeScript
- TailwindCSS + shadcn/ui
- Framer Motion
- Recharts
- Axios

### Backend
- Python 3.11 + FastAPI
- SQLAlchemy + SQLite
- JWT Authentication
- HuggingFace Transformers

### Crawler
- Python + requests + BeautifulSoup
- Playwright for complex sites

## Project Structure

```
vi-sense/
├── client/          # React frontend
├── core/           # FastAPI backend
|   ├── app/        # main bussiness services
|   └── crawler/        # Crawler services
├── docker/         # Docker configs
└── docs/           # Documentation
```

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Docker (optional)

### Local Development

1. **Clone and setup:**
```bash
git clone <repository-url>
cd vi-sense
```

2. **Run the application:**
```bash
# Windows
run.bat

# Or manually:
# Backend setup
cd core
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
python run.py

# Frontend setup (in another terminal)
cd client
npm install
npm run dev
```

3. **Access the app:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Docker Deployment

```bash
docker-compose up --build
```

## API Documentation

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login

### Analysis
- `POST /analyze/text` - Analyze single text
- `POST /analyze/link` - Analyze from URL
- `POST /analyze/file` - Analyze uploaded file

### History & Analytics
- `GET /history` - Get analysis history
- `GET /analytics/summary` - Get analytics data

## Development

### Frontend
```bash
cd client
npm install
npm run dev
```

### Backend
```bash
cd core
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### Testing
```bash
cd core
pytest
```

## Deployment

The application is containerized and can be deployed using Docker Compose.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License