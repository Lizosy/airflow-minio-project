@echo off
REM Stop Airflow + MinIO Project (Windows)

echo.
echo Stopping Airflow + MinIO...
echo.

docker-compose down

echo.
echo =============================================
echo Services stopped successfully!
echo =============================================
echo.
echo To remove all data (volumes):
echo    docker-compose down -v
echo.

pause
