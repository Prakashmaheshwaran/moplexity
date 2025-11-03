# Moplexity - Quick Start Reference

## 🚀 Fastest Way to Start

### Option 1: Docker (Recommended - 3 steps)
```bash
cd /Users/kash/Desktop/moplexity
cp backend/.env.example backend/.env
# Edit backend/.env and add your OPENAI_API_KEY
docker-compose up --build
```
**Open:** http://localhost:3000

### Option 2: Local Development (1 command)
```bash
cd /Users/kash/Desktop/moplexity
./setup.sh
```
Then run backend and frontend as shown in the output.

**Open:** http://localhost:5173

---

## 🔑 Minimum Required Configuration

Edit `backend/.env`:
```env
LITELLM_MODEL=gpt-3.5-turbo
OPENAI_API_KEY=sk-your-key-here
```

That's it! DuckDuckGo search works without additional API keys.

---

## 📝 Common Commands

### Docker
```bash
# Start
docker-compose up

# Start in background
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Rebuild
docker-compose up --build
```

### Local Development
```bash
# Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Frontend
cd frontend
npm run dev
```

---

## 🎯 Test Your Setup

1. **Open the app** (http://localhost:3000 or :5173)
2. **Ask a question**: "What is Python?"
3. **Check sources**: Scroll down to see search results
4. **Try Pro Mode**: Toggle in the header for more sources
5. **View history**: Check the sidebar for past conversations

---

## 🔧 Supported LLM Models

Just change `LITELLM_MODEL` in `.env`:

**OpenAI:**
- `gpt-3.5-turbo` (fast, cheap)
- `gpt-4` (best quality)
- `gpt-4-turbo-preview` (balanced)

**Anthropic:**
- `claude-3-sonnet-20240229`
- `claude-3-opus-20240229`

**Google:**
- `gemini-pro`

---

## 🔍 Search Sources (No API Keys Needed)

✅ **DuckDuckGo** - Primary web search
✅ **Reddit RSS** - Discussions and opinions
✅ **YouTube** - Video transcripts

**Optional (with API keys):**
- Bing Search
- Google Custom Search

---

## 📚 Full Documentation

- **README.md** - Complete overview
- **SETUP_GUIDE.md** - Detailed setup instructions
- **PROJECT_SUMMARY.md** - What was built
- **API Docs** - http://localhost:8000/docs

---

## ⚡ Pro Tips

1. **Streaming**: Enable in Settings for faster feedback
2. **Pro Mode**: Get 15 sources instead of 10
3. **Caching**: Search results cached for 1 hour
4. **Citations**: Click source numbers in responses
5. **History**: All conversations auto-saved

---

## 🆘 Quick Troubleshooting

**API Key Error:**
```bash
# Check your .env file
cat backend/.env
# Restart backend after changes
```

**Port Already in Use:**
```bash
# Change ports in docker-compose.yml or vite.config.js
```

**Database Issues:**
```bash
# Delete and recreate
cd backend
rm moplexity.db
# Database will be recreated on next start
```

---

## 🎉 You're Ready!

Your personal AI search engine is ready to use.

**Next:** Try asking a question and explore the sources!

