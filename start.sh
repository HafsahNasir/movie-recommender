#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

# Start backend
cd "$ROOT/backend"
python app.py &
BACKEND_PID=$!

# Start frontend
cd "$ROOT/frontend"
npm run dev &
FRONTEND_PID=$!

# Open browser once frontend is ready
sleep 3
open http://localhost:5173

echo ""
echo "Movie Recommender is running."
echo "  Backend:  http://localhost:5001"
echo "  Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers."

# On Ctrl+C, kill both
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
