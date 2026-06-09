"""Detect resume-dump cover letters and trigger regeneration."""

import re

MULTI_JOB_PATTERNS = [
    r"\bpreviously\b",
    r"\bmy work at\b",
    r"\bmy academic background\b",
    r"\bcontributions to open[- ]source\b",
    r"\bresearch assistant\b",
    r"\bdata science intern\b",
    r"\bintern at\b",
    r"\bm\.s\.\b",
    r"\buniversity\b",
]

FORBIDDEN_PHRASES = [
    "previously at",
    "prior to that",
    "before that",
    "another role",
    "also at",
    "in addition",
    "my academic",
    "open-source",
    "open source",
    "hands-on experience with",
    "technical skills span",
]


def looks_like_resume_dump(
    letter: str,
    allowed_employer: str,
    forbidden_employers: list[str] | None = None,
    *,
    letter_length: str = "short",
) -> list[str]:
    """Return violation reasons. Empty list means OK."""
    issues: list[str] = []
    body = letter.lower()
    word_count = len(letter.split())

    max_words = 320 if letter_length == "standard" else 240
    if word_count > max_words:
        issues.append(f"too long ({word_count} words)")

    if len(re.findall(r"\d+%", letter)) > 2:
        issues.append("too many metrics/percentages")

    at_matches = len(re.findall(r"\bat [A-Z]", letter))
    if at_matches > 1:
        issues.append("multiple 'At Company' mentions")

    for pattern in MULTI_JOB_PATTERNS:
        if re.search(pattern, body, re.IGNORECASE):
            issues.append(f"forbidden: {pattern}")

    for phrase in FORBIDDEN_PHRASES:
        if phrase in body:
            issues.append(f"forbidden phrase: {phrase}")

    for employer in forbidden_employers or []:
        name = employer.strip()
        if name and name.lower() in body:
            issues.append(f"mentions forbidden employer: {name}")

    return issues
