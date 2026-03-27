#!/bin/bash

echo "🚀 Starting BizIntel AI..."

# Start backend
echo "Starting backend..."
cd backend/app
python main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Start frontend
echo "Starting frontend..."
cd ../../frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ BizIntel AI is running!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
