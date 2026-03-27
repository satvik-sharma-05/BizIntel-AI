@echo off
echo Setting up BizIntel AI...

REM Backend setup
echo Setting up backend...
cd backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
cd ..

REM Frontend setup
echo Setting up frontend...
cd frontend
call npm install
echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local
cd ..

echo Setup complete!
echo.
echo To run the application:
echo 1. Backend: cd backend\app ^&^& python main.py
echo 2. Frontend: cd frontend ^&^& npm run dev
echo.
echo Access the app at http://localhost:3000
pause
