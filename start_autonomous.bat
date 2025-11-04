@echo off
REM Autonomous Detection System Startup Script
REM No manual uploads - full automation only

echo ================================================
echo   SKYHAWK AUTONOMOUS DETECTION SYSTEM
echo ================================================
echo.
echo Mode: FULLY AUTOMATED
echo Flow: RTSP --^> Capture --^> YOLO --^> Database --^> Map
echo.
echo Starting services...
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM Navigate to backend
cd backend

REM Start all services with docker-compose
echo [1/4] Starting PostgreSQL database...
docker-compose up -d postgres
timeout /t 5 /nobreak >nul

echo [2/4] Starting ML inference service...
docker-compose up -d ml-service
timeout /t 10 /nobreak >nul

echo [3/4] Starting API services...
docker-compose up -d api-service agent-service
timeout /t 5 /nobreak >nul

echo [4/4] Starting AUTONOMOUS CAPTURE SERVICE...
docker-compose up -d capture-service

echo.
echo ================================================
echo   ALL SERVICES STARTED!
echo ================================================
echo.
echo Capture Service: MONITORING RTSP STREAMS
echo ML Service: READY FOR INFERENCE
echo Database: STORING DETECTIONS
echo Frontend: http://localhost:5000/monitoring
echo.
echo Detections will appear automatically on the map!
echo.
echo Press Ctrl+C to view logs, or close this window.
echo.

REM Follow logs
docker-compose logs -f capture-service

cd ..
