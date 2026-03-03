# Assignment 4 - AI API Tester Agent

An automated QA agent that stress-tests any REST API and spits out a PDF report. You give it an API description and a base URL, it handles everything else.

## How it works

1. AI generates 8 test cases covering happy path, input validation, boundary testing, security, and null payloads
2. Each test case gets executed against the target API
3. Another AI model evaluates each result (PASS/FAIL with reasoning)
4. A final QA report is compiled and exported as `qa_report.pdf`

## Stack

- **FastAPI** - HTTP server
- **Celery + Redis** - background task processing
- **OpenRouter** - AI models (Gemini 3 Flash + GPT-OSS 120B)
- **WeasyPrint** - PDF generation

## Setup

**Prerequisites:** Python 3.13+, Redis running on localhost:6379

```bash
# install deps
uv sync

# create .env
OPENROUTER_API_KEY=your_key_here
```

## Running

You need two terminals:

```bash
# terminal 1 - API server
make dev

# terminal 2 - celery worker
make celery
```

## Usage

```bash
curl -X POST http://localhost:8000/qa \
  -H "Content-Type: application/json" \
  -d '{
    "api_description": "A simple todo API with CRUD operations",
    "base_url": "http://localhost:3000"
  }'
```

The task runs in the background. Once done, check `qa_report.pdf` in the project root.

API docs available at `http://localhost:8000/scalar`.
