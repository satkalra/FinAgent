#!/bin/bash

echo "🚀 Starting FinAgent..."
echo ""

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "❌ Error: backend/.env file not found!"
    echo ""
    echo "Please create backend/.env with your OpenAI API key:"
    echo ""
    echo "cat > backend/.env << EOF"
    echo "OPENAI_API_KEY=your_api_key_here"
    echo "OPENAI_MODEL=gpt-4o"
    echo "EOF"
    echo ""
    exit 1
fi

# Start backend in background
echo "📡 Starting backend server..."
cd backend && uvicorn app.main:app --reload > /dev/null 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to be ready
echo "⏳ Waiting for backend to start..."
sleep 3

# Check if backend started successfully
if ! curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "❌ Backend failed to start!"
    echo "Check backend logs for errors"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo "✅ Backend running on http://localhost:8000"

# Start frontend in background
echo "🎨 Starting frontend server..."
cd frontend && npm run dev > /dev/null 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to be ready
echo "⏳ Waiting for frontend to start..."
sleep 5

if ! curl -s http://localhost:5173/ > /dev/null 2>&1; then
    echo "❌ Frontend failed to start!"
    echo "Check frontend logs for errors"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 1
fi

echo "✅ Frontend running on http://localhost:5173"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  FinAgent is ready! 🎉"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  💬 Chat Interface:    http://localhost:5173/"
echo "  🧪 Evaluation System: http://localhost:5173/evaluation"
echo "  📖 API Documentation: http://localhost:8000/docs"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT

# Wait for user to press Ctrl+C
wait
