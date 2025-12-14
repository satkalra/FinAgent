# FinAgent - Financial Agent Powered by LLMs

AI-powered financial analyst chatbot with React Agent implementation, featuring real-time tool execution and evaluation capabilities.

## Features

- **React Agent Pattern**: OpenAI function calling with autonomous tool selection
- **Financial Tools**: Stock prices, company info, financial ratios, investment calculations
- **Real-time Streaming**: SSE for live updates including thinking, tool calls, and responses
- **Evaluation System**: Rate and analyze AI response quality
- **Analytics Dashboard**: Track usage, tool performance, and quality metrics

## Tech Stack

**Backend:**
- FastAPI + Python 3.11+
- OpenAI GPT-4 with function calling
- SQLite + SQLAlchemy (async)
- uv package manager
- SSE for streaming

**Frontend:**
- React 18 + TypeScript
- Vite
- Tailwind CSS + shadcn/ui
- Zustand state management
- Recharts for analytics

## Quick Start

### Backend Setup

1. **Install uv** (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **Navigate to backend and install dependencies**:
```bash
cd backend
uv pip install -e .
```

3. **Configure environment**:
```bash
# Edit backend/.env and add your OpenAI API key
nano .env
```

4. **Run the backend**:
```bash
python -m app.main
```

Backend will be available at http://localhost:8000
- API docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Frontend Setup

(Coming soon - will be implemented in Phase 6-7)

## Project Structure

```
bardeen-chatbot/
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── main.py       # Entry point
│   │   ├── models/       # Database models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── api/routes/   # API endpoints
│   │   ├── services/     # Business logic
│   │   ├── tools/        # Financial tools
│   │   └── core/         # Core utilities
│   ├── pyproject.toml    # Dependencies
│   └── .env              # Configuration
│
└── frontend/             # React frontend (TBD)
```

## API Endpoints

### Chat
- `POST /api/v1/chat/send` - Send message and get AI response with tool execution

### Conversations
- `GET /api/v1/conversations` - List conversations
- `POST /api/v1/conversations` - Create conversation
- `GET /api/v1/conversations/{id}` - Get conversation
- `GET /api/v1/conversations/{id}/messages` - Get messages

### Evaluations
- `POST /api/v1/evaluations` - Create evaluation
- `GET /api/v1/evaluations` - List evaluations

### Analytics
- `GET /api/v1/analytics/overview` - Overall statistics
- `GET /api/v1/analytics/tool-usage` - Tool usage stats
- `GET /api/v1/analytics/quality-metrics` - Quality metrics

### SSE Streaming
- `GET /sse/chat/{conversation_id}` - Stream chat with real-time updates

## Available Tools

1. **get_stock_price** - Get current/historical stock prices
2. **get_company_info** - Company details, sector, executives
3. **calculate_financial_ratios** - P/E, ROE, margins, debt ratios
4. **calculate_investment_returns** - Compound interest calculator

## Development

### Running tests
```bash
cd backend
pytest
```

### Code formatting
```bash
black app/
ruff check app/
```

## License

MIT
