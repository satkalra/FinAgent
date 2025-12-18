# FinAgent Backend

Financial Agent powered by LLMs - Backend API

## Setup

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager

### Quick Setup

#### Option 1: Automated Setup (Recommended)

**macOS/Linux:**
```bash
./setup.sh
```

**Windows:**
```bash
setup.bat
```

#### Option 2: Manual Setup

1. Create virtual environment:
```bash
uv venv
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate.bat  # Windows
```

2. Install dependencies:
```bash
uv sync
```

3. Create `.env` file:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

4. Run the development server:
```bash
python -m app.main
```

Or with uvicorn directly:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Configuration
│   ├── database.py          # Database setup
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── api/routes/          # API endpoints
│   ├── services/            # Business logic
│   ├── tools/               # Financial tools for agent
│   └── core/                # Core utilities
├── pyproject.toml           # uv dependencies
└── .env                     # Environment variables
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

### Code formatting
```bash
black app/
ruff check app/
```
