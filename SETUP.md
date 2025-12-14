# FinAgent Setup Guide

Complete setup instructions for the FinAgent financial analyst chatbot.

## Prerequisites

- **Python 3.11+**
- **Node.js 18+** and npm
- **[uv](https://github.com/astral-sh/uv)** - Python package manager
- **OpenAI API Key** - Get one from [OpenAI Platform](https://platform.openai.com/)

## Quick Start

### 1. Install uv (if not installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Backend Setup

#### Option A: Automated Setup (Recommended)

```bash
cd backend

# macOS/Linux
./setup.sh

# Windows
setup.bat
```

#### Option B: Manual Setup

```bash
cd backend

# Create virtual environment with uv
uv venv
source .venv/bin/activate  # macOS/Linux
# or: .venv\Scripts\activate.bat  # Windows

# Install dependencies
uv pip install -e .

# Configure environment variables
nano .env  # Add your OPENAI_API_KEY

# Run the backend
python -m app.main
```

Backend will start at **http://localhost:8000**
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### 3. Frontend Setup

Open a **new terminal** and run:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will start at **http://localhost:5173**

## Configuration

### Backend (.env)

```env
# Required
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o

# Optional
DATABASE_URL=sqlite+aiosqlite:///./finagent.db
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
LOG_LEVEL=INFO
```

### Frontend (.env)

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_SSE_BASE_URL=http://localhost:8000/sse
```

## Testing the Application

1. **Open the frontend** at http://localhost:5173

2. **Try these example queries**:
   - "What's the current price of Apple stock?"
   - "Calculate the P/E ratio for TSLA"
   - "Compare AAPL and MSFT financial ratios"
   - "What are the key financial metrics for Microsoft?"

3. **Watch the React Agent in action**:
   - The agent will automatically decide which financial tools to use
   - Tool executions will be displayed in the chat
   - You'll see response times and token usage

## Features Implemented

### Backend
✅ FastAPI with async/await
✅ SQLite database with SQLAlchemy ORM
✅ React Agent pattern with OpenAI function calling
✅ 4 Financial tools:
  - get_stock_price (using yfinance)
  - get_company_info
  - calculate_financial_ratios
  - calculate_investment_returns
✅ SSE streaming for real-time updates
✅ Full REST API with CRUD operations
✅ Tool execution tracking
✅ Evaluation system
✅ Analytics endpoints

### Frontend
✅ React 18 + TypeScript + Vite
✅ Tailwind CSS styling
✅ Real-time chat interface
✅ Tool execution visualization
✅ Markdown support for rich responses
✅ Responsive design
✅ SSE integration (ready to use)

## API Endpoints

### Chat
- `POST /api/v1/chat/send` - Send message to agent

### Conversations
- `GET /api/v1/conversations` - List conversations
- `POST /api/v1/conversations` - Create conversation
- `GET /api/v1/conversations/{id}` - Get conversation
- `GET /api/v1/conversations/{id}/messages` - Get messages

### Analytics
- `GET /api/v1/analytics/overview` - Overall statistics
- `GET /api/v1/analytics/tool-usage` - Tool usage stats
- `GET /api/v1/analytics/quality-metrics` - Quality metrics

### SSE Streaming
- `GET /sse/chat/{conversation_id}?message=...` - Stream chat with real-time updates

## Project Structure

```
bardeen-chatbot/
├── backend/                   # FastAPI backend
│   ├── app/
│   │   ├── main.py           # Entry point
│   │   ├── config.py         # Settings
│   │   ├── database.py       # Database setup
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── api/routes/       # API endpoints
│   │   ├── services/         # Business logic
│   │   │   ├── agent_service.py     # React Agent
│   │   │   ├── openai_service.py    # OpenAI integration
│   │   │   └── conversation_service.py
│   │   ├── tools/            # Financial tools
│   │   │   ├── base.py
│   │   │   ├── stock_price.py
│   │   │   ├── company_info.py
│   │   │   ├── financial_ratios.py
│   │   │   └── calculator.py
│   │   └── core/             # Core utilities
│   │       └── sse_manager.py
│   └── pyproject.toml
│
└── frontend/                  # React frontend
    ├── src/
    │   ├── main.tsx
    │   ├── App.tsx
    │   ├── components/
    │   │   └── chat/
    │   │       ├── ChatInterface.tsx
    │   │       ├── ChatMessage.tsx
    │   │       └── ChatInput.tsx
    │   ├── hooks/
    │   │   └── useSSE.ts
    │   ├── services/
    │   │   ├── api.ts
    │   │   └── chatService.ts
    │   └── types/
    │       └── index.ts
    └── package.json
```

## Troubleshooting

### Backend Issues

**"ModuleNotFoundError"**
```bash
# Make sure you're in the backend directory and run:
uv pip install -e .
```

**"OpenAI API Error"**
- Check that your OPENAI_API_KEY is set correctly in backend/.env
- Ensure you have credits in your OpenAI account

**"Database locked"**
- Close any other instances of the backend
- Delete finagent.db and restart

### Frontend Issues

**"Cannot connect to backend"**
- Ensure backend is running on port 8000
- Check VITE_API_BASE_URL in frontend/.env

**"npm install fails"**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Development

### Backend Development

```bash
cd backend

# Run with auto-reload
python -m app.main

# Run tests (when available)
pytest

# Code formatting
black app/
ruff check app/
```

### Frontend Development

```bash
cd frontend

# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint
npm run lint
```

## Next Steps

Now that everything is set up, you can:

1. **Customize the financial tools** - Add more tools in `backend/app/tools/`
2. **Enhance the UI** - Add more features to the frontend
3. **Add the evaluation dashboard** - Implement the full evaluation system
4. **Add the analytics dashboard** - Build charts with Recharts
5. **Deploy** - Deploy to production (Render, Vercel, etc.)

## Support

For issues or questions:
- Backend API Docs: http://localhost:8000/docs
- Check logs in terminal for error messages
- Review the plan at `.claude/plans/luminous-orbiting-moore.md`

Happy coding! 🚀
