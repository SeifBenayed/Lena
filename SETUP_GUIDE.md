# Setup Guide for WhatsApp Restaurant Assistant

This guide will walk you through setting up all required API keys and services.

## Table of Contents

1. [SerpAPI Setup](#serpapi-setup)
2. [Anthropic Claude API Setup](#anthropic-claude-api-setup)
3. [WhatsApp Business API Setup](#whatsapp-business-api-setup)
4. [Local Development Setup](#local-development-setup)
5. [Production Deployment](#production-deployment)

---

## SerpAPI Setup

SerpAPI provides access to Google Places data for restaurant searches.

### Steps:

1. **Sign Up**
   - Go to [SerpAPI](https://serpapi.com/)
   - Click "Sign Up" and create an account

2. **Get API Key**
   - After logging in, go to your dashboard
   - Find your API key under "API Key" section
   - Copy the key

3. **Add to .env**
   ```env
   SERPAPI_API_KEY=your_api_key_here
   ```

4. **Free Tier**
   - 100 searches per month free
   - Upgrade if you need more

---

## Anthropic Claude API Setup

Claude AI powers the natural conversation capabilities.

### Steps:

1. **Sign Up**
   - Go to [Anthropic Console](https://console.anthropic.com/)
   - Create an account or sign in

2. **Get API Key**
   - Go to "API Keys" section
   - Click "Create Key"
   - Give it a name (e.g., "WhatsApp Bot")
   - Copy the API key (you won't see it again!)

3. **Add to .env**
   ```env
   ANTHROPIC_API_KEY=sk-ant-your_api_key_here
   ```

4. **Pricing**
   - Pay-per-token pricing
   - Check [Anthropic Pricing](https://www.anthropic.com/api) for current rates
   - Claude 3.5 Sonnet is recommended for best performance

---

## WhatsApp Business API Setup

### Prerequisites

- Facebook Business Account
- Meta Developer Account
- Phone number for WhatsApp Business

### Steps:

1. **Create Meta Developer Account**
   - Go to [Meta for Developers](https://developers.facebook.com/)
   - Sign in or create account

2. **Create a New App**
   - Click "Create App"
   - Select "Business" as app type
   - Fill in app details

3. **Add WhatsApp Product**
   - In app dashboard, click "Add Product"
   - Find "WhatsApp" and click "Set Up"

4. **Get Test Number (Development)**
   - Meta provides a test phone number
   - Add your personal WhatsApp number to test recipients

5. **Get API Credentials**

   **Phone Number ID:**
   - Go to WhatsApp > API Setup
   - Find "Phone number ID" - copy this
   - Already configured: `832096983319171`

   **WhatsApp Business Account ID:**
   - Found in WhatsApp > API Setup
   - Already configured: `727846363608348`

   **Access Token:**
   - In WhatsApp > API Setup
   - Find "Temporary access token" (valid 24 hours)
   - For production, generate permanent token:
     - Go to "System Users" in Business Settings
     - Create system user
     - Generate permanent token with `whatsapp_business_messaging` permission
   - Already configured temporarily

6. **Configure Webhook**

   **During Development (with ngrok):**
   ```bash
   # Install ngrok
   npm install -g ngrok
   # or download from https://ngrok.com/

   # Start ngrok
   ngrok http 8000
   ```

   - Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)
   - In Meta Dashboard:
     - WhatsApp > Configuration > Webhook
     - Callback URL: `https://abc123.ngrok.io/webhook`
     - Verify Token: `lena_restaurant_bot_2024` (or your custom token)
     - Click "Verify and Save"

   **Subscribe to Webhooks:**
   - Check "messages" field
   - Save

7. **Update .env**
   ```env
   WHATSAPP_PHONE_NUMBER_ID=832096983319171
   WHATSAPP_BUSINESS_ACCOUNT_ID=727846363608348
   WHATSAPP_ACCESS_TOKEN=your_token_here
   WHATSAPP_VERIFY_TOKEN=lena_restaurant_bot_2024
   ```

---

## Local Development Setup

### Option 1: Using Docker (Recommended)

```bash
# 1. Ensure .env is configured with all API keys
nano .env

# 2. Run setup script
./setup.sh

# 3. View logs
docker-compose logs -f

# 4. In another terminal, start ngrok
ngrok http 8000
```

### Option 2: Python Virtual Environment

```bash
# 1. Run local setup script
./run_local.sh

# 2. In another terminal, start ngrok
ngrok http 8000
```

### Testing the Setup

1. **Test Health Check**
   ```bash
   curl http://localhost:8000/
   ```

   Should return:
   ```json
   {
     "status": "running",
     "service": "WhatsApp Restaurant Assistant",
     "version": "1.0.0"
   }
   ```

2. **Test Webhook Verification**
   - After configuring webhook in Meta Dashboard
   - Meta will automatically verify
   - Check app logs for "Webhook verified successfully!"

3. **Send Test Message**
   - Send a WhatsApp message to your test number
   - Try: "Hi, I'm looking for Italian restaurants in Manhattan"
   - Bot should respond naturally

---

## Production Deployment

### Option 1: Cloud VM (AWS, GCP, Azure)

1. **Provision VM**
   - Ubuntu 22.04 or later
   - At least 1GB RAM
   - Open port 8000 (or use nginx reverse proxy on port 80/443)

2. **Install Docker**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

3. **Install Docker Compose**
   ```bash
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

4. **Clone and Deploy**
   ```bash
   git clone <your-repo>
   cd Lena
   nano .env  # Add production API keys
   ./setup.sh
   ```

5. **Set Up Domain & SSL**
   - Point domain to your VM IP
   - Use Certbot for SSL:
     ```bash
     sudo apt install certbot python3-certbot-nginx
     sudo certbot --nginx -d yourdomain.com
     ```

6. **Configure Nginx Reverse Proxy**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;

       location / {
           proxy_pass http://localhost:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

7. **Update WhatsApp Webhook**
   - Change webhook URL to: `https://yourdomain.com/webhook`

### Option 2: Railway.app

1. **Sign Up**
   - Go to [Railway.app](https://railway.app/)
   - Connect GitHub account

2. **Deploy**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway auto-detects Dockerfile

3. **Add Environment Variables**
   - In project settings > Variables
   - Add all environment variables from .env

4. **Get Public URL**
   - Railway provides HTTPS URL automatically
   - Use this URL for WhatsApp webhook

### Option 3: Heroku

1. **Install Heroku CLI**
   ```bash
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Login and Create App**
   ```bash
   heroku login
   heroku create whatsapp-restaurant-bot
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set WHATSAPP_PHONE_NUMBER_ID=832096983319171
   heroku config:set WHATSAPP_ACCESS_TOKEN=your_token
   # ... set all other variables
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

5. **Update Webhook**
   - Use Heroku app URL: `https://whatsapp-restaurant-bot.herokuapp.com/webhook`

---

## Troubleshooting

### Common Issues

**1. Webhook Verification Fails**
- Ensure verify token matches in .env and Meta Dashboard
- Check server is running and accessible
- Verify ngrok/domain is pointing to correct port

**2. "API Key Invalid" Errors**
- Double-check API keys in .env
- Ensure no extra spaces or quotes
- Verify API key is active in respective dashboard

**3. No Restaurant Results**
- Check SerpAPI credits
- Verify API key is correct
- Test SerpAPI directly: https://serpapi.com/playground

**4. AI Not Responding**
- Check Anthropic API key
- Verify you have API credits
- Check rate limits

**5. WhatsApp Token Expired**
- Temporary tokens expire in 24 hours
- Generate permanent system user token for production

---

## Support

- WhatsApp Business API: [Meta Documentation](https://developers.facebook.com/docs/whatsapp)
- SerpAPI: [Documentation](https://serpapi.com/docs)
- Anthropic: [API Documentation](https://docs.anthropic.com/)

---

## Next Steps

1. ✅ Get all API keys
2. ✅ Configure .env file
3. ✅ Run setup script
4. ✅ Test locally with ngrok
5. ✅ Deploy to production
6. ✅ Configure permanent WhatsApp webhook
7. 🚀 Start helping users find great restaurants!
