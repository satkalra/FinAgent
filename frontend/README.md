# FinAgent Frontend

React + TypeScript frontend for FinAgent financial analyst chatbot.

## Setup

1. **Install dependencies**:
```bash
npm install
```

2. **Configure environment**:
```bash
# Copy .env file and configure API URLs
cp .env.example .env
```

3. **Run development server**:
```bash
npm run dev
```

Frontend will be available at http://localhost:5173

## Features

- Real-time chat with AI financial analyst
- Tool execution visualization
- Markdown support for rich responses
- Responsive design with Tailwind CSS
- SSE streaming support (ready for Phase 5)

## Tech Stack

- React 18
- TypeScript
- Vite
- Tailwind CSS
- Zustand (state management)
- Axios (API client)
- React Markdown
- Lucide React (icons)

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
