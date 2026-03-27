@echo off
echo ========================================
echo  BizIntel AI - Push to GitHub
echo ========================================
echo.

REM Check if git is initialized
if not exist .git (
    echo Initializing Git repository...
    git init
    echo.
)

REM Add all files
echo Adding files to Git...
git add .
echo.

REM Commit
echo Enter commit message (or press Enter for default):
set /p COMMIT_MSG="Commit message: "
if "%COMMIT_MSG%"=="" set COMMIT_MSG=Update BizIntel AI

echo Committing changes...
git commit -m "%COMMIT_MSG%"
echo.

REM Check if remote exists
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo Adding GitHub remote...
    git remote add origin https://github.com/satvik-sharma-05/BizIntel-AI.git
    echo.
)

REM Push to GitHub
echo Pushing to GitHub...
git branch -M main
git push -u origin main
echo.

echo ========================================
echo  Successfully pushed to GitHub!
echo  Visit: https://github.com/satvik-sharma-05/BizIntel-AI
echo ========================================
echo.
pause
