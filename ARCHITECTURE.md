# Architecture & rules

How LetterFit AI is built, how requests flow, and the rules the generator must follow.

## System overview

```
+------------------------------------------------------------------+
|                         USER BROWSER                              |
|  React (Vite)  :5173                                              |
|  - Generator page, localStorage session                           |
|  - /api/* proxied to backend                                      |
+----------------------------+-------------------------------------+
                             | HTTP
                             v
+------------------------------------------------------------------+
|                    FASTAPI BACKEND  :8008                         |
|  main.py  ->  routes  ->  services  ->  Mistral / web / files    |
+------------------------------------------------------------------+
         |              |                    |
         v              v                    v
   +-----------+  +-------------+     +--------------+
   | PyMuPDF   |  | In-memory   |     | Mistral API  |
   | python-   |  | cache       |     | (chat        |
   | docx      |  | (10-30 min) |     | completions) |
   +-----------+  +-------------+     +--------------+
                         |
                         v
                  +--------------+
                  | Wikipedia +  |
                  | DuckDuckGo   |
                  +--------------+
```

No database. The API is stateless; the browser keeps form state in `localStorage`.

---

## Request flows

### Generate cover letter

```
  [Upload resume]          [Paste JD + options]
         |                          |
         v                          v
   POST /upload-resume        (text in memory)
         |
         +----------+----------+
                    |
                    v
         POST /generate-cover-letter
                    |
    +---------------+---------------+
    |               |               |
    v               v               v
 evidence      company         (parallel
 selector      research         if company
 (Mistral      (web)            name set)
 small)            |
    |               |               |
    +-------+-------+               |
            v                       |
     merge soft skills              |
            |                       |
            v                       |
     build prompt (style + length + rules)
            |
            v
     Mistral medium (JSON: letter + quality)
            |
            v
     validate (no resume dump, length check)
            |
            +-- standard & <220 body words? --> retry once
            |
            v
     response: cover_letter, quality_analysis, company_research
```

### Compare two styles

```
POST /compare-styles
        |
        +-- evidence + company research ONCE (cached)
        |
        +-- generate style A  -----+
        |                          +-- parallel
        +-- generate style B  -----+
        |
        v
letters{ A, B }, quality_analysis{ A, B }, company_research
```

### Regenerate one paragraph

```
POST /regenerate-paragraph
        |
        +-- cached evidence only (no company research)
        |
        v
   Mistral rewrites ONE paragraph (opening | proof | soft_skills | close)
        |
        v
   merge back into full letter text
```

---

## Backend modules

| Module | Role |
|--------|------|
| `main.py` | Routes, CORS, schema wiring |
| `mistral_service.py` | Prompts, generation, compare, quality normalization |
| `style_config.py` | Tone presets: Professional, Qualifications, Hype, Mix, Bold |
| `resume_selector.py` | Picks one resume employer + proof for the JD (fast model) |
| `evidence_service.py` | Cached wrapper around evidence selection |
| `company_research.py` | Wikipedia + DuckDuckGo summary for company field |
| `paragraph_regenerator.py` | Single-paragraph rewrite |
| `letter_parser.py` | Split/merge paragraphs; body word count |
| `letter_validator.py` | Reject resume dumps, multi-job letters |
| `letter_template.py` | Fallback template if model JSON fails |
| `request_cache.py` | TTL cache for evidence and research |
| `http_client.py` | Shared `httpx` connection pool |
| `export_docx.py` / `export_pdf.py` | File download responses |

---

## Frontend modules

| Area | Role |
|------|------|
| `pages/Generator.jsx` | Main workflow, API calls, persisted state |
| `api/client.js` | Fetch helpers, `/api` base |
| `components/*` | Upload, editor, quality panel, style compare, progress |
| `utils/formPersistence.js` | `localStorage` session |
| `utils/wordCount.js` | Body word count + length limits UI |
| `hooks/useGenerationProgress.js` | Step UI during long requests |

---

## Cover letter generation rules

These rules are enforced in prompts and post-generation validation.

### Language & format

- Entire letter in **English** only.
- Standard business letter: salutation, body, closing, optional signature.
- No em dashes or en dashes.
- No bullet lists in the body.

### Structure (always)

```
Dear [Manager],

[OPENING]     1-2 sentences - role + why this company/role

[PROOF]       ONE employer only, tied to top JD requirement

[WORK STYLE]  Soft skills / how you work - no job titles, no metrics

[CLOSE]       1-2 sentences + optional language-learning note

Yours sincerely,
[Name]
```

Exactly **two body paragraphs** between opening and close (proof + work style). No third proof paragraph.

### Forbidden content

- Walking the full resume role-by-role.
- More than **one** past employer cited in the letter.
- Phrases like "Previously at…", "At X… At Y…", academic dumps, open-source laundry lists.
- Invented metrics or experience not on the resume.
- Hollow filler: "passionate", "perfect fit", "dynamic team player".

### Length targets

| Mode | Body words (excl. salutation & sign-off) | Paragraph depth |
|------|------------------------------------------|-----------------|
| **Short** | 150-200 (hard cap ~200) | Opening 1-2 sent.; proof 3-4; work style 3-5 |
| **Standard** | 220-280 (min 220; auto-retry if short) | Opening 2-3; proof 5-6; work style 5-6 |

Word count in the UI uses **body only** (same definition as backend `count_body_words`).

### Style presets (tone, not country)

| Style | Voice |
|-------|--------|
| Professional | Balanced, corporate-safe |
| Qualifications | Facts-first, credentials |
| Hype | Confident, impact-led |
| Mix | Warm professional blend |
| Bold | Memorable hook, high energy |

Optional **country** and **language** fields tune cultural context and may add a language-willingness note in the close (non-citizens only).

### Company research

- Runs only when **company name** is provided.
- Summary is injected into the prompt; model should write **1-2 sentences** of genuine company fit in the opening.
- Does **not** run on paragraph regenerate (uses cached evidence only).

### Quality analysis

Returned with every full generation (and compare):

- `ats_keyword_match_score` (0-100)
- `missing_skills` - JD skills weak/absent on resume
- `strongest_matches` - alignments used in the letter
- `tone_score` - fit to selected style
- `improvement_suggestions` - actionable tips

---

## Performance design

```
                    +------------------+
                    |  request_cache   |
                    +--------+---------+
                             |
        +--------------------+--------------------+
        |                    |                    |
   evidence key         research key         shared httpx
   (resume+JD hash)    (company name)       connection pool
   TTL ~10 min          TTL ~30 min
```

- Evidence selection uses `mistral-small-latest` (configurable).
- Full letter uses `mistral-medium-latest` (configurable).
- Compare shares one evidence + one research call, then parallel letter gens.

---

## Dev ports

| Service | Port |
|---------|------|
| Frontend (Vite) | 5173 |
| Backend (uvicorn) | 8008 |
| API from browser | `/api` → proxy → 8008 |

On Windows, stale uvicorn processes can ghost-listen on old ports; prefer a single backend on **8008**.
