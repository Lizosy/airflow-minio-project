#!/bin/bash

# Start Airflow + MinIO Project
# Windows users: Use Git Bash or WSL to run this script

echo "🚀 Starting Airflow + MinIO..."

# Create necessary directories
mkdir -p ./logs ./dags ./plugins ./config

# Set permissions (Linux/Mac only)
if [[ "$OSTYPE" != "msys" && "$OSTYPE" != "win32" ]]; then
    echo "📝 Setting permissions..."
    chmod -R 777 ./logs
    chmod -R 755 ./dags
    chmod -R 755 ./plugins
fi

# Start Docker Compose
echo "🐳 Starting Docker containers..."
docker-compose up -d

echo ""
echo "✅ Services started!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Airflow Web UI:    http://localhost:8080"
echo "   Username: airflow"
echo "   Password: airflow"
echo ""
echo "💾 MinIO Console:     http://localhost:9001"
echo "   Username: minioadmin"
echo "   Password: minioadmin"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⏳ Waiting for services to be ready..."
echo "   (This may take 1-2 minutes on first startup)"
echo ""

# Wait for services
sleep 30

# Check status
docker-compose ps

echo ""
echo "💡 Tips:"
echo "   - View logs: docker-compose logs -f"
echo "   - Stop services: docker-compose down"
echo "   - Restart: docker-compose restart"
echo ""
