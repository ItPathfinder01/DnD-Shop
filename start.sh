#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "▶ Запускаю базу данных..."
docker compose -f "$PROJECT_DIR/docker-compose.yml" up -d

echo "▶ Запускаю бэкенд..."
source "$PROJECT_DIR/venv/bin/activate"
cd "$PROJECT_DIR/backend"
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

echo "▶ Запускаю фронтенд..."
export NVM_DIR="$HOME/.nvm"
source "$NVM_DIR/nvm.sh"
nvm use --lts --silent
cd "$PROJECT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Всё запущено!"
echo "   Фронтенд: http://localhost:5173"
echo "   Бэкенд:   http://localhost:8000"
echo ""
echo "Для остановки нажми Ctrl+C"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; docker compose -f '$PROJECT_DIR/docker-compose.yml' stop" EXIT
wait
