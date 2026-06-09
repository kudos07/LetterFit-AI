"""Robust JSON extraction from Mistral responses."""

import json
import re


def extract_json_object(raw: str) -> dict:
    if not raw or not str(raw).strip():
        raise ValueError("Empty model response.")

    text = str(raw).strip()

    fence = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if fence:
        text = fence.group(1).strip()

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end <= start:
        raise ValueError("No JSON object found in model response.")

    chunk = text[start : end + 1]
    try:
        parsed = json.loads(chunk)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        chunk = re.sub(r",\s*}", "}", chunk)
        chunk = re.sub(r",\s*]", "]", chunk)
        parsed = json.loads(chunk)
        if isinstance(parsed, dict):
            return parsed

    raise ValueError("No JSON object found in model response.")


def looks_like_cover_letter(text: str) -> bool:
    t = text.strip().lower()
    return len(t) > 80 and (
        t.startswith("dear ")
        or "dear hiring" in t
        or "yours sincerely" in t
        or "kind regards" in t
        or "best regards" in t
    )


def parse_generation_payload(content: str) -> dict:
    """Parse JSON generation response; recover plain-text letter if needed."""
    try:
        return extract_json_object(content)
    except (ValueError, json.JSONDecodeError):
        text = content.strip()
        if looks_like_cover_letter(text):
            return {
                "cover_letter": text,
                "quality_analysis": {
                    "ats_keyword_match_score": 70,
                    "missing_skills": [],
                    "strongest_matches": [],
                    "tone_score": 75,
                    "improvement_suggestions": [],
                },
            }
        raise ValueError("No JSON object found in model response.") from None
