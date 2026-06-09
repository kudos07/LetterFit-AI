"""Gather public company information to personalize cover letters."""

import asyncio
import os
import re
from typing import Any

import httpx

from services.request_cache import cache_get, cache_set

WIKIPEDIA_SEARCH = "https://en.wikipedia.org/w/api.php"
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_MODEL = "mistral-small-latest"
USER_AGENT = "CoverLetterAI/1.0 (https://github.com; cover-letter-generator)"


EUROPE_COUNTRY_LANGUAGES: dict[str, str] = {
    "germany": "German",
    "france": "French",
    "netherlands": "Dutch",
    "belgium": "French or Dutch",
    "spain": "Spanish",
    "italy": "Italian",
    "portugal": "Portuguese",
    "poland": "Polish",
    "sweden": "Swedish",
    "norway": "Norwegian",
    "denmark": "Danish",
    "finland": "Finnish",
    "austria": "German",
    "switzerland": "German, French, or Italian",
    "ireland": "English",
    "united kingdom": "English",
    "uk": "English",
    "czech republic": "Czech",
    "czechia": "Czech",
    "hungary": "Hungarian",
    "romania": "Romanian",
    "greece": "Greek",
}


def language_for_europe_country(country: str) -> str | None:
    if not country or not country.strip():
        return None
    return EUROPE_COUNTRY_LANGUAGES.get(country.strip().lower())


def _clean_text(text: str, max_len: int = 600) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rstrip() + "..."


async def _fetch_wikipedia_extract(
    client: httpx.AsyncClient, company_name: str
) -> tuple[str | None, str | None]:
    """Returns (extract, page_title)."""
    headers = {"User-Agent": USER_AGENT}

    try:
        search = await client.get(
            WIKIPEDIA_SEARCH,
            params={
                "action": "opensearch",
                "search": company_name,
                "limit": 1,
                "namespace": 0,
                "format": "json",
            },
            headers=headers,
            timeout=12.0,
        )
        search.raise_for_status()
        data = search.json()
        if len(data) < 2 or not data[1]:
            return None, None

        title = data[1][0]
        page = await client.get(
            WIKIPEDIA_SEARCH,
            params={
                "action": "query",
                "titles": title,
                "prop": "extracts",
                "exintro": True,
                "explaintext": True,
                "format": "json",
            },
            headers=headers,
            timeout=12.0,
        )
        page.raise_for_status()
        pages = page.json().get("query", {}).get("pages", {})
        if not pages:
            return None, None

        page_data = next(iter(pages.values()))
        extract = page_data.get("extract")
        if extract:
            return _clean_text(extract, 500), title
    except (httpx.HTTPError, KeyError, TypeError, StopIteration):
        return None, None

    return None, None


def _search_duckduckgo_sync(company_name: str, max_results: int = 4) -> list[dict[str, str]]:
    try:
        from duckduckgo_search import DDGS

        query = f"{company_name} company technology products"
        with DDGS() as ddgs:
            return [
                {
                    "title": r.get("title", ""),
                    "body": r.get("body", ""),
                    "href": r.get("href", ""),
                }
                for r in ddgs.text(query, max_results=max_results)
                if r.get("body")
            ]
    except Exception:
        return []


async def _mistral_research_brief(company_name: str, web_snippets: str) -> str | None:
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        return None

    prompt = f"""You are researching a company for a tech job cover letter.

Company: {company_name}

Public web snippets (may be incomplete):
{web_snippets or "None available."}

Write a short factual brief (80-120 words) covering:
- What the company does
- Industry and products/services if known
- Why a software engineer might want to join

Rules:
- Use only well-established public facts from the snippets or widely known information.
- If uncertain, say "limited public information available" rather than inventing.
- English only. No em dashes.
- Plain text only, no JSON."""

    payload = {
        "model": MISTRAL_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(MISTRAL_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return _clean_text(content.strip(), 700)
    except (httpx.HTTPError, KeyError, IndexError):
        return None


async def research_company(company_name: str) -> dict[str, Any]:
    name = company_name.strip()
    if not name:
        return {"found": False, "summary": "", "sources": [], "company_name": name}

    cached = cache_get("company", name.lower())
    if cached:
        return cached

    snippets: list[str] = []
    sources: list[str] = []

    async with httpx.AsyncClient(timeout=20.0) as client:
        wiki_task = _fetch_wikipedia_extract(client, name)
        ddg_task = asyncio.to_thread(_search_duckduckgo_sync, name)
        (wiki_text, wiki_title), web_results = await asyncio.gather(wiki_task, ddg_task)

    if wiki_text:
        snippets.append(f"Wikipedia ({wiki_title}): {wiki_text}")
        sources.append("Wikipedia")
    for item in web_results[:3]:
        body = _clean_text(item.get("body", ""), 260)
        title = item.get("title", "").strip()
        if body:
            snippets.append(f"{title}: {body}" if title else body)
            if "Web search" not in sources:
                sources.append("Web search")

    raw_context = "\n\n".join(snippets)
    mistral_brief = None
    if not wiki_text or len(wiki_text) < 350:
        mistral_brief = await _mistral_research_brief(name, raw_context)
    if mistral_brief:
        sources.append("Mistral synthesis")
        summary = mistral_brief
        if raw_context:
            summary = f"{mistral_brief}\n\nRaw sources:\n{raw_context}"
        result = {
            "found": True,
            "summary": _clean_text(summary, 2000),
            "sources": sources,
            "company_name": name,
        }
        cache_set("company", result, name.lower(), ttl=1800)
        return result

    if snippets:
        result = {
            "found": True,
            "summary": _clean_text(raw_context, 1800),
            "sources": sources,
            "company_name": name,
        }
        cache_set("company", result, name.lower(), ttl=1800)
        return result

    result = {
        "found": False,
        "summary": (
            f"Limited public research found for '{name}'. "
            "The cover letter will rely on the job description for company context."
        ),
        "sources": [],
        "company_name": name,
    }
    cache_set("company", result, name.lower(), ttl=600)
    return result
