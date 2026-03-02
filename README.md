# AI Competitive Intelligence Research Tool

An automated competitive intelligence system that generates comprehensive market research reports for SaaS product ideas. Built with FastAPI, Celery, and AI-powered web search.

## Features

- **AI-Powered Research**: Uses LLMs (Gemini 3 Flash, GPT-OSS 120B) via OpenRouter to generate targeted search queries and analyze results
- **Automated Web Search**: Leverages Tavily API for advanced web search with raw content extraction
- **Async Processing**: Celery tasks handle long-running research jobs asynchronously with Redis as broker
- **PDF Report Generation**: Produces professional, boardroom-ready competitive intelligence reports in PDF format
- **REST API**: Simple HTTP endpoint to submit research requests

## Tech Stack

| Component | Technology |
|-----------|------------|
| Web Framework | FastAPI |
| Task Queue | Celery |
| Message Broker | Redis |
| AI Models | OpenRouter (Gemini 3 Flash, GPT-OSS 120B) |
| Web Search | Tavily API |
| PDF Generation | WeasyPrint |
| Python Version | >= 3.13 |

## Project Structure

```
.
├── app/
│   ├── main.py                 # FastAPI application & API endpoints
│   ├── celery_app.py           # Celery configuration
│   ├── modules/
│   │   └── research/
│   │       ├── tasks.py        # Celery task definitions
│   │       ├── methods.py      # Research logic (query gen, search, report)
│   │       ├── schema.py       # Pydantic models
│   │       └── prompt.py       # LLM system prompts
│   └── utils/
│       ├── openai.py           # OpenRouter/OpenAI client setup
│       └── tavily.py           # Tavily client setup
├── pyproject.toml              # Project dependencies
├── Makefile                    # Development commands
└── .env                        # Environment variables (not in git)
```

## Prerequisites

1. **Python 3.13+**
2. **Redis** - Install and run Redis locally:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install redis-server
   sudo service redis-server start

   # macOS (Homebrew)
   brew install redis
   brew services start redis

   # Docker
   docker run -d -p 6379:6379 redis:latest
   ```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd assignment-4
   ```

2. **Install dependencies with uv**:
   ```bash
   uv sync
   ```

3. **Set up environment variables**:
   Create a `.env` file with:
   ```env
   OPENROUTER_API_KEY=your_openrouter_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```

   Get your API keys from:
   - [OpenRouter](https://openrouter.ai/)
   - [Tavily](https://tavily.com/)

## Usage

### 1. Start Redis
Ensure Redis is running on `localhost:6379` (default port).

### 2. Start the FastAPI Server
```bash
make dev
```
Or manually:
```bash
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### 3. Start the Celery Worker
In a separate terminal:
```bash
make celery
```
Or manually:
```bash
uv run celery -A app.celery_app worker --loglevel=info
```

### 4. Submit a Research Request

**Endpoint**: `POST /ask`

**Request body**:
```json
{
  "idea": "AI-powered resume builder for developers"
}
```

**Example with curl**:
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"idea": "AI-powered resume builder for developers"}'
```

**Response**:
```json
{
  "message": "Researching..."
}
```

The research runs as a background Celery task. Once complete, a PDF report file `{idea}.pdf` will be generated in the project root.

### 5. View API Documentation
Visit `http://localhost:8000/scalar` for interactive API documentation powered by Scalar.

## How It Works

1. **Query Generation**: AI generates 5 targeted search queries covering competitors, pricing, features, and user complaints
2. **Web Search**: Each query is executed via Tavily API with deep search enabled
3. **Data Extraction**: AI extracts hard facts (competitor names, pricing, features, complaints) from search results
4. **Report Synthesis**: AI compiles a comprehensive markdown report following a structured template
5. **PDF Conversion**: Report is converted to PDF using WeasyPrint

## Report Structure

Generated reports include:

- **Executive Summary**: High-level market landscape overview
- **Market Dynamics & Core Competitors**: Analysis of the software category
- **Competitor Landscape Matrix**: Comparison table of competitors
- **Feature Parity & Gap Analysis**: Table stakes vs missing features
- **Sentiment Analysis & User Pain Points**: User complaints and frustrations
- **Strategic Recommendations & Go-to-Market**: Product, pricing, and positioning strategy
- **Source Repository**: All referenced URLs

## Development Commands

| Command | Description |
|---------|-------------|
| `make dev` | Start FastAPI server with hot reload |
| `make celery` | Start Celery worker |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | Yes | API key for OpenRouter (access to Gemini, GPT models) |
| `TAVILY_API_KEY` | Yes | API key for Tavily web search |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ask` | Submit a research request |
| GET | `/scalar` | Interactive API documentation |

## Dependencies

Main dependencies (see `pyproject.toml` for full list):

- `fastapi` - Web framework
- `celery` - Distributed task queue
- `redis` - Message broker
- `openai` - OpenAI client for API calls
- `tavily-python` - Tavily search client
- `weasyprint` - HTML to PDF conversion
- `markdown` - Markdown processing
- `scalar-fastapi` - API documentation UI
- `uvicorn` - ASGI server

