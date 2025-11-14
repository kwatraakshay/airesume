# AI Resume Evaluation System

A full-stack MVP application for AI-powered recruitment resume evaluation. The system processes PDF resumes, extracts information, and provides AI-generated fit scores, recommendations, and detailed summaries.

## 🏗️ Architecture

- **Frontend:** React (Vite)
- **Backend:** Python + FastAPI
- **Worker:** Celery with Redis broker
- **Database:** SQLite
- **Storage:** Local filesystem (`/storage`)
- **AI Model:** OpenAI API

## 📋 Features

- Upload 1-10 PDF resumes simultaneously
- Automatic PDF text extraction (PyMuPDF → pdfminer → OCR fallback)
- Structured data parsing (name, email, phone, skills)
- AI-powered evaluation with fit score (1-10) and recommendation
- 2-page detailed narrative summary
- Real-time status tracking with auto-refresh
- Isolated candidate processing (zero cross-contamination)
- Parallel processing support (1-10 resumes)

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Redis (for Celery)
- OpenAI API key

### Option 1: Docker Compose (Recommended)

1. **Clone and navigate to the project:**
   ```bash
   cd resumeai
   ```

2. **Set environment variables:**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4o-mini
   ```

3. **Start all services:**
   ```bash
   docker-compose up -d
   ```

   This will start:
   - Redis (port 6379)
   - FastAPI backend (port 8000)
   - Celery worker

4. **Start the frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Access the application:**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Option 2: Local Development

#### Backend Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install system dependencies (for PDF/OCR):**
   ```bash
   # macOS
   brew install poppler tesseract tesseract-lang
   
   # Ubuntu/Debian
   sudo apt-get install poppler-utils tesseract-ocr tesseract-ocr-eng
   ```

3. **Set environment variables:**
   Create a `.env` file:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4o-mini
   DATABASE_URL=sqlite:///./storage/db/recruitment.db
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/0
   ```

4. **Start Redis:**
   ```bash
   redis-server
   ```

5. **Initialize database:**
   ```bash
   cd backend
   python -c "from app.db.database import init_db; init_db()"
   ```

6. **Start FastAPI:**
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Start Celery worker (in a separate terminal):**
   ```bash
   cd backend
   celery -A app.workers.tasks worker --loglevel=info --concurrency=4
   ```

#### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000

## 📁 Project Structure

```
resumeai/
├── backend/
│   └── app/
│       ├── api/              # FastAPI routes
│       ├── core/              # Configuration
│       ├── db/                # Database models
│       ├── services/          # Business logic
│       ├── workers/           # Celery tasks
│       ├── schemas/           # Pydantic schemas
│       ├── utils/             # Utilities
│       └── main.py            # FastAPI app
├── frontend/
│   └── src/
│       ├── components/        # React components
│       ├── pages/             # Page components
│       ├── services/          # API client
│       └── App.jsx            # Main app
├── storage/                   # File storage
│   ├── db/                    # SQLite database
│   ├── candidates/            # Candidate files
│   └── logs/                  # Application logs
├── docker-compose.yml
├── Dockerfile.api
├── Dockerfile.worker
└── requirements.txt
```

## 🔌 API Endpoints

### `POST /api/candidates/upload`
Upload 1-10 PDF resume files.

**Request:** Multipart form data with `files` field

**Response:**
```json
{
  "message": "Uploaded 3 resume(s)",
  "candidates": [
    {
      "id": "uuid",
      "filename": "resume.pdf",
      "status": "PENDING"
    }
  ]
}
```

### `GET /api/candidates`
List all candidates.

### `GET /api/candidates/{id}/status`
Get candidate status.

**Response:**
```json
{
  "id": "uuid",
  "status": "PROCESSING",
  "fit_score": null,
  "recommendation": null
}
```

### `GET /api/candidates/{id}/result`
Get full candidate result.

**Response:**
```json
{
  "id": "uuid",
  "status": "DONE",
  "fit_score": 8.5,
  "recommendation": "Interview",
  "summary_text": "2-page summary...",
  "raw_text": "Extracted text...",
  "structured_data": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "123-456-7890",
    "skills": ["Python", "React"]
  }
}
```

### `POST /api/candidates/{id}/re-evaluate`
Re-process a candidate.

### `GET /api/health`
Health check endpoint.

## 🔄 Processing Pipeline

1. **Upload:** PDF files are validated and saved to `/storage/candidates/<id>/`
2. **Enqueue:** Celery task is enqueued for each candidate
3. **Extract:** PDF text extraction (PyMuPDF → pdfminer → OCR)
4. **Parse:** Structured data extraction (name, email, phone, skills)
5. **Evaluate:** AI evaluation using OpenAI API
6. **Store:** Results saved to database and filesystem
7. **Complete:** Status updated to DONE

## 🛡️ Reliability Features

- **Isolation:** Each candidate has its own directory
- **Retry Logic:** Celery tasks retry on failure (max 3 retries)
- **Error Logging:** All errors logged to files and database
- **Transaction Safety:** SQLite with WAL mode and foreign keys
- **Timeout Protection:** Task timeouts prevent hanging processes

## 🧪 Testing

Run tests (when implemented):
```bash
cd backend
pytest
```

## 📝 Configuration

Key configuration options in `backend/app/core/config.py`:

- `MAX_FILES_PER_UPLOAD`: Maximum files per upload (default: 10)
- `MAX_UPLOAD_SIZE`: Maximum file size in bytes (default: 10MB)
- `OPENAI_MODEL`: OpenAI model to use (default: gpt-4o-mini)
- `JOB_DESCRIPTION`: Job description for evaluation

## 🐛 Troubleshooting

### Celery worker not processing tasks
- Check Redis is running: `redis-cli ping`
- Check worker logs: `docker-compose logs worker`
- Verify Celery connection: Check `CELERY_BROKER_URL`

### PDF extraction failing
- Ensure system dependencies are installed (poppler, tesseract)
- Check file is a valid PDF
- Review logs in `/storage/logs/`

### OpenAI API errors
- Verify `OPENAI_API_KEY` is set correctly
- Check API quota and billing
- Review error logs for specific error messages

## 📄 License

This project is provided as-is for MVP purposes.

## 🤝 Contributing

This is an MVP project. For production use, consider:
- Adding authentication/authorization
- Implementing proper error handling UI
- Adding unit and integration tests
- Setting up CI/CD pipeline
- Adding monitoring and alerting
- Implementing rate limiting
- Adding database migrations
- Optimizing for scale

