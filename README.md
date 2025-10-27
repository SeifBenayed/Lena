# WhatsApp Restaurant Assistant

An AI-powered WhatsApp bot that provides natural, conversational restaurant recommendations using Claude AI, Google Places (via SerpAPI), and WhatsApp Business API.

## Features

- **Natural Conversations**: Powered by Claude AI for human-like interactions
- **Restaurant Search**: Real-time restaurant data from Google Places via SerpAPI
- **Location Sharing**: Sends restaurant locations directly in WhatsApp
- **Context Awareness**: Remembers conversation history for better recommendations
- **Docker Ready**: Easy deployment with Docker and Docker Compose
- **Scalable**: Built with FastAPI for high performance

## Architecture

```
User (WhatsApp) → WhatsApp Business API → FastAPI Webhook
                                              ↓
                                    AI Handler (Claude)
                                              ↓
                                    Restaurant Search (SerpAPI)
                                              ↓
                                    Response → WhatsApp User
```

## Prerequisites

- Python 3.11+
- Docker and Docker Compose (for containerized deployment)
- WhatsApp Business API Account
- SerpAPI Account
- Anthropic API Key (Claude)

## Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd Lena
```

### 2. Set Up Environment Variables

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your actual credentials:

```env
# WhatsApp Business API Configuration
WHATSAPP_PHONE_NUMBER_ID=832096983319171
WHATSAPP_BUSINESS_ACCOUNT_ID=727846363608348
WHATSAPP_ACCESS_TOKEN=your_actual_token_here
WHATSAPP_VERIFY_TOKEN=your_custom_verify_token_here

# SerpAPI Configuration
SERPAPI_API_KEY=your_serpapi_key_here

# Anthropic Claude API Configuration
ANTHROPIC_API_KEY=your_anthropic_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
```

### 3. Run with Docker (Recommended)

```bash
# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

### 4. Run Locally (Development)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

The server will start at `http://localhost:8000`

## WhatsApp Business API Setup

### 1. Configure Webhook URL

In your Meta Developer Dashboard:

1. Go to WhatsApp > Configuration
2. Set Webhook URL: `https://your-domain.com/webhook`
3. Set Verify Token: Same as `WHATSAPP_VERIFY_TOKEN` in your `.env`
4. Subscribe to webhook fields: `messages`

### 2. Expose Local Server (Development)

For local testing, use ngrok or similar:

```bash
ngrok http 8000
```

Use the ngrok URL as your webhook URL.

## API Endpoints

### Health Check
```
GET /
```
Returns service status and version.

### Webhook Verification
```
GET /webhook
```
Handles WhatsApp webhook verification.

### Message Handler
```
POST /webhook
```
Receives and processes incoming WhatsApp messages.

### Reset Conversation
```
POST /reset-conversation/{phone_number}
```
Clears conversation history for a specific user.

## Usage Examples

Once deployed, users can interact with the bot naturally via WhatsApp:

**Example Conversations:**

```
User: Hey, I'm looking for Italian food
Bot: Great choice! I'd love to help you find some excellent Italian restaurants.
     What area or city are you in?

User: I'm in Manhattan
Bot: Perfect! Let me search for the best Italian restaurants in Manhattan for you!

     Here are some great restaurant recommendations:

     1. *Carbone*
        ⭐ 4.5 (1200 reviews)
        📍 Italian Restaurant
        💰 $$$$
        📌 181 Thompson St, New York, NY
        📞 (212) 254-3000

     [Location sent]
```

```
User: Any good sushi places near Times Square?
Bot: Let me find the best sushi restaurants near Times Square for you!

     [Restaurant recommendations...]
```

## How It Works

1. **User sends message** via WhatsApp
2. **WhatsApp Business API** forwards message to your webhook
3. **AI Handler** (Claude) processes the message and determines intent
4. If restaurant search is needed:
   - **SerpAPI Handler** searches Google Places
   - Results are formatted and combined with AI response
5. **Response sent** back to user via WhatsApp Business API
6. **Location shared** (if available) for the top recommendation

## Configuration

### AI Behavior

Modify the system prompt in `ai_handler.py` to customize the AI's personality and behavior:

```python
def _build_system_prompt(self) -> str:
    return """Your custom system prompt here..."""
```

### Search Results

Adjust the number of restaurant recommendations in `main.py`:

```python
restaurants = restaurant_handler.search_restaurants(
    query=query,
    location=location,
    max_results=5  # Change this number
)
```

## Development

### Project Structure

```
.
├── main.py                 # FastAPI application
├── config.py              # Configuration and settings
├── whatsapp_handler.py    # WhatsApp API integration
├── serpapi_handler.py     # Restaurant search logic
├── ai_handler.py          # AI conversation handling
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker container definition
├── docker-compose.yml    # Docker Compose configuration
├── .env.example          # Environment variables template
└── README.md             # This file
```

### Adding Features

**Add new message types:**
Edit `whatsapp_handler.py` to handle images, documents, etc.

**Customize restaurant search:**
Modify `serpapi_handler.py` to add filters, sorting, or different data sources.

**Enhance AI responses:**
Update system prompts and conversation logic in `ai_handler.py`.

## Monitoring and Logs

View application logs:

```bash
# Docker
docker-compose logs -f whatsapp-assistant

# Local
# Logs will appear in the console
```

## Troubleshooting

### Webhook Verification Fails
- Ensure `WHATSAPP_VERIFY_TOKEN` matches in both `.env` and Meta Dashboard
- Check that your server is publicly accessible

### Messages Not Received
- Verify webhook is subscribed to `messages` field
- Check WhatsApp Business API configuration
- Review application logs for errors

### Restaurant Search Returns No Results
- Verify SerpAPI key is valid and has credits
- Check search query format
- Review SerpAPI dashboard for API usage

### AI Responses Are Slow
- Check Anthropic API status
- Consider reducing `max_tokens` in `ai_handler.py`
- Implement caching for common queries

## Security Best Practices

1. **Never commit `.env` file** - It's already in `.gitignore`
2. **Rotate access tokens regularly** - Update in Meta Dashboard and `.env`
3. **Use HTTPS in production** - Required for WhatsApp webhooks
4. **Implement rate limiting** - Add rate limiting middleware to prevent abuse
5. **Validate webhook signatures** - Add WhatsApp signature validation

## Performance Optimization

1. **Implement caching** - Cache frequent restaurant searches
2. **Database integration** - Store conversation history in Redis/PostgreSQL
3. **Async processing** - Use background tasks for long operations
4. **Load balancing** - Use multiple instances with a load balancer

## API Keys and Credits

### WhatsApp Business API
- Free tier available with limited messages
- Check Meta's pricing for production usage

### SerpAPI
- Free tier: 100 searches/month
- Paid plans available for higher volume

### Anthropic Claude API
- Pay-per-token pricing
- See Anthropic's pricing page for details

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review WhatsApp Business API documentation

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- AI powered by [Anthropic Claude](https://www.anthropic.com/)
- Restaurant data from [SerpAPI](https://serpapi.com/)
- Messaging via [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)

---

Made with ❤️ for restaurant lovers everywhere!
