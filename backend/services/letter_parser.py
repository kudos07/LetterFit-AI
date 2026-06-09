"""Split and merge cover letter sections for paragraph-level editing."""

import re

CLOSING_PREFIXES = (
    "yours sincerely",
    "yours faithfully",
    "kind regards",
    "best regards",
    "warm regards",
    "sincerely",
    "regards",
)


def _is_salutation(text: str) -> bool:
    return text.lower().startswith("dear ")


def _is_closing_line(text: str) -> bool:
    lower = text.lower().rstrip(",")
    return any(lower.startswith(prefix) for prefix in CLOSING_PREFIXES)


def _looks_like_signature(text: str) -> bool:
    if not text or len(text) > 80:
        return False
    if text.endswith("."):
        return False
    return "\n" not in text


def _split_closing_block(text: str) -> tuple[str, str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return "", ""
    if _is_closing_line(lines[0]):
        closing_line = lines[0]
        signature = lines[1] if len(lines) > 1 else ""
        return closing_line, signature
    return "", text


def parse_cover_letter(text: str) -> dict[str, str]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]

    salutation = ""
    closing_line = ""
    signature = ""

    if paragraphs and _is_salutation(paragraphs[0]):
        salutation = paragraphs.pop(0)

    if paragraphs:
        last = paragraphs[-1]
        if _is_closing_line(last) or (
            "\n" in last and _is_closing_line(last.splitlines()[0].strip())
        ):
            closing_line, signature = _split_closing_block(last)
            paragraphs.pop()
        elif _looks_like_signature(last):
            signature = paragraphs.pop()
            if paragraphs and _is_closing_line(paragraphs[-1]):
                closing_line = paragraphs.pop()

    body = paragraphs
    opening = body[0] if len(body) > 0 else ""
    proof = body[1] if len(body) > 1 else ""
    soft_skills = body[2] if len(body) > 2 else ""
    close = body[3] if len(body) > 3 else ""

    if len(body) == 3:
        soft_skills = body[2]
        close = ""
    elif len(body) == 2:
        soft_skills = ""
        close = ""

    return {
        "salutation": salutation,
        "opening": opening,
        "proof": proof,
        "soft_skills": soft_skills,
        "close": close,
        "closing_line": closing_line,
        "signature": signature,
    }


def merge_cover_letter(parts: dict[str, str]) -> str:
    blocks: list[str] = []
    if parts.get("salutation", "").strip():
        blocks.append(parts["salutation"].strip())
    for key in ("opening", "proof", "soft_skills", "close"):
        value = parts.get(key, "").strip()
        if value:
            blocks.append(value)
    if parts.get("closing_line", "").strip():
        blocks.append(parts["closing_line"].strip())
    if parts.get("signature", "").strip():
        blocks.append(parts["signature"].strip())
    return "\n\n".join(blocks)


def replace_paragraph(parts: dict[str, str], paragraph: str, new_text: str) -> dict[str, str]:
    updated = dict(parts)
    updated[paragraph] = new_text.strip()
    return updated


def count_body_words(text: str) -> int:
    """Count words in letter body (opening + proof + soft_skills + close)."""
    if not text or not text.strip():
        return 0
    parts = parse_cover_letter(text)
    body = " ".join(
        parts[key].strip()
        for key in ("opening", "proof", "soft_skills", "close")
        if parts.get(key, "").strip()
    )
    return len(body.split()) if body else 0
