import asyncio
import json
import os
import re
from typing import Any

import httpx
from fastapi import HTTPException

from models.schemas import CompanyResearch, GenerateCoverLetterResponse, QualityAnalysis
from services.company_research import research_company
from services.evidence_service import get_cover_letter_evidence
from services.http_client import get_http_client
from services.style_config import LETTER_STYLES, get_style_cfg, get_style_summaries
from services.json_utils import parse_generation_payload
from services.letter_template import build_template_letter
from services.letter_parser import count_body_words
from services.letter_validator import looks_like_resume_dump

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-medium-latest")

# Each market has distinct tone, structure, emphasis, and formatting preferences.
# All letters are written in English only.
MARKET_CONFIG: dict[str, dict[str, Any]] = {
    "Europe": {
        "summary": "Pan-EU tone: evidence-led, modest, qualification-first",
        "tone": "Professional, concise, evidence-based, modest confidence.",
        "opening": "Open with the exact role title and a one-line fit statement. No hype or clever hooks.",
        "structure": "3-4 short paragraphs: intro, two proof paragraphs tied to JD requirements, brief close.",
        "emphasis": "Role alignment, qualifications, facts from resume, reliability, EU work culture fit.",
        "avoid": "Superlatives, buzzword stuffing, American-style self-promotion, long narratives.",
        "certainty_style": "Use calm, evidence-first language such as 'My experience aligns well with...' Avoid sounding overly certain.",
        "proof_style": "Prefer explicit links to JD requirements. Use resume facts. If the resume has numbers, use them; otherwise use specific scope without inventing metrics.",
        "company_fit_style": "Briefly connect your collaboration and reliability to EU/EEA team norms. Mention company fit only if the JD provides clues.",
        "salutation": "Dear Hiring Manager,",
        "closing": "Yours sincerely,",
        "call_to_action": "Close with a short request for an interview and a willingness to discuss fit.",
        "length": "280-350 words",
        "include_language_note": True,
        "language_focus": "local European languages mentioned in the JD, or European languages generally",
    },
    "Germany": {
        "summary": "Direct, precise, qualification-heavy; low hype",
        "tone": "Formal, precise, qualification-focused, direct, factual, low hype.",
        "opening": "State the position and your relevant qualifications immediately. Use a structured, information-heavy first paragraph.",
        "structure": "Clear logical flow: motivation (brief), qualifications (detailed), company fit, close.",
        "emphasis": "Degrees, years of experience, technical credentials, methodical delivery, reliability.",
        "avoid": "Emotional language, vague claims, marketing speak, excessive enthusiasm, passive vagueness.",
        "certainty_style": "Be direct but not overly warm. Use formulations like 'I am applying because...' and 'My experience includes...'.",
        "proof_style": "Use concrete delivery details from the resume: systems shipped, responsibilities, team scope. Avoid adjectives without evidence.",
        "company_fit_style": "Emphasize structured delivery and reliability. Mention company fit by tying to role responsibilities described in the JD.",
        "salutation": "Dear Hiring Team,",
        "closing": "Yours sincerely,",
        "call_to_action": "Politely request an interview and confirm you would be able to contribute immediately.",
        "length": "300-380 words",
        "include_language_note": True,
        "language_focus": "German",
    },
    "France": {
        "summary": "Polished, motivated, company-fit focused",
        "tone": "Formal, polished, motivation-focused, company and mission alignment.",
        "opening": "Express genuine motivation for the company and role first. Then connect to competencies.",
        "structure": "Motivation paragraph, competencies paragraph, contribution paragraph, courteous close.",
        "emphasis": "Why this company, professional presentation, adaptability, long-term fit.",
        "avoid": "Overly casual tone, bullet-heavy US style, arrogance, purely transactional tone.",
        "certainty_style": "Sound assured but respectful. Use phrases like 'I am particularly interested in...' and 'I believe my experience...' without overclaiming.",
        "proof_style": "Balance motivation with 2-3 concrete resume-supported examples. Avoid long lists.",
        "company_fit_style": "Tie motivation to what the JD says about mission, product impact, or company priorities.",
        "salutation": "Dear Hiring Manager,",
        "closing": "Kind regards,",
        "call_to_action": "Close with a courteous request to discuss how you can contribute.",
        "length": "300-380 words",
        "include_language_note": True,
        "language_focus": "French",
    },
    "United Kingdom": {
        "summary": "Formal, brief, understated confidence",
        "tone": "Formal, concise, role-fit focused, understated modest confidence.",
        "opening": "Two sentences max to start: role plus direct match to requirements. Keep the tone restrained.",
        "structure": "Short intro, one strong evidence paragraph, one JD-mapping paragraph, polite sign-off.",
        "emphasis": "Relevant experience only, no overselling, clear match to listed requirements.",
        "avoid": "American enthusiasm, 'I am the perfect candidate', long letters, unproven claims, exaggerated confidence.",
        "certainty_style": "Use modest certainty such as 'I would welcome the opportunity' rather than 'I guarantee...'.",
        "proof_style": "Use one detailed example that mirrors a JD requirement. Keep it focused.",
        "company_fit_style": "Mention company fit briefly only if the JD provides concrete details.",
        "salutation": "Dear Hiring Manager,",
        "closing": "Yours sincerely,",
        "call_to_action": "Ask for consideration and offer availability for interview.",
        "length": "250-320 words",
        "include_language_note": False,
    },
    "Ireland": {
        "summary": "Warm, team-oriented, impact-focused",
        "tone": "Friendly, professional, team-oriented, impact-focused, personable but credible.",
        "opening": "Warm professional opener that mentions the team, collaboration, or product context from the JD.",
        "structure": "Engaging intro, collaboration and impact examples, culture fit, enthusiastic close.",
        "emphasis": "Teamwork, cross-functional work, outcomes delivered, communication, adaptability.",
        "avoid": "Cold corporate tone, excessive formality, jargon without context.",
        "certainty_style": "Be warm and confident without overhyping. Use 'I enjoy collaborating...' and 'I have delivered...' style statements.",
        "proof_style": "Include at least one example of cross-functional collaboration or communication from the resume.",
        "company_fit_style": "Connect to the team or culture described in the JD rather than broad generic claims.",
        "salutation": "Dear Hiring Team,",
        "closing": "Kind regards,",
        "call_to_action": "Close with an inviting note about working with the team and delivering outcomes together.",
        "length": "280-350 words",
        "include_language_note": False,
    },
    "Canada": {
        "summary": "Polite, clear, achievement-focused; bilingual-aware",
        "tone": "Professional, clear, achievement-focused, polite, direct but courteous.",
        "opening": "Reference the role and location. Lead with your strongest relevant achievement in one sentence.",
        "structure": "Intro with achievement, skills match paragraph, teamwork paragraph, professional close.",
        "emphasis": "Results, collaboration, inclusivity, clarity, readiness to work in a multilingual context when relevant.",
        "avoid": "Aggressive US tone, excessive brevity, ignoring JD location or language hints.",
        "certainty_style": "Use courteous confidence. Avoid sounding overly assertive.",
        "proof_style": "Use clear, readable sentences and connect each claim to a JD bullet or requirement.",
        "company_fit_style": "Mention inclusivity or clear communication if present in the JD. Otherwise tie fit to responsibilities described.",
        "salutation": "Dear Hiring Manager,",
        "closing": "Sincerely,",
        "call_to_action": "Politely ask to be considered and request an interview to discuss fit.",
        "length": "280-350 words",
        "include_language_note": True,
        "language_focus": "French or other local languages mentioned in the JD, especially for Quebec or bilingual roles",
    },
    "Australia": {
        "summary": "Straightforward, results-led, no fluff",
        "tone": "Professional, straightforward, results-focused, confident but not boastful.",
        "opening": "Start with role plus the outcome you have delivered that matches the JD.",
        "structure": "Direct intro, results paragraph with specifics, skills paragraph, short confident close.",
        "emphasis": "Deliverables, ownership, practical outcomes, no-nonsense communication.",
        "avoid": "Flowery language, passive voice, vague aspirations, over-formality.",
        "certainty_style": "Sound capable and practical. Use direct statements without overconfidence.",
        "proof_style": "Prefer outcomes tied to responsibilities. Keep each paragraph short and actionable.",
        "company_fit_style": "Tie to product and delivery expectations from the JD.",
        "salutation": "Dear Hiring Manager,",
        "closing": "Regards,",
        "call_to_action": "Invite a conversation and confirm you would welcome the opportunity to contribute.",
        "length": "250-320 words",
        "include_language_note": False,
    },
    "New Zealand": {
        "summary": "Humble, collaborative, practical",
        "tone": "Professional, humble, collaborative, practical, personable.",
        "opening": "A modest opener focused on what you can contribute to the team. Avoid self-praise.",
        "structure": "Humble intro, team contribution examples, technical competence, warm close.",
        "emphasis": "Team fit, willingness to help, practical skills, cultural adaptability.",
        "avoid": "Bragging, aggressive self-promotion, hype, lone-wolf framing.",
        "certainty_style": "Keep confidence calm and grounded. Use 'I can contribute by...' language.",
        "proof_style": "Include at least one example of supporting others, sharing ownership, or improving team outcomes.",
        "company_fit_style": "Show you understand the collaboration and delivery context described in the JD.",
        "salutation": "Dear Hiring Team,",
        "closing": "Kind regards,",
        "call_to_action": "Close with willingness to learn and contribute to team goals.",
        "length": "260-330 words",
        "include_language_note": False,
    },
    "Singapore": {
        "summary": "Precise, skills-first, multicultural",
        "tone": "Professional, precise, skills-first, efficient, multicultural and adaptable.",
        "opening": "State the role and the top 2-3 matching skills in the first 2 sentences.",
        "structure": "Skills-forward intro, technical proof, adaptability and stakeholder paragraph, concise close.",
        "emphasis": "Technical precision, efficiency, cross-cultural teamwork, reliability, fast learning.",
        "avoid": "Rambling stories, vague soft skills without evidence, overly casual tone.",
        "certainty_style": "Be specific and confident about execution, but avoid exaggerated claims.",
        "proof_style": "Include at least one example tied to delivery speed, reliability, quality, or operational readiness from the resume (only if present).",
        "company_fit_style": "Mention stakeholder collaboration and adaptability if the JD suggests it.",
        "salutation": "Dear Hiring Manager,",
        "closing": "Sincerely,",
        "call_to_action": "Request an interview and highlight your ability to ramp up quickly.",
        "length": "250-320 words",
        "include_language_note": True,
        "language_focus": "Mandarin, Malay, Tamil, or other languages mentioned in the JD",
    },
    "Other": {
        "summary": "Adaptable professional tone for any country",
        "tone": "Professional, clear, respectful. Match local hiring norms inferred from the JD and country.",
        "opening": "State the role and a concise fit statement. Keep tone neutral and professional.",
        "structure": "3-4 short paragraphs: intro, proof, work style, brief close.",
        "emphasis": "Role alignment, relevant experience, reliability, cultural awareness without overclaiming.",
        "avoid": "Generic US-style hype, invented local knowledge, visa or relocation commentary unless relevant.",
        "certainty_style": "Use balanced language: 'My experience aligns with...' or 'I can contribute to...'.",
        "proof_style": "One clear proof point tied to the JD. Factual, not boastful.",
        "company_fit_style": "Brief company fit from JD or research only. Do not invent local market expertise.",
        "salutation": "Dear Hiring Manager,",
        "closing": "Yours sincerely,",
        "call_to_action": "Close with a polite request to discuss fit.",
        "length": "150-200 words",
        "include_language_note": True,
        "language_focus": "the local language",
    },
    "United States": {
        "summary": "Confident, impact-driven, metrics-heavy",
        "tone": "Confident, impact-driven, concise, metrics and outcomes where possible.",
        "opening": "Lead with your biggest relevant quantified win in sentence one. If the resume has no numbers, use specific scope without inventing metrics.",
        "structure": "Hook intro, impact paragraph with numbers or scope, skills alignment, confident call-to-action close.",
        "emphasis": "Metrics, scale, impact, leadership, speed, business outcomes.",
        "avoid": "Humble hedging, passive voice, European understatement, excessive length, overly cautious phrasing.",
        "certainty_style": "Use confident action verbs: 'led', 'shipped', 'reduced', 'scaled'.",
        "proof_style": "Prefer one strong measurable story. Keep the total letter concise and outcome-focused.",
        "company_fit_style": "Tie your impact to the product and business goals inferred from the JD.",
        "salutation": "Dear Hiring Manager,",
        "closing": "Best regards,",
        "call_to_action": "Close with a confident request for the next steps and an invitation to discuss.",
        "length": "280-360 words",
        "include_language_note": False,
    },
}

COUNTRY_STYLE_RULES: dict[str, str] = {
    name: str(cfg["summary"]) for name, cfg in MARKET_CONFIG.items()
}

# Visible differentiators per market (merged into prompts and API)
MARKET_DIFFERENTIATORS: dict[str, dict[str, str]] = {
    "Europe": {
        "differentiator": "Modest, evidence-first EU tone. Qualifications over hype.",
        "example_opening": "I am applying for the Senior Software Engineer role. My background in backend systems aligns well with your platform team.",
        "soft_skills_angle": "Frame traits as reliable, collaborative, and EU work-culture aware. Stay understated.",
        "signature_phrases": "My experience aligns well with; I would welcome the opportunity",
        "vs_us": "Less bold than US letters. No aggressive self-promotion or metric hooks in the opening.",
    },
    "Germany": {
        "differentiator": "Direct, formal, qualification-heavy. Facts and credentials first.",
        "example_opening": "I am applying for the Software Engineer position. My qualifications in Python and distributed systems match your requirements.",
        "soft_skills_angle": "Frame traits as methodical, precise, structured, and dependable. Sound factual not emotional.",
        "signature_phrases": "I am applying for; My qualifications include; I deliver reliably",
        "vs_us": "More formal and credential-focused than US or UK. Low enthusiasm, high precision.",
    },
    "France": {
        "differentiator": "Motivation and company mission come before skills. Polished and courteous.",
        "example_opening": "I am particularly interested in the Backend Engineer role and your mission to simplify B2B payments across Europe.",
        "soft_skills_angle": "Frame traits as motivated, adaptable, professional, and long-term oriented toward the company.",
        "signature_phrases": "I am particularly interested in; I believe my experience; your mission",
        "vs_us": "Leads with why the company, not a metric hook. More formal than UK/Ireland.",
    },
    "United Kingdom": {
        "differentiator": "Brief, formal, understated. Modest confidence only.",
        "example_opening": "I am writing to apply for the Platform Engineer role. I believe my experience could contribute to your team.",
        "soft_skills_angle": "Frame traits quietly: capable, considered, professional. Avoid sounding boastful.",
        "signature_phrases": "I would welcome the opportunity; I believe I can contribute; thank you for considering",
        "vs_us": "Shorter and more restrained than US. Never say 'perfect candidate' or oversell.",
    },
    "Ireland": {
        "differentiator": "Warm, personable, team-focused. Friendly but still professional.",
        "example_opening": "I would like to apply for the Full Stack Engineer role. I enjoy building products with collaborative teams and would be glad to contribute here.",
        "soft_skills_angle": "Frame traits around teamwork, communication, and shared outcomes. Sound approachable.",
        "signature_phrases": "I enjoy collaborating; I have delivered with teams; I would be glad to contribute",
        "vs_us": "Warmer and more people-focused than UK. Less metric-heavy than US.",
    },
    "Canada": {
        "differentiator": "Polite, clear, achievement-led. Courteous but direct.",
        "example_opening": "I am pleased to apply for the Senior Developer role. I am keen to contribute my experience in scalable web platforms to your team.",
        "soft_skills_angle": "Frame traits as inclusive, clear communicators who collaborate respectfully.",
        "signature_phrases": "I would be pleased to; I am keen to contribute; thank you for your consideration",
        "vs_us": "Politer and less aggressive than US. Acknowledge bilingual context when relevant.",
    },
    "Australia": {
        "differentiator": "Straightforward, practical, no fluff. Outcomes without hype.",
        "example_opening": "I am applying for the Software Engineer role. I have delivered production APIs and frontend features in agile teams and can contribute from day one.",
        "soft_skills_angle": "Frame traits as hands-on, practical, and get-things-done. Plain English.",
        "signature_phrases": "I have delivered; I can hit the ground running; happy to discuss",
        "vs_us": "More direct and less formal than UK. Less hype than US but still confident.",
    },
    "New Zealand": {
        "differentiator": "Humble, collaborative, practical. Understated confidence.",
        "example_opening": "I am applying for the Developer role. I can contribute practical experience in backend services and work well in small, collaborative teams.",
        "soft_skills_angle": "Frame traits as helpful, team-minded, and grounded. Avoid self-praise.",
        "signature_phrases": "I can contribute by; I work well with teams; keen to support",
        "vs_us": "More humble than Australia/US. Emphasise team over individual glory.",
    },
    "Singapore": {
        "differentiator": "Precise, efficient, skills-first. Multicultural and execution-focused.",
        "example_opening": "I am applying for the Software Engineer role. I am proficient in Python and React and adapt quickly in multicultural engineering teams.",
        "soft_skills_angle": "Frame traits as efficient, adaptable, stakeholder-aware, and fast to ramp up.",
        "signature_phrases": "I am proficient in; I adapt quickly; I work effectively across teams",
        "vs_us": "More concise and skills-forward than US. Highlight multicultural adaptability.",
    },
    "United States": {
        "differentiator": "Confident, impact-driven. Lead with outcomes and ownership.",
        "example_opening": "I led the migration of a monolith to microservices serving 2M+ monthly requests, and I would love to bring that ownership mindset to your Platform team.",
        "soft_skills_angle": "Frame traits boldly: ownership, bias for action, results-oriented, proactive.",
        "signature_phrases": "I led; I shipped; I would love to bring; excited to discuss next steps",
        "vs_us": "Most confident market. Use strong verbs. Ask clearly for next steps.",
    },
    "Other": {
        "differentiator": "Neutral, adaptable tone tailored to the country you specify.",
        "example_opening": "I am applying for the Software Engineer role. My experience aligns with the responsibilities outlined in your job description.",
        "soft_skills_angle": "Frame traits as professional, adaptable, and respectful of local team norms.",
        "signature_phrases": "My experience aligns with; I would welcome the opportunity; I can contribute",
        "vs_us": "Balanced tone. Neither US hype nor EU understatement unless the country suggests it.",
    },
}


def _get_market_cfg(market: str) -> dict[str, Any]:
    cfg = dict(MARKET_CONFIG[market])
    cfg.update(MARKET_DIFFERENTIATORS.get(market, {}))
    return cfg


def _format_market_signature(cfg: dict[str, Any], style: str) -> str:
    return f"""STYLE SIGNATURE ({style}) - the letter MUST read distinctly {style}, not generic:
- Summary: {cfg.get("summary", "")}
- How to open: {cfg.get("opening", "")}
- Proof paragraph angle: {cfg.get("proof_style", "")}
- Soft skills paragraph angle: {cfg.get("soft_skills_angle", "")}
- Salutation: {cfg.get("salutation", "")} | Closing: {cfg.get("closing", "")}
- Call to action style: {cfg.get("call_to_action", "")}"""

LANGUAGE_NOTE_REQUIRED = """
REQUIRED LANGUAGE WILLINGNESS (you MUST include this for this market):
- Add 1-2 natural sentences in English near the end of the letter.
- State clearly that you are happy and motivated to learn {language_focus}.
- Say you are confident you can reach professional working proficiency within one year.
- Make clear that language is not a long-term barrier for you in this role.
- If the resume already shows language skill, acknowledge it honestly without overstating.
- Do not claim current fluency unless the resume supports it.
- Example (adapt naturally): "I am happy to learn German and am confident I can reach professional working proficiency within a year. Language will not be a barrier to my contribution in this role."
"""

COVER_LETTER_RULES = """
WHAT A COVER LETTER IS:
A short, human letter for ONE job. Brief interest + one proof point + how you work. NOT a resume in prose.

FORBIDDEN:
- Do NOT write two long paragraphs stacking multiple jobs, internships, and metrics.
- Do NOT walk through the resume role-by-role ("At X... Previously at Y... At Z...").
- Do NOT list more than ONE past role as evidence in the entire letter.
- Do NOT dump technologies, tools, or comma-separated skills.
- Do NOT use bullet points or numbered lists in the body.
- Do NOT paste resume summary, skills block, or education.
- Avoid hollow filler: "passionate", "excited to apply", "perfect fit", "dynamic team player".

REQUIRED STRUCTURE (follow the LENGTH TARGET in the user prompt; exclude salutation and sign-off from the count):

1. OPENING (1-2 sentences): Role you are applying for + why this company/role (use company research or JD). No biography.

2. BODY PARAGRAPH 1 - PROOF:
   - Pick the single strongest JD requirement.
   - Support it with ONE example from ONE role on the resume only.
   - At most one metric if the resume has one. No second job. No "Previously..." or "At [other company]...".
   - End by linking to the role: "This maps to your need for..."

3. BODY PARAGRAPH 2 - HOW YOU WORK:
   - Describe work style and character: disciplined, hardworking, self-directed, calm under ambiguity, able to turn vague problems into clear plans, collaborative, ownership-minded, reliable delivery.
   - Ground this in the resume's themes (e.g. production systems, data, AI) without re-listing employers or metrics.
   - Sound like a real person, not a buzzword list. No new job titles or project names here.

4. CLOSE (1-2 sentences): Professional sign-off per market rules. Language-learning note only when instructed.

SELECTION DISCIPLINE:
- One resume example total in the entire letter.
- If the resume has many roles, ignore all but the best match for the JD.
- Hit the LENGTH TARGET in the user prompt for total body word count.
- Maximum 2 body paragraphs between opening and closing. No third or fourth proof paragraphs.

BAD (never write like this):
"In my current role at X I did A, B, C... Previously at Y I did D, E, F... At Z I did G, H, I..."
That is a resume rewrite. Reject it.

GOOD (write like this):
"Dear Hiring Manager,

I am applying for the [Role] at [Company]. [One sentence on why the company/role matters.]

In my work at [one employer], I [one concrete outcome tied to one JD need]. This maps directly to your focus on [JD theme].

I am disciplined and self-directed, especially when problems are underspecified. I break vague requirements into clear steps, communicate early with stakeholders, and follow through reliably. I work well in collaborative teams and stay calm when priorities shift.

[Optional language note if required.] I would welcome the opportunity to discuss the role.

Yours sincerely,
[Name]"
"""

SYSTEM_PROMPT = f"""You are an expert international tech career writing assistant. Write compelling, human-sounding cover letters for tech roles.

{COVER_LETTER_RULES}

Each market has DISTINCT rules for tone, opening, emphasis, and length. Apply market rules on top of the letter flow above.

CRITICAL LANGUAGE RULES:
- Write the ENTIRE cover letter in English only.
- Do NOT write in German, French, Dutch, or any other local language.
- Do NOT use non-English salutations, subject lines (Betreff), or letter formats.
- Use standard English business letter structure with salutation and closing per market rules.
- Never use em dashes or en dashes. Use commas, periods, or hyphens (-) instead.

Content rules:
- Do not invent experience. Use only facts supported by the resume.
- Prioritize the job description: address its top requirements directly.
- When COMPANY RESEARCH is provided, use it for a genuine company-fit paragraph. Do not invent company facts.

Before writing: (1) pick the top JD requirement, (2) find ONE resume proof for it, (3) write para 2 about work ethic and problem-solving style without naming more roles.

Return valid JSON only, with no markdown fences or extra text:
{{
  "cover_letter": "...",
  "quality_analysis": {{
    "ats_keyword_match_score": 0-100,
    "missing_skills": [],
    "strongest_matches": [],
    "tone_score": 0-100,
    "improvement_suggestions": []
  }}
}}"""


def _format_market_rules(cfg: dict[str, Any], *, letter_length: str = "short") -> str:
    ordered_fields = [
        ("Tone", "tone"),
        ("Opening style", "opening"),
        ("Structure", "structure"),
        ("What to emphasize", "emphasis"),
        ("What to avoid", "avoid"),
        ("Certainty style", "certainty_style"),
        ("Proof style", "proof_style"),
        ("Company fit style", "company_fit_style"),
        ("Salutation", "salutation"),
        ("Closing", "closing"),
        ("Call to action", "call_to_action"),
        ("Target length", "length"),
    ]

    lines: list[str] = []
    for label, key in ordered_fields:
        if key == "length":
            lines.append(f"{label}: {_style_length_label(letter_length)}")
            continue
        if key in cfg and cfg[key]:
            lines.append(f"{label}: {cfg[key]}")

    return "\n".join(lines)


def _build_language_block(
    *,
    language: str | None = None,
    is_citizen: bool | None = None,
) -> str:
    if is_citizen or not language or not language.strip():
        return ""
    return LANGUAGE_NOTE_REQUIRED.format(language_focus=language.strip())


def _guess_job_title(job_description: str, role_title: str | None = None) -> str:
    if role_title and role_title.strip():
        return role_title.strip()
    for line in job_description.strip().splitlines():
        line = line.strip()
        if line and len(line) < 120:
            return line
    return "this role"


def _format_length_block(letter_length: str) -> str:
    if letter_length == "standard":
        return (
            "LENGTH TARGET (MANDATORY): standard - 220-280 words in the body, excluding salutation and sign-off. "
            "Do NOT write fewer than 220 body words. "
            "Opening: 2-3 sentences. Proof paragraph: 5-6 sentences. Work-style paragraph: 5-6 sentences. Close: 2 sentences."
        )
    return (
        "LENGTH TARGET (MANDATORY): short - 150-200 words in the body, excluding salutation and sign-off. "
        "Strict cap at 200 body words. "
        "Opening: 1-2 sentences. Proof paragraph: 3-4 sentences. Work-style paragraph: 3-5 sentences. Close: 1-2 sentences."
    )


def _style_length_label(letter_length: str) -> str:
    if letter_length == "standard":
        return "220-280 words"
    return "150-200 words"


def _format_personalization_block(
    *,
    role_title: str | None,
    hiring_manager_name: str | None,
    cfg: dict[str, Any],
) -> str:
    lines: list[str] = []
    if role_title and role_title.strip():
        lines.append(f"Role title to use in opening: {role_title.strip()}")
    if hiring_manager_name and hiring_manager_name.strip():
        lines.append(f"Salutation MUST be: Dear {hiring_manager_name.strip()},")
    else:
        lines.append(f"Salutation: {cfg.get('salutation', 'Dear Hiring Manager,')}")
    lines.append(f"Closing: {cfg.get('closing', 'Yours sincerely,')}")
    return "\n".join(lines)


def _merge_soft_skills(
    evidence: dict[str, Any], soft_skills: list[str] | None
) -> dict[str, Any]:
    if not soft_skills:
        return evidence
    cleaned = [s.strip() for s in soft_skills if s and s.strip()][:6]
    if not cleaned:
        return evidence
    merged = dict(evidence)
    merged["work_style_themes"] = cleaned
    merged["user_soft_skills"] = cleaned
    return merged


def _format_evidence_pack(evidence: dict[str, Any]) -> str:
    themes_list = evidence.get("user_soft_skills") or evidence.get("work_style_themes") or []
    themes = ", ".join(themes_list)
    skills_instruction = ""
    if evidence.get("user_soft_skills"):
        skills_instruction = (
            "\nUSER-SELECTED SOFT SKILLS (paragraph 2 MUST weave in ALL of these naturally): "
            + "; ".join(evidence["user_soft_skills"])
        )
    forbidden = evidence.get("forbidden_employers") or []
    forbidden_block = ""
    if forbidden:
        forbidden_block = (
            "\nFORBIDDEN (never mention these employers, education, internships, or open source): "
            + ", ".join(forbidden)
        )
    return f"""SELECTED EVIDENCE (the ONLY job experience you may cite in the entire letter):
Employer: {evidence.get("employer", "")}
Role: {evidence.get("role_title", "")}
Proof (copy closely, max 2 sentences, do not add more metrics): {evidence.get("evidence", "")}
Maps to JD need: {evidence.get("jd_link", "")}
{forbidden_block}

WORK STYLE THEMES for paragraph 2 (no employer names, no metrics, no education, no open source):
{themes or "disciplined, self-directed, turns vague problems into clear plans, reliable delivery, collaborative"}
{skills_instruction}

Candidate name for sign-off: {evidence.get("candidate_name") or "[Your name]"}

CRITICAL: No second job. No "Previously". No academic background paragraph. No skills list."""


def _build_user_prompt(
    job_description: str,
    letter_style: str,
    evidence: dict[str, Any],
    *,
    country: str | None = None,
    language: str | None = None,
    is_citizen: bool | None = None,
    company_name: str | None = None,
    role_title: str | None = None,
    hiring_manager_name: str | None = None,
    letter_length: str = "short",
    company_research_summary: str | None = None,
    retry_note: str | None = None,
) -> str:
    cfg = get_style_cfg(letter_style)
    market_rules = _format_market_rules(cfg, letter_length=letter_length)
    style_signature = _format_market_signature(cfg, letter_style)
    language_block = _build_language_block(language=language, is_citizen=is_citizen)

    location_block = ""
    if country and country.strip():
        citizen_note = (
            "Applicant is a citizen. Do NOT mention visa, relocation, or work authorization."
            if is_citizen
            else "Applicant is not a citizen. Do NOT mention visa unless the JD requires it."
        )
        location_block = f"""
Target country: {country.strip()}
- Lightly tailor cultural tone to {country.strip()} if relevant.
- {citizen_note}
"""

    company_block = ""
    if company_name:
        company_block = f"\nCompany name: {company_name}\n"
        if company_research_summary:
            company_block += f"""
COMPANY RESEARCH (from public sources - use for company-fit only, do not invent beyond this):
{company_research_summary}

Use this research to write 1-2 sentences showing you understand what {company_name} does and why you want to work there.
"""
        else:
            company_block += (
                f"\nNo external research was found for {company_name}. "
                "Use the job description for company context only.\n"
            )

    retry_block = f"\nRETRY INSTRUCTION:\n{retry_note}\n" if retry_note else ""
    personalization = _format_personalization_block(
        role_title=role_title,
        hiring_manager_name=hiring_manager_name,
        cfg=cfg,
    )
    length_block = _format_length_block(letter_length)
    resolved_role = _guess_job_title(job_description, role_title)

    return f"""Letter style: {letter_style}
{location_block}
{style_signature}

PERSONALIZATION:
{personalization}
{length_block}

STYLE RULES (follow all of these closely):
{market_rules}
{language_block}
{company_block}
{_format_evidence_pack(evidence)}
{retry_block}
JOB DESCRIPTION:
{job_description}

TASK:
Write a cover letter in English using the {letter_style} style for the {resolved_role} role.

Exact structure (must satisfy LENGTH TARGET above):
- Opening: role + why this company/role
- Paragraph 1: ONLY the selected evidence above. One employer only. Expand detail to reach target length.
- Paragraph 2: Work style only. Use USER-SELECTED SOFT SKILLS framed with the soft_skills_angle above. No job titles. No metrics.
- Close: professional sign-off (+ language note if required)

Exactly 2 body paragraphs. Zero other employers.

In quality_analysis:
- ats_keyword_match_score: how well resume keywords align with the JD (0-100)
- missing_skills: skills in JD not clearly supported by resume
- strongest_matches: top resume-JD alignments (the 2-3 you used in the letter)
- tone_score: how well tone matches the {letter_style} style (0-100)
- improvement_suggestions: 2-4 actionable tips"""


def get_market_summaries() -> list[dict[str, Any]]:
    return get_style_summaries()


def _sanitize_no_em_dashes(text: str) -> str:
    for dash in ("\u2014", "\u2013"):
        text = text.replace(f" {dash} ", ", ")
        text = text.replace(dash, ", ")
    text = re.sub(r",\s*,", ",", text)
    text = re.sub(r"\s+,", ",", text)
    text = re.sub(r",\s+\.", ".", text)
    text = re.sub(r"  +", " ", text)
    return text.strip()


def _normalize_analysis(data: dict) -> QualityAnalysis:
    analysis = data.get("quality_analysis") or {}

    def as_int(value, default=0) -> int:
        try:
            return max(0, min(100, int(value)))
        except (TypeError, ValueError):
            return default

    def as_list(value) -> list[str]:
        if not isinstance(value, list):
            return []
        return [
            _sanitize_no_em_dashes(str(item).strip())
            for item in value
            if str(item).strip()
        ]

    return QualityAnalysis(
        ats_keyword_match_score=as_int(analysis.get("ats_keyword_match_score"), 50),
        missing_skills=as_list(analysis.get("missing_skills")),
        strongest_matches=as_list(analysis.get("strongest_matches")),
        tone_score=as_int(analysis.get("tone_score"), 50),
        improvement_suggestions=as_list(analysis.get("improvement_suggestions")),
    )


async def _fetch_generation_context(
    resume_text: str,
    job_description: str,
    company_name: str | None,
) -> tuple[dict[str, Any], CompanyResearch | None, str | None]:
    """Load evidence and optional company research in parallel (cached when possible)."""
    evidence_task = get_cover_letter_evidence(resume_text, job_description)
    if company_name and company_name.strip():
        research_task = research_company(company_name.strip())
        evidence, raw = await asyncio.gather(evidence_task, research_task)
        company_research = CompanyResearch(
            company_name=raw["company_name"],
            found=raw["found"],
            summary=raw["summary"],
            sources=raw.get("sources", []),
        )
        return evidence, company_research, raw.get("summary") or None
    evidence = await evidence_task
    return evidence, None, None


async def _call_mistral_generate(
    user_prompt: str,
    *,
    max_tokens: int = 900,
) -> dict:
    api_key = os.getenv("MISTRAL_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MISTRAL_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
    }
    client = get_http_client()
    response = await client.post(MISTRAL_API_URL, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


async def _generate_letter_for_style(
    *,
    resume_text: str,
    job_description: str,
    letter_style: str,
    evidence: dict[str, Any],
    letter_length: str = "short",
    country: str | None = None,
    language: str | None = None,
    is_citizen: bool | None = None,
    company_name: str | None = None,
    role_title: str | None = None,
    hiring_manager_name: str | None = None,
    research_summary: str | None = None,
) -> GenerateCoverLetterResponse:
    cfg = get_style_cfg(letter_style)
    cover_letter = ""
    parsed: dict = {}
    retry_note: str | None = None
    issues: list[str] = []
    json_failed = False
    max_tokens = 720 if letter_length == "short" else 1024
    max_attempts = 3 if letter_length == "standard" else 2

    for attempt in range(max_attempts):
        user_prompt = _build_user_prompt(
            job_description,
            letter_style,
            evidence,
            country=country,
            language=language,
            is_citizen=is_citizen,
            company_name=company_name,
            role_title=role_title,
            hiring_manager_name=hiring_manager_name,
            letter_length=letter_length,
            company_research_summary=research_summary,
            retry_note=retry_note,
        )
        try:
            body = await _call_mistral_generate(user_prompt, max_tokens=max_tokens)
            content = body["choices"][0]["message"]["content"] or ""
            parsed = parse_generation_payload(content)
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text[:500] if exc.response else str(exc)
            raise HTTPException(status_code=502, detail=f"Mistral API error: {detail}") from exc
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"Could not reach Mistral API: {exc}") from exc
        except (KeyError, IndexError, json.JSONDecodeError, ValueError):
            json_failed = True
            retry_note = (
                "Return ONLY valid JSON with cover_letter and quality_analysis. No markdown."
            )
            continue

        json_failed = False
        cover_letter = _sanitize_no_em_dashes(str(parsed.get("cover_letter", "")).strip())
        if not cover_letter:
            retry_note = "cover_letter field was empty."
            continue

        issues = looks_like_resume_dump(
            cover_letter,
            evidence.get("employer", ""),
            evidence.get("forbidden_employers"),
            letter_length=letter_length,
        )
        if not issues:
            if letter_length == "standard":
                body_words = count_body_words(cover_letter)
                if body_words < 220 and attempt < max_attempts - 1:
                    retry_note = (
                        f"TOO SHORT: body is only {body_words} words. "
                        "MANDATORY: expand to 220-280 body words (excluding salutation and sign-off). "
                        "Add richer detail to the proof and work-style paragraphs. "
                        "Do not add employers, resume dumps, or bullet lists."
                    )
                    continue
            break

        length_hint = (
            "220-280 body words."
            if letter_length == "standard"
            else "150-200 body words max."
        )
        retry_note = (
            f"REJECTED: {', '.join(issues)}. Only employer: {evidence.get('employer')}. "
            f"{length_hint} One proof para + one soft-skills para only."
        )

    if issues or json_failed or not cover_letter:
        lang_focus = language.strip() if language and language.strip() else "the local language"
        include_lang = bool(language and language.strip()) and not is_citizen
        salutation = (
            f"Dear {hiring_manager_name.strip()},"
            if hiring_manager_name and hiring_manager_name.strip()
            else str(cfg.get("salutation", "Dear Hiring Manager,"))
        )
        cover_letter = build_template_letter(
            evidence,
            company_name=company_name,
            job_title=_guess_job_title(job_description, role_title),
            target_country=letter_style,
            europe_country=country,
            include_language_note=include_lang,
            language_focus=lang_focus,
            salutation=salutation,
            closing=str(cfg.get("closing", "Yours sincerely,")),
            soft_skills=evidence.get("user_soft_skills"),
        )
        cover_letter = _sanitize_no_em_dashes(cover_letter)
        parsed = {
            "cover_letter": cover_letter,
            "quality_analysis": parsed.get("quality_analysis") or {
                "ats_keyword_match_score": 75,
                "missing_skills": [],
                "strongest_matches": [evidence.get("jd_link", "")],
                "tone_score": 80,
                "improvement_suggestions": [],
            },
        }

    return GenerateCoverLetterResponse(
        cover_letter=cover_letter,
        quality_analysis=_normalize_analysis(parsed),
        company_research=None,
    )


async def generate_cover_letter(
    resume_text: str,
    job_description: str,
    letter_style: str,
    *,
    letter_length: str = "short",
    country: str | None = None,
    language: str | None = None,
    is_citizen: bool | None = None,
    company_name: str | None = None,
    role_title: str | None = None,
    hiring_manager_name: str | None = None,
    soft_skills: list[str] | None = None,
) -> GenerateCoverLetterResponse:
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="MISTRAL_API_KEY is not configured. Set it in backend/.env",
        )

    if letter_style not in LETTER_STYLES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported style: {letter_style}. Choose: {', '.join(LETTER_STYLES)}",
        )

    evidence, company_research, research_summary = await _fetch_generation_context(
        resume_text,
        job_description,
        company_name,
    )
    evidence = _merge_soft_skills(evidence, soft_skills)

    result = await _generate_letter_for_style(
        resume_text=resume_text,
        job_description=job_description,
        letter_style=letter_style,
        evidence=evidence,
        letter_length=letter_length,
        country=country.strip() if country else None,
        language=language.strip() if language else None,
        is_citizen=bool(is_citizen) if country else None,
        company_name=company_name.strip() if company_name else None,
        role_title=role_title.strip() if role_title else None,
        hiring_manager_name=hiring_manager_name.strip() if hiring_manager_name else None,
        research_summary=research_summary,
    )
    result.company_research = company_research
    return result


async def compare_cover_letter_styles(
    resume_text: str,
    job_description: str,
    style_a: str,
    style_b: str,
    *,
    letter_length: str = "short",
    country: str | None = None,
    language: str | None = None,
    is_citizen: bool | None = None,
    company_name: str | None = None,
    role_title: str | None = None,
    hiring_manager_name: str | None = None,
    soft_skills: list[str] | None = None,
) -> dict[str, Any]:
    if style_a not in LETTER_STYLES or style_b not in LETTER_STYLES:
        raise HTTPException(status_code=400, detail="Unsupported style in compare request.")
    if style_a == style_b:
        raise HTTPException(status_code=400, detail="Pick two different styles to compare.")

    evidence, company_research, research_summary = await _fetch_generation_context(
        resume_text,
        job_description,
        company_name,
    )
    evidence = _merge_soft_skills(evidence, soft_skills)

    common = {
        "resume_text": resume_text,
        "job_description": job_description,
        "evidence": evidence,
        "letter_length": letter_length,
        "country": country.strip() if country else None,
        "language": language.strip() if language else None,
        "is_citizen": bool(is_citizen) if country else None,
        "company_name": company_name.strip() if company_name else None,
        "role_title": role_title.strip() if role_title else None,
        "hiring_manager_name": hiring_manager_name.strip() if hiring_manager_name else None,
        "research_summary": research_summary,
    }

    result_a, result_b = await asyncio.gather(
        _generate_letter_for_style(letter_style=style_a, **common),
        _generate_letter_for_style(letter_style=style_b, **common),
    )

    return {
        "letters": {
            style_a: result_a.cover_letter,
            style_b: result_b.cover_letter,
        },
        "quality_analysis": {
            style_a: result_a.quality_analysis.model_dump(),
            style_b: result_b.quality_analysis.model_dump(),
        },
        "company_research": company_research,
    }
