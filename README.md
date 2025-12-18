# FinAgent - AI-Powered Financial Agent

<div align="center">

**Autonomous AI financial analyst with ReAct reasoning, real-time streaming, and comprehensive evaluation system**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--5.2-412991?style=flat&logo=openai)](https://openai.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)

</div>

---

## 🎯 What is FinAgent?

FinAgent is a production-ready AI financial agent that uses the **ReAct pattern** (Reasoning + Acting) to autonomously answer financial queries. It selects tools, executes them, and provides grounded responses with full transparency into its reasoning process.

### Key Capabilities

✅ **Autonomous Tool Selection** - Agent decides which tools to use based on user queries

✅ **Real-Time Streaming** - See the agent think, act, and respond in real-time via SSE

✅ **Transparent Reasoning** - View step-by-step thought process and tool executions

✅ **Comprehensive Evaluation** - Test agent performance with CSV datasets and LLM-as-judge metrics

✅ **Multi-Tool Queries** - Handle complex queries requiring multiple tool calls

---

## 🚀 What Can FinAgent Do?

### 💬 Interactive Chat
Ask natural language questions about:
- **Stock Prices** - Current prices, historical data, price changes
- **Company Information** - Sector, industry, executives, headquarters
- **Financial Ratios** - P/E, ROE, ROA, profit margins, debt-to-equity
- **Investment Calculations** - Compound interest, future value projections
- **Historical Returns** - Calculate what past investments would be worth today

**Example Queries:**
- *"What's Apple's current stock price?"*
- *"Compare AAPL and MSFT financial ratios"*
- *"Get Tesla's stock price and company information"*
- *"If I invested $10,000 in Apple 3 years ago, what would it be worth today?"*
- *"What blue chip should I invest in today and why?"*

### 🧪 Agent Evaluation
Test your agent's performance with CSV datasets:
- **Tool Selection Accuracy** - Did it choose the right tools?
- **Argument Matching** - Did it extract parameters correctly?
- **Response Faithfulness** - Is the response grounded in tool outputs?

Upload CSV test cases and get detailed metrics with real-time streaming results.

[📖 Full Evaluation Guide](./EVALUATION.md)

### 📊 Live Agent Monitoring
Watch the agent work in real-time:
- See reasoning steps as they happen
- Track tool executions with timing
- Monitor response generation
- View complete conversation history

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern async Python web framework
- **OpenAI GPT-5.2** - ReAct agent with function calling
- **Pydantic** - Data validation and settings
- **yfinance** - Real-time financial data
- **SSE** - Server-sent events for streaming
- **Jinja2** - Prompt templating

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **@microsoft/fetch-event-source** - SSE with POST support
- **Recharts** - Charts and visualizations
- **Lucide React** - Icons

---

## ⚡ Quick Start

### Prerequisites
- **Python 3.11+**
- **Node.js 18+**
- **OpenAI API Key** - [Get one here](https://platform.openai.com/api-keys)

### 1. Setup Environment
```bash
# Create .env file in backend directory
cat > backend/.env << EOF
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5.2
EOF
```

### 2. Install Dependencies

**Backend:**
```bash
cd backend
uv venv 
```
Now virtual env is ready 

```bash
source .venv/bin/activate 
uv sync
```

**Frontend:**
```bash
cd ../frontend
npm install
```

### 3. Run the Application

To start both frontend and backend at same time

```bash
chmod +x ./start.sh
./start.sh
```

To run backend and frontend seperately

Open two terminal windows:

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload
```
Backend runs on: http://localhost:8000

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Frontend runs on: http://localhost:5173


### $. Access the Application

Open your browser and navigate to:
- **Chat Interface**: http://localhost:5173/
- **Evaluation System**: http://localhost:5173/evaluation
- **API Documentation**: http://localhost:8000/docs

---

## 📁 Project Structure

```
FinAgent/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI entry point
│   │   ├── config.py                  # Settings and configuration
│   │   ├── api/routes/
│   │   │   ├── chat.py                # Chat endpoints (deprecated)
│   │   │   ├── sse.py                 # Real-time streaming endpoint
│   │   │   └── evaluations.py         # Evaluation endpoint
│   │   ├── services/
│   │   │   ├── agent_service.py       # ReAct agent logic
│   │   │   ├── openai_service.py      # OpenAI API wrapper
│   │   │   ├── evaluation_service.py  # Evaluation orchestration
│   │   │   └── evaluation_metrics.py  # Metric evaluators
│   │   ├── tools/
│   │   │   ├── base.py                # Tool registry
│   │   │   ├── stock_price.py         # Stock price tool
│   │   │   ├── company_info.py        # Company info tool
│   │   │   ├── financial_ratios.py    # Financial ratios tool
│   │   │   ├── calculator.py          # Investment calculator
│   │   │   └── stock_returns.py       # Historical returns calculator
│   │   ├── prompts/
│   │   │   ├── fin_react_agent.j2     # ReAct agent prompt
│   │   │   ├── faithfulness_judge.j2  # LLM judge prompt
│   │   │   └── prompt_utils.py        # Template rendering
│   │   ├── schemas/
│   │   │   ├── message.py             # Chat schemas
│   │   │   └── evaluation.py          # Evaluation schemas
│   │   └── utils/
│   │       └── csv_parser.py          # CSV parsing for evaluations                          
│   └── .env                           # Environment variables
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx                    # Main app with routing
│   │   ├── components/
│   │   │   ├── chat/
│   │   │   │   ├── ChatInterface.tsx  # Main chat UI
│   │   │   │   ├── ChatMessage.tsx    # Message display
│   │   │   │   ├── ChatInput.tsx      # Input component
│   │   │   │   ├── StatusIndicator.tsx # Status updates
│   │   │   │   └── ThinkingStep.tsx   # Reasoning display
│   │   │   └── evaluation/
│   │   │       ├── FileUploader.tsx   # CSV upload
│   │   │       ├── EvaluationProgress.tsx # Progress bar
│   │   │       ├── TestCaseResult.tsx # Individual result
│   │   │       └── EvaluationSummary.tsx # Metrics summary
│   │   ├── pages/
│   │   │   └── EvaluationPage.tsx     # Evaluation interface
│   │   ├── hooks/
│   │   │   └── useEvaluationSSE.ts    # SSE hook
│   │   ├── services/
│   │   │   └── evaluationService.ts   # Evaluation API
│   │   └── types/
│   │       ├── index.ts               # Chat types
│   │       └── evaluation.ts          # Evaluation types
│   └── package.json
│
├── README.md                          # This file
├── EVALUATION.md                      # Evaluation guide
└── start.sh                           # Development startup script
```

---

## 🔧 Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| **get_stock_price** | Current/historical stock prices with start/end prices | `ticker`, `period` (optional), `info` (optional) |
| **get_company_info** | Company details, sector, industry | `ticker` |
| **calculate_financial_ratios** | P/E, PEG, ROE, ROA, margins | `ticker` |
| **calculate_investment_returns** | Compound interest calculations | `principal`, `annual_rate`, `years`, `monthly_contribution` (optional) |
| **calculate_stock_returns** | Historical investment returns calculator | `ticker`, `investment_amount`, `years_ago` or `start_date` |

---

## 📡 API Endpoints

### Chat & Streaming
- `POST /sse/chat` - Real-time streaming chat with SSE
  - Request body: JSON with `message` and `history`
  - Events: `status`, `thought`, `answer`, `content_chunk`
  - Uses `@microsoft/fetch-event-source` for POST support

### Evaluation
- `POST /evaluations/run` - Upload CSV and stream evaluation results
  - Accepts: CSV file with test cases
  - Returns: SSE stream with results
  - Events: `status`, `test_case_start`, `test_case_result`, `summary`, `error`

### Health
- `GET /` - Health check endpoint

## 🎓 How It Works

### ReAct Agent Flow

1. **Receive Query** - User asks a question
2. **Reasoning** - Agent analyzes what information is needed
3. **Tool Selection** - Chooses appropriate tools (can be multiple)
4. **Action** - Executes selected tools with extracted parameters
5. **Observation** - Receives tool outputs
6. **Iteration** - Repeats steps 2-5 if more information needed (max 10 iterations)
7. **Response** - Provides final answer grounded in tool outputs

All steps are streamed in real-time via SSE for full transparency.

### Evaluation Metrics

1. **Tool Selection** (0.0-1.0)
   - Single tool: 1.0 if correct, 0.0 otherwise
   - Multiple tools: % of expected tools called

2. **Argument Match** (0.0-1.0)
   - Field-level comparison with normalization
   - Case-insensitive strings, epsilon for floats
   - Average score across all tools

3. **Response Faithfulness** (0.0-1.0)
   - LLM-as-judge using GPT-4o
   - Evaluates grounding in tool outputs
   - Checks for expected content

**Overall Score** = Average of all three metrics
**Pass Threshold** = 0.7

---

## 🔒 Environment Variables

Create `backend/.env`:
```bash
# Required
OPENAI_API_KEY=sk-...

# Optional
OPENAI_MODEL=gpt-5.2              # Default: gpt-5.2
LOG_LEVEL=INFO                    # Default: INFO
CORS_ORIGINS=["http://localhost:5173"]  # Frontend URL
```

---

## 📚 Additional Documentation

- [📖 Evaluation Guide](./EVALUATION.md) - Detailed evaluation system documentation
- [🔗 API Documentation](http://localhost:8000/docs) - Interactive Swagger docs (when backend running)
- [🎨 Frontend README](./frontend/README.md) - Frontend-specific documentation

