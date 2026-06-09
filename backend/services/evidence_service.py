"""Cached resume evidence selection."""

from typing import Any

from services.request_cache import cache_get, cache_set
from services.resume_selector import select_cover_letter_evidence


async def get_cover_letter_evidence(
    resume_text: str,
    job_description: str,
    *,
    use_cache: bool = True,
) -> dict[str, Any]:
    if use_cache:
        cached = cache_get("evidence", resume_text, job_description)
        if cached:
            return cached

    evidence = await select_cover_letter_evidence(resume_text, job_description)
    if use_cache:
        cache_set("evidence", evidence, resume_text, job_description)
    return evidence
