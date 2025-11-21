@echo off
REM Start Airflow + MinIO Project (Windows)

echo.
echo Starting Airflow + MinIO...
echo.

REM Create necessary directories
if not exist "logs" mkdir logs
if not exist "dags" mkdir dags
if not exist "plugins" mkdir plugins
if not exist "config" mkdir config

REM Start Docker Compose
echo Starting Docker containers...
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
echo (This may take 1-2 minutes on first startup)
echo.

REM Wait for services
timeout /t 30 /nobreak > nul

REM Check status
docker-compose ps

echo.
echo Tips:
echo    - View logs: docker-compose logs -f
echo    - Stop services: docker-compose down
echo    - Restart: docker-compose restart
echo.

pause
