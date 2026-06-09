# LetterFit AI

Full-stack app for generating English tech cover letters with tone presets, optional company research, and quality analysis. Upload a resume, paste a job description, pick a style and length, and get an AI-written letter powered by **Mistral AI**.

## Features

- Resume upload (PDF & DOCX) with text extraction
- Job description input with sample JD
- **Letter styles:** Professional, Qualifications, Hype, Mix, Bold
- **Letter length:** Short (150-200 body words) or Standard (220-280 body words)
- Optional application context: role title, hiring manager, company name, country, language
- **Company research** (Wikipedia + web) when a company name is provided
- Soft skills selector woven into the work-style paragraph
- Mistral-powered generation with evidence selection from your resume
- Quality analysis: ATS keyword match, missing skills, tone score, suggestions
- Paragraph-level regenerate and “address skill in letter” from quality panel
- **Style compare** - two tones in one request with side-by-side scores
- Editable output, copy, DOCX export, PDF export
- Form state saved in the browser (localStorage)

## Tech stack

| Layer | Stack |
|-------|--------|
| Frontend | React, Vite, Tailwind CSS |
| Backend | FastAPI |
| LLM | Mistral AI API |
| Database | None (stateless MVP) |
| Parsing | PyMuPDF (PDF), python-docx (DOCX) |

## Architecture & rules

See **[ARCHITECTURE.md](./ARCHITECTURE.md)** for:

- ASCII system and request-flow diagrams (no Mermaid)
- Module map (backend + frontend)
- Cover letter generation rules (structure, forbidden content, length targets)
- Caching and performance notes

## Project structure

```
ARCHITECTURE.md

backend/
  main.py
  services/
    mistral_service.py
    style_config.py
    resume_selector.py
    company_research.py
    paragraph_regenerator.py
    export_docx.py
    export_pdf.py
  models/
    schemas.py
  requirements.txt
  .env.example

frontend/
  src/
    pages/Generator.jsx
    components/
    api/client.js
  vite.config.js
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- A [Mistral AI API key](https://console.mistral.ai/)

## Backend setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env   # macOS / Linux
```

Edit `backend/.env`:

```
MISTRAL_API_KEY=your_mistral_api_key_here
```

Optional:

```
MISTRAL_MODEL=mistral-medium-latest
MISTRAL_SELECTOR_MODEL=mistral-small-latest
```

Start the API:

```bash
uvicorn main:app --reload --port 8008
```

API docs: http://127.0.0.1:8008/docs

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

The Vite dev server proxies `/api` to the backend on **port 8008** (see `frontend/vite.config.js`).

## Sample data

```bash
python samples/create_sample_resume.py
```

Suggested test flow:

1. Upload `samples/sample_resume.docx`
2. Click **Load sample JD**
3. Enter a company name (e.g. `Stripe`) to test company research
4. Pick **Professional** and **Short**, then **Generate cover letter**

## API routes

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/health` | Health check |
| GET | `/styles` | List tone presets |
| POST | `/upload-resume` | Upload PDF/DOCX, returns extracted text |
| POST | `/generate-cover-letter` | Generate letter + quality analysis |
| POST | `/compare-styles` | Two styles in one call (shared evidence/research) |
| POST | `/regenerate-paragraph` | Rewrite one paragraph |
| POST | `/export-docx` | Download as DOCX |
| POST | `/export-pdf` | Download as PDF |

## Letter styles

All letters are written in **English**. Each style changes tone, opening, proof angle, and closing, not country-specific formatting.

| Style | Best for |
|-------|----------|
| **Professional** | Balanced, corporate-safe applications |
| **Qualifications** | Facts-first, credential-heavy roles |
| **Hype** | Confident, impact-driven startups |
| **Mix** | Warm professional blend |
| **Bold** | Memorable hook, high-energy voice |

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MISTRAL_API_KEY` | Yes | Mistral AI API key |
| `MISTRAL_MODEL` | No | Generation model (default: `mistral-medium-latest`) |
| `MISTRAL_SELECTOR_MODEL` | No | Evidence picker model (default: `mistral-small-latest`) |

Frontend override:

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | API base URL (default: `/api` via Vite proxy) |

## License

This project is licensed under the [MIT License](LICENSE).

Copyright © 2026 Saransh Surana. You are free to use, modify, and distribute this software with attribution.
