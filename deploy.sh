#!/bin/bash
# DataAssist Deployment Script

set -e

echo "🚀 DataAssist Deployment Script"
echo "================================"

# Function to display usage
usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build     - Build the Docker image"
    echo "  start     - Start the application"
    echo "  stop      - Stop the application"
    echo "  restart   - Restart the application"
    echo "  logs      - View application logs"
    echo "  clean     - Clean up containers and images"
    echo "  status    - Check application status"
    echo ""
    exit 1
}

# Build the Docker image
build() {
    echo "📦 Building DataAssist Docker image..."
    docker build -t dataassist:latest .
    echo "✅ Build complete!"
}

# Start the application
start() {
    echo "🚀 Starting DataAssist..."
    docker-compose up -d
    sleep 3
    echo "✅ DataAssist started!"
    status
}

# Stop the application
stop() {
    echo "🛑 Stopping DataAssist..."
    docker-compose down
    echo "✅ DataAssist stopped!"
}

# Restart the application
restart() {
    echo "🔄 Restarting DataAssist..."
    stop
    start
}

# View logs
logs() {
    echo "📋 DataAssist Logs:"
    docker-compose logs -f web
}

# Clean up
clean() {
    echo "🧹 Cleaning up Docker resources..."
    docker-compose down
    docker image prune -f
    docker container prune -f
    echo "✅ Cleanup complete!"
}

# Check status
status() {
    echo "📊 DataAssist Status:"
    echo "====================="
    docker-compose ps
    echo ""
    if curl -s -I http://localhost:8000 | grep -q "200 OK"; then
        echo "🟢 Application: RUNNING"
        echo "🌐 URL: http://localhost:8000"
    else
        echo "🔴 Application: NOT RESPONDING"
    fi
}

# Main script logic
case "${1:-}" in
    build)
        build
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        logs
        ;;
    clean)
        clean
        ;;
    status)
        status
        ;;
    *)
        usage
        ;;
esac
