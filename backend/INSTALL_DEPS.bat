@echo off
echo ========================================
echo Installing MongoDB Dependencies
echo ========================================
echo.

pip install certifi dnspython

echo.
echo ========================================
echo Testing MongoDB Connection
echo ========================================
echo.

python test_mongo.py

echo.
echo ========================================
echo If test passed, start backend with:
echo python -m uvicorn app.main:app --reload
echo ========================================
pause
