"""Pick one resume evidence block for the cover letter so the model cannot dump the full CV."""

import os
from typing import Any

from fastapi import HTTPException

from services.http_client import get_http_client
from services.json_utils import extract_json_object

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_SELECTOR_MODEL = os.getenv("MISTRAL_SELECTOR_MODEL", "mistral-small-latest")
RESUME_SNIPPET_CHARS = 5000

SELECT_PROMPT = """You select evidence for a cover letter. Read the resume and job description.

Pick exactly ONE past role that best matches the job description.
Extract at most ONE metric from that role (only if present in the resume).

Also list every other employer from the resume in forbidden_employers.

Return JSON only:
{
  "candidate_name": "name or empty string",
  "employer": "single company name chosen",
  "role_title": "job title at that company",
  "evidence": "ONE or TWO short sentences, max 45 words, ONE metric max, this employer only",
  "jd_link": "short phrase for what JD requirement this proves",
  "work_style_themes": ["disciplined", "handles ambiguous problems", "max 4 themes, no company names"],
  "forbidden_employers": ["every other company name from resume except the chosen employer"]
}

Rules:
- Pick exactly one employer from the resume
- evidence must not mention other employers
- forbidden_employers must include ALL other companies/orgs on the resume"""


def _fallback_evidence(resume_text: str, job_description: str) -> dict[str, Any]:
    lines = [ln.strip() for ln in resume_text.splitlines() if ln.strip()]
    name = lines[0] if lines and len(lines[0]) < 60 else ""
    employer = ""
    role_title = ""
    for line in lines[1:8]:
        if " at " in line.lower() or " - " in line:
            employer = line.split(" at ")[-1].split(" - ")[0].strip()[:80]
            role_title = line.split(" at ")[0].split(" - ")[0].strip()[:80]
            break
    if not employer:
        employer = "my most recent role"
    snippet = " ".join(lines[1:4])[:220]
    return {
        "candidate_name": name,
        "employer": employer,
        "role_title": role_title,
        "evidence": snippet or "Relevant experience from my resume aligns with this role.",
        "jd_link": job_description.strip().splitlines()[0][:80] if job_description else "role requirements",
        "work_style_themes": ["disciplined", "self-directed", "handles ambiguous problems", "collaborative"],
        "forbidden_employers": [],
    }


def _normalize_evidence(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_name": str(data.get("candidate_name", "")).strip(),
        "employer": str(data.get("employer", "")).strip() or "my most recent role",
        "role_title": str(data.get("role_title", "")).strip(),
        "evidence": str(data.get("evidence", "")).strip() or "Relevant experience aligns with this role.",
        "jd_link": str(data.get("jd_link", "")).strip() or "role requirements",
        "work_style_themes": [
            str(t).strip() for t in (data.get("work_style_themes") or []) if str(t).strip()
        ][:5]
        or ["disciplined", "self-directed", "collaborative"],
        "forbidden_employers": [
            str(e).strip() for e in (data.get("forbidden_employers") or []) if str(e).strip()
        ],
    }


async def select_cover_letter_evidence(
    resume_text: str, job_description: str
) -> dict[str, Any]:
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="MISTRAL_API_KEY is not configured.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    resume_snippet = resume_text[:RESUME_SNIPPET_CHARS]
    jd_snippet = job_description[:3000]

    for attempt in range(2):
        payload = {
            "model": MISTRAL_SELECTOR_MODEL,
            "messages": [
                {"role": "system", "content": SELECT_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"RESUME:\n{resume_snippet}\n\nJOB DESCRIPTION:\n{jd_snippet}"
                        + (
                            "\n\nReturn valid JSON only."
                            if attempt
                            else ""
                        )
                    ),
                },
            ],
            "temperature": 0.1,
            "max_tokens": 320,
            "response_format": {"type": "json_object"},
        }

        try:
            client = get_http_client()
            response = await client.post(MISTRAL_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"] or ""
            data = extract_json_object(content)
            return _normalize_evidence(data)
        except (KeyError, IndexError, ValueError):
            continue
        except Exception:
            break

    return _fallback_evidence(resume_text, job_description)
