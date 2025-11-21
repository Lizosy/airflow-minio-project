@echo off
REM Build and Start Airflow + MinIO with Custom Image

echo.
echo ============================================
echo Building Custom Airflow Image with Chrome
echo ============================================
echo.

REM Stop existing containers
echo Stopping existing containers...
docker-compose down

echo.
echo Building custom image (this may take 5-10 minutes)...
docker-compose build

echo.
echo Starting services...
docker-compose up -d

echo.
echo =============================================
echo Services started successfully!
echo =============================================
echo.
echo Airflow Web UI:    http://localhost:8080
echo    Username: airflow
echo    Password: airflow
echo.
echo MinIO Console:     http://localhost:9001
echo    Username: minioadmin
echo    Password: minioadmin
echo =============================================
echo.
echo Waiting for services to be ready...
echo (This may take 1-2 minutes)
echo.

timeout /t 30 /nobreak > nul

docker-compose ps

echo.
echo View logs: docker-compose logs -f
echo.

pause
