#!/bin/bash

echo "🤖 WhatsApp Restaurant Assistant Setup"
echo "======================================"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ .env file created!"
    echo ""
    echo "⚠️  Please edit .env and add your API keys:"
    echo "   - SERPAPI_API_KEY"
    echo "   - ANTHROPIC_API_KEY"
    echo ""
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo "📥 Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed!"
    echo "📥 Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Build and start the container
echo "🔨 Building Docker image..."
docker-compose build

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
    echo ""
    echo "🚀 Starting the application..."
    docker-compose up -d

    if [ $? -eq 0 ]; then
        echo "✅ Application started successfully!"
        echo ""
        echo "📊 Application is running at: http://localhost:8000"
        echo ""
        echo "📝 Next steps:"
        echo "   1. Expose your local server using ngrok:"
        echo "      ngrok http 8000"
        echo ""
        echo "   2. Configure WhatsApp webhook in Meta Developer Dashboard:"
        echo "      - Webhook URL: https://your-ngrok-url.ngrok.io/webhook"
        echo "      - Verify Token: lena_restaurant_bot_2024"
        echo ""
        echo "   3. View logs:"
        echo "      docker-compose logs -f"
        echo ""
        echo "   4. Stop the application:"
        echo "      docker-compose down"
        echo ""
    else
        echo "❌ Failed to start the application!"
        exit 1
    fi
else
    echo "❌ Failed to build Docker image!"
    exit 1
fi
