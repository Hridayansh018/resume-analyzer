# Resume Analysis

A FastAPI-based resume analysis project with AI-powered features for:
- resume review against a job description
- ATS score estimation
- cover letter generation
- interview question generation

A modern static frontend is available at `static/index.html` and is served by the backend at `/`.

## Features

- Upload PDF resumes
- Compare resume text to job descriptions
- Generate structured JSON responses for review, ATS, cover letters, and interview prompts
- Live frontend with mode tabs and results display

## Prerequisites

- Python 3.11 or newer
- `pip` available
- An OpenRouter-compatible API key set in `.env`

## Installation

1. Create and activate a virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\activate
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your API key:

```text
OPENROUTER_API_KEY=your_api_key_here
```

## Running the app

Start the FastAPI server:

```powershell
uvicorn main:app --reload
```

Then open the frontend in your browser:

```text
http://127.0.0.1:8000/
```

## API Endpoints

### `POST /review`

Review a resume using a job description.

Form fields:
- `file` (PDF resume)
- `job_description`

### `POST /ats-score`

Return ATS-style scoring for the resume.

Form fields:
- `file` (PDF resume)
- `job_description`

### `POST /cover-letter`

Generate a cover letter from the resume and target role.

Form fields:
- `file` (PDF resume)
- `company_name`
- `job_title`

### `POST /interview-questions`

Generate interview questions for the target job.

Form fields:
- `file` (PDF resume)
- `job_description`

## Frontend

The app includes a static single-page UI at `static/index.html`.
The FastAPI app mounts this under `/`, so visiting the root URL serves the UI automatically.

## Environment Variables

- `OPENROUTER_API_KEY` — required API key used by `client.py` to communicate with the AI service.
- `CORS_ALLOW_ORIGINS` — optional comma-separated origins for CORS.

## Troubleshooting

- `405 Method Not Allowed` means the frontend is calling the wrong host or route.
- `400 Bad Request` usually indicates missing form fields or a PDF with non-extractable text.
- If your resume PDF is a scanned image, text extraction may fail.

## Files

- `main.py` — FastAPI server and endpoint definitions
- `client.py` — OpenAI/OpenRouter API client setup
- `schema.py` — Pydantic response models
- `static/index.html` — frontend user interface
- `requirements.txt` — Python dependencies
