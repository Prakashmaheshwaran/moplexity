# Moplexity Setup Guide

## Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- Docker and Docker Compose (for Docker deployment)

## Quick Setup

### Method 1: One-Command Local Setup

```bash
chmod +x setup.sh
./setup.sh
```

This will:
1. Check for Python and Node.js
2. Set up the backend virtual environment
3. Install all dependencies
4. Create configuration files
5. Initialize the database

### Method 2: Docker Setup

```bash
# 1. Copy environment file
cp backend/.env.example backend/.env

# 2. Edit .env and add your API keys
nano backend/.env  # or use your preferred editor

# 3. Start with Docker Compose
docker-compose up --build
```

## Configuration

### Required API Keys

At minimum, you need **one LLM API key**:

- **OpenAI**: Get from https://platform.openai.com/api-keys
  - Models: gpt-3.5-turbo, gpt-4, gpt-4-turbo-preview
- **Anthropic**: Get from https://console.anthropic.com/
  - Models: claude-3-sonnet, claude-3-opus
- **Google**: Get from https://makersuite.google.com/app/apikey
  - Models: gemini-pro

### Optional Search API Keys

Moplexity works with DuckDuckGo without any API keys, but you can add:

- **Bing Search**: https://www.microsoft.com/en-us/bing/apis/bing-web-search-api
- **Google Custom Search**: https://developers.google.com/custom-search/v1/overview

### Backend Configuration (.env)

Edit `backend/.env`:

```env
# Required: Choose your LLM
LITELLM_MODEL=gpt-3.5-turbo

# Required: At least one LLM API key
OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
# GOOGLE_API_KEY=AIza...

# Optional: Search APIs (DuckDuckGo works without these)
# BING_SEARCH_API_KEY=...
# GOOGLE_SEARCH_API_KEY=...
# GOOGLE_CSE_ID=...

# Database (SQLite by default)
DATABASE_URL=sqlite+aiosqlite:///./moplexity.db

# Server
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:5173
```

### Frontend Configuration

Configure in the app:
1. Go to Settings (⚙️)
2. Add your API keys (stored locally in browser)
3. Choose your preferred model
4. Enable/disable streaming and Pro Mode

## Running the Application

### Local Development

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Access at: http://localhost:5173

### Docker

```bash
docker-compose up
```

Access at: http://localhost:3000

### Production Deployment

```bash
# Build and start in detached mode
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Usage

### Basic Search

1. Type your question in the search bar
2. Press Enter or click Search
3. Wait for Moplexity to search and generate a response
4. View sources below the response

### Pro Mode

Enable Pro Mode for:
- More search results (15 vs 10)
- Deeper analysis
- More comprehensive answers

### Streaming Responses

Enable in Settings for real-time response generation.

### Conversation History

- All conversations are saved automatically
- Click on a conversation in the sidebar to load it
- Delete conversations with the × button

## Troubleshooting

### Backend Issues

**Database errors:**
```bash
cd backend
rm moplexity.db  # Delete and recreate
python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"
```

**API key errors:**
- Check that your .env file has valid API keys
- Ensure no extra spaces around the = sign
- Restart the backend after changing .env

**Import errors:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### Frontend Issues

**Build errors:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Proxy errors:**
- Ensure backend is running on port 8000
- Check vite.config.js proxy settings

### Docker Issues

**Build failures:**
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

**Permission errors:**
```bash
sudo chown -R $USER:$USER backend/data
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing Search Sources

### DuckDuckGo (Default)
- Works without API key
- Primary search source
- Good for general queries

### Bing Search
- Requires API key
- Fallback when DuckDuckGo insufficient
- Good for news and recent content

### Google Search
- Requires API key + Custom Search Engine ID
- Last resort fallback
- Requires setup at https://programmablesearchengine.google.com/

### Reddit RSS
- Works without API key
- Automatic for all queries
- Great for opinions and discussions

### YouTube Transcripts
- Works without API key
- Activated when query contains YouTube URL or "video"
- Extracts and analyzes video content

## Performance Tips

1. **Enable Search Cache**: Results cached for 1 hour
2. **Use Streaming**: Better UX with real-time responses
3. **Pro Mode**: Only when you need comprehensive answers
4. **Model Selection**: gpt-3.5-turbo is fastest and cheapest

## Security Notes

- API keys in backend/.env are server-side only
- Frontend settings stored in browser localStorage
- Never commit .env files to version control
- Use environment variables in production

## Getting Help

- Check the main README.md
- Review API docs at /docs
- Check logs: `docker-compose logs`
- Open an issue on GitHub

## Next Steps

1. Configure your API keys
2. Test with a simple query
3. Explore Pro Mode
4. Check out the Settings page
5. Review conversation history

Enjoy using Moplexity! 🚀

