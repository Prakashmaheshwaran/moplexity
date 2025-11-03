# Moplexity

A powerful Perplexity clone with configurable LLM APIs, multi-source search, and full control over your AI search experience.

## Features

- 🔍 **Multi-Source Search**: Cascading search through DuckDuckGo, Bing, and Google
- 📺 **YouTube Transcripts**: Extract and search through video transcripts
- 💬 **Reddit Integration**: Search Reddit discussions via RSS feeds
- 🤖 **Flexible AI Models**: Use any LLM via LiteLLM (OpenAI, Anthropic, Google, etc.)
- 💾 **Conversation History**: All chats and sources stored in SQLite
- ⚡ **Streaming Responses**: Real-time AI responses
- 🎨 **Clean Interface**: Simple, functional UI built with Vue.js
- 🐳 **Easy Deployment**: Docker and Docker Compose support

## Quick Start

### Option 1: Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd moplexity
```

2. Set up your API keys:
```bash
cp backend/.env.example backend/.env
# Edit backend/.env and add your API keys
```

3. Start with Docker Compose:
```bash
docker-compose up --build
```

4. Open http://localhost:3000 in your browser

### Option 2: Local Development

1. Run the setup script:
```bash
chmod +x setup.sh
./setup.sh
```

2. Start the backend:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

3. Start the frontend (in a new terminal):
```bash
cd frontend
npm run dev
```

4. Open http://localhost:5173 in your browser

## Configuration

### Backend Configuration

Edit `backend/.env`:

```env
# LLM Configuration
LITELLM_MODEL=gpt-3.5-turbo
OPENAI_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here
# GOOGLE_API_KEY=your_key_here

# Optional Search APIs
# BING_SEARCH_API_KEY=your_key_here
# GOOGLE_SEARCH_API_KEY=your_key_here
# GOOGLE_CSE_ID=your_cse_id_here
```

### Frontend Configuration

Configure API keys and preferences in the Settings page (⚙️ Settings).

### Supported LLM Models

- OpenAI: `gpt-3.5-turbo`, `gpt-4`, `gpt-4-turbo-preview`
- Anthropic: `claude-3-sonnet-20240229`, `claude-3-opus-20240229`
- Google: `gemini-pro`
- And many more via LiteLLM

## Architecture

### Backend (FastAPI + Python)

- **FastAPI**: Modern async web framework
- **LiteLLM**: Universal LLM API interface
- **SQLAlchemy**: Database ORM with SQLite
- **Search Services**: DuckDuckGo, Bing, Google, Reddit RSS, YouTube transcripts

### Frontend (Vue.js)

- **Vue 3**: Composition API
- **Vite**: Fast build tool
- **Pinia**: State management
- **Marked**: Markdown rendering

### Database Schema

- **conversations**: Chat conversations
- **messages**: User and AI messages
- **sources**: Search results and citations
- **search_cache**: Cached search results (1 hour TTL)

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Features in Detail

### Multi-Source Search

Moplexity implements a cascading search strategy:

1. **DuckDuckGo** (primary, no API key needed)
2. **Bing Search** (fallback, if API key provided)
3. **Google Search** (last resort, if API key provided)
4. **Reddit RSS** (parallel, for discussion threads)
5. **YouTube Transcripts** (for video content)

### Pro Mode

Enable Pro Mode for:
- More search results (15 vs 10)
- Deeper analysis
- More comprehensive answers

### Streaming Responses

Real-time AI responses using Server-Sent Events (SSE) for a better user experience.

## Development

### Project Structure

```
moplexity/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   ├── services/         # Business logic
│   │   ├── models.py         # Database models
│   │   ├── schemas.py        # Pydantic schemas
│   │   └── main.py           # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/       # Vue components
│   │   ├── views/            # Page views
│   │   ├── stores/           # Pinia stores
│   │   └── main.js
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── setup.sh
```

### Running Tests

```bash
# Backend tests (coming soon)
cd backend
pytest

# Frontend tests (coming soon)
cd frontend
npm test
```

## Deployment

### Production Deployment

1. Update `.env` with production values
2. Build and deploy with Docker Compose:

```bash
docker-compose -f docker-compose.yml up -d
```

3. Set up a reverse proxy (nginx/Caddy) for HTTPS
4. Configure your domain to point to the server

### Environment Variables

See `backend/.env.example` for all available configuration options.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for any purpose.

## Acknowledgments

- Inspired by [Perplexity AI](https://www.perplexity.ai/)
- Built with [LiteLLM](https://github.com/BerriAI/litellm)
- Search powered by DuckDuckGo, Bing, and Google

## Support

For issues and questions, please open an issue on GitHub.

---

**Note**: This project requires API keys for LLM providers. DuckDuckGo search works without an API key, but Bing and Google search require their respective API keys.

