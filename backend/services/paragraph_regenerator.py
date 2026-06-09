"""Regenerate a single cover letter paragraph while keeping the rest intact."""

import json
import os
from typing import Literal

import httpx
from fastapi import HTTPException

from services.evidence_service import get_cover_letter_evidence
from services.http_client import get_http_client
from services.json_utils import extract_json_object
from services.letter_parser import merge_cover_letter, parse_cover_letter, replace_paragraph
from services.mistral_service import (
    _build_language_block,
    _format_evidence_pack,
    _format_length_block,
    _guess_job_title,
    _merge_soft_skills,
    _sanitize_no_em_dashes,
)
from services.style_config import LETTER_STYLES, get_style_cfg

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-medium-latest")

ParagraphType = Literal["opening", "proof", "soft_skills", "close"]

PARAGRAPH_RULES: dict[str, str] = {
    "opening": """Write ONLY the opening paragraph (1-2 sentences).
- State the role and a concise fit statement.
- Use company name or JD context if available.
- No resume proof yet. No metrics. No biography.
- Match the letter style tone.""",
    "proof": """Write ONLY the proof paragraph (3-4 sentences max).
- Use the SELECTED EVIDENCE below. One employer only.
- At most one metric if present in evidence. No second job.
- Link clearly to a JD requirement.
- Match the style proof approach.""",
    "soft_skills": """Write ONLY the work-style paragraph (3-5 sentences).
- Use USER-SELECTED SOFT SKILLS. No employer names. No metrics. No job titles.
- Sound human, not like a buzzword list.
- Match the style soft_skills_angle.""",
    "close": """Write ONLY the closing paragraph (1-2 sentences).
- Professional call to action per style rules.
- Include language willingness note ONLY if instructed below.
- No new proof points. No resume dump.""",
}


async def regenerate_paragraph(
    *,
    paragraph: ParagraphType,
    cover_letter: str,
    resume_text: str,
    job_description: str,
    letter_style: str,
    letter_length: str = "short",
    country: str | None = None,
    language: str | None = None,
    is_citizen: bool | None = None,
    company_name: str | None = None,
    role_title: str | None = None,
    hiring_manager_name: str | None = None,
    soft_skills: list[str] | None = None,
    focus_skill: str | None = None,
) -> dict[str, str]:
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="MISTRAL_API_KEY is not configured.")

    if letter_style not in LETTER_STYLES:
        raise HTTPException(status_code=400, detail=f"Unsupported style: {letter_style}")

    parts = parse_cover_letter(cover_letter)
    if not any(parts[k].strip() for k in ("opening", "proof", "soft_skills", "close")):
        raise HTTPException(status_code=400, detail="Could not parse cover letter into paragraphs.")

    evidence = await get_cover_letter_evidence(resume_text, job_description)
    evidence = _merge_soft_skills(evidence, soft_skills)
    if focus_skill and focus_skill.strip() and paragraph == "proof":
        evidence = dict(evidence)
        evidence["jd_link"] = focus_skill.strip()

    cfg = get_style_cfg(letter_style)
    language_block = _build_language_block(language=language, is_citizen=is_citizen)

    include_lang_in_close = paragraph == "close" and bool(language_block.strip())
    lang_instruction = language_block if include_lang_in_close else (
        "Do NOT include a language-learning note." if paragraph == "close" else ""
    )

    company_ctx = f"Company: {company_name.strip()}\n" if company_name and company_name.strip() else ""
    country_ctx = f"Target country: {country.strip()}\n" if country and country.strip() else ""

    other_paras = {
        k: parts[k]
        for k in ("opening", "proof", "soft_skills", "close")
        if k != paragraph and parts[k].strip()
    }
    context_block = ""
    if other_paras:
        context_block = "Keep this consistent with the other paragraphs already in the letter:\n"
        for label, text in other_paras.items():
            context_block += f"- {label}: {text}\n"

    job_title = _guess_job_title(job_description, role_title)
    manager_ctx = (
        f"Hiring manager salutation context: Dear {hiring_manager_name.strip()},\n"
        if hiring_manager_name and hiring_manager_name.strip()
        else ""
    )
    focus_block = ""
    if focus_skill and focus_skill.strip() and paragraph == "proof":
        focus_block = (
            f"\nPRIORITY SKILL TO ADDRESS: {focus_skill.strip()}\n"
            "Rewrite proof to relate resume evidence to this JD requirement.\n"
        )

    prompt = f"""Letter style: {letter_style}
Role: {job_title}
{country_ctx}{company_ctx}{manager_ctx}
{context_block}
{_format_length_block(letter_length)}
{focus_block}
{PARAGRAPH_RULES[paragraph]}

Style tone: {cfg.get('tone', '')}
Soft-skills angle: {cfg.get('soft_skills_angle', '')}
{lang_instruction}

{_format_evidence_pack(evidence)}

JOB DESCRIPTION:
{job_description}

Return JSON only: {{"paragraph": "your paragraph text with no salutation or sign-off"}}"""

    payload = {
        "model": MISTRAL_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You rewrite one paragraph of a cover letter in English. "
                    "Return valid JSON only. Never use em dashes."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.35,
        "max_tokens": 350,
        "response_format": {"type": "json_object"},
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        client = get_http_client()
        response = await client.post(MISTRAL_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"] or ""
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Mistral API error: {exc}") from exc

    try:
        data = extract_json_object(content)
        new_para = _sanitize_no_em_dashes(str(data.get("paragraph", "")).strip())
    except (ValueError, json.JSONDecodeError):
        new_para = _sanitize_no_em_dashes(content.strip().strip('"'))

    if not new_para:
        raise HTTPException(status_code=502, detail="Mistral returned an empty paragraph.")

    updated_parts = replace_paragraph(parts, paragraph, new_para)
    return {
        "paragraph": paragraph,
        "paragraph_text": new_para,
        "cover_letter": merge_cover_letter(updated_parts),
    }
