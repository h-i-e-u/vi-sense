---
title: Vi Sense App
emoji: 🌍
colorFrom: pink
colorTo: purple
sdk: docker
pinned: false
license: unknown
short_description: 'Vietnamese sentiment analysis application. '
---
Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

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
- Backend API: http://localhost:8000/api
- API Docs: http://localhost:8000/docs

### Docker Deployment

```bash
docker-compose up --build
```

## API Documentation

Base URL: `http://localhost:8000/api`

API docs tu dong cua FastAPI: `http://localhost:8000/docs`

Tat ca endpoint ben duoi, tru `/api`, `/api/health`, `/api/auth/register`, `/api/auth/login`, can header:

```http
Authorization: Bearer <access_token>
```

### Root & Health

#### `GET /api`

Response:

```json
{
  "message": "Welcome to Vi-Sense API"
}
```

#### `GET /api/health`

Response:

```json
{
  "status": "healthy"
}
```

### Authentication

#### `POST /api/auth/register`

Dang ky tai khoan moi.

Request:

```json
{
  "email": "user@example.com",
  "username": "demo_user",
  "password": "your_password"
}
```

Response:

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer",
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "username": "demo_user",
    "created_at": "2026-05-29T12:00:00"
  }
}
```

#### `POST /api/auth/login`

Dang nhap bang form URL encoded. Truong `username` la email.

Request content type: `application/x-www-form-urlencoded`

```text
username=user@example.com&password=your_password
```

Response giong `/api/auth/register`.

### Analysis

Response chung cua cac API analyze la `AnalysisJob`:

```json
{
  "id": "job-uuid",
  "user_id": "user-uuid",
  "type": "text",
  "status": "completed",
  "created_at": "2026-05-29T12:00:00",
  "completed_at": "2026-05-29T12:00:01",
  "source_url": null,
  "results": [
    {
      "label": "POSITIVE",
      "confidence": 0.98,
      "text": "San pham rat tot"
    }
  ],
  "metadata": {
    "total_comments": 1,
    "positive_ratio": 1.0,
    "neutral_ratio": 0.0,
    "negative_ratio": 0.0
  },
  "from_cache": false
}
```

`label` co the la `POSITIVE`, `NEUTRAL`, hoac `NEGATIVE`.

#### `POST /api/analyze/text`

Phan tich cam xuc cho mot doan text.

Request:

```json
{
  "text": "San pham rat tot, giao hang nhanh"
}
```

Response: `AnalysisJob` voi `type = "text"` va `metadata.total_comments = 1`.

#### `POST /api/analyze/link`

Lay comment/review tu link va phan tich cam xuc. Ho tro `type`: `youtube`, `tiki`, `shopee`.

Request:

```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "type": "youtube"
}
```

Response:

```json
{
  "id": "job-uuid",
  "user_id": "user-uuid",
  "type": "link",
  "status": "completed",
  "created_at": "2026-05-29T12:00:00",
  "completed_at": "2026-05-29T12:00:05",
  "source_url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "results": [
    {
      "label": "POSITIVE",
      "confidence": 0.94,
      "text": "Noi dung rat huu ich"
    }
  ],
  "metadata": {
    "total_comments": 50,
    "positive_ratio": 0.7,
    "neutral_ratio": 0.2,
    "negative_ratio": 0.1,
    "source_url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "platform": "youtube"
  },
  "from_cache": false
}
```

Neu link da tung duoc phan tich thanh cong, API co the tra job cu voi `from_cache = true`.

#### `POST /api/analyze/file`

Upload file va phan tich cam xuc theo tung dong/ban ghi. Ho tro `.csv`, `.xlsx`, `.xls`, `.txt`.

Request content type: `multipart/form-data`

```text
file=@reviews.csv
```

Response: `AnalysisJob` voi `type = "file"` va metadata co them thong tin file:

```json
{
  "metadata": {
    "total_comments": 120,
    "positive_ratio": 0.6,
    "neutral_ratio": 0.25,
    "negative_ratio": 0.15,
    "file_name": "reviews.csv",
    "file_size": 4096
  }
}
```

#### `GET /api/analyze/check-existing/{job_id}`

Kiem tra job co ton tai va da co ket qua sentiment hay chua.

Response:

```json
{
  "exists": true,
  "has_results": true,
  "job_type": "link",
  "status": "completed",
  "created_at": "2026-05-29T12:00:00",
  "result_count": 50,
  "metadata": {
    "total_comments": 50,
    "platform": "youtube"
  }
}
```

Neu khong tim thay:

```json
{
  "exists": false,
  "has_results": false
}
```

#### `POST /api/analyze/refresh/{job_id}`

Chay lai phan tich cho job link cu. Endpoint nay khong ho tro job `text` hoac `file`.

Response: `AnalysisJob` moi, co `metadata.refreshed_from` tro ve job cu.

### History

#### `GET /api/history?skip=0&limit=50`

Lay lich su phan tich cua user hien tai.

Response:

```json
[
  {
    "id": "job-uuid",
    "user_id": "user-uuid",
    "type": "text",
    "status": "completed",
    "created_at": "2026-05-29T12:00:00",
    "completed_at": "2026-05-29T12:00:01",
    "source_url": null,
    "results": [],
    "metadata": {},
    "from_cache": false
  }
]
```

#### `GET /api/history/{job_id}`

Lay chi tiet mot job.

Response: `AnalysisJob`.

#### `DELETE /api/history/`

Xoa toan bo lich su cua user hien tai.

Response:

```json
{
  "message": "All history deleted successfully"
}
```

### Analytics

#### `GET /api/analytics/summary`

Tong quan analytics cua user hien tai.

Response:

```json
{
  "total_analyses": 10,
  "text_analyses": 4,
  "file_analyses": 2,
  "link_analyses": 4,
  "sentiment_distribution": {
    "positive": 80,
    "neutral": 30,
    "negative": 15
  },
  "daily_analysis_counts": [
    {
      "date": "2026-05-29",
      "count": 3
    }
  ],
  "top_keywords": [
    {
      "word": "tot",
      "count": 12
    }
  ]
}
```

#### `GET /api/analytics/job/{job_id}`

Analytics chi tiet cho mot job.

Response:

```json
{
  "total_analyses": 1,
  "text_analyses": 0,
  "file_analyses": 0,
  "link_analyses": 1,
  "sentiment_distribution": {
    "positive": 35,
    "neutral": 10,
    "negative": 5
  },
  "trend_data": [
    {
      "date": "2026-05-29",
      "positive": 5,
      "neutral": 1,
      "negative": 0
    }
  ],
  "top_keywords": [
    {
      "word": "hay",
      "count": 8
    }
  ],
  "top_positive_comments": [
    {
      "id": "result-uuid",
      "job_id": "job-uuid",
      "text": "Rat hai long",
      "sentiment": {
        "label": "POSITIVE",
        "confidence": 0.99,
        "text": "Rat hai long"
      },
      "source_date": "2026-05-29T12:00:00",
      "created_at": "2026-05-29T12:00:00"
    }
  ],
  "top_negative_comments": []
}
```

### Sentences

#### `GET /api/sentences/?page=1&limit=20&search=tot&job_type=text&label=POSITIVE`

Lay danh sach cac cau/comment da duoc xu ly, co phan trang va filter.

Query params:

- `page`: so trang, mac dinh `1`
- `limit`: so item moi trang, tu `1` den `100`, mac dinh `20`
- `search`: tim trong noi dung cau
- `job_type`: `text`, `link`, hoac `file`
- `label`: `POSITIVE`, `NEUTRAL`, hoac `NEGATIVE`

Response:

```json
{
  "total": 42,
  "page": 1,
  "limit": 20,
  "total_pages": 3,
  "items": [
    {
      "id": "result-uuid",
      "job_id": "job-uuid",
      "comment_id": "comment-uuid",
      "text": "San pham rat tot",
      "label": "POSITIVE",
      "confidence": 0.98,
      "created_at": "2026-05-29T12:00:00",
      "job": {
        "id": "job-uuid",
        "type": "text"
      }
    }
  ]
}
```

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
