"""Letter tone/style presets (replaces country-based markets)."""

from typing import Any

LETTER_STYLES: dict[str, dict[str, Any]] = {
    "Professional": {
        "summary": "Balanced, polished, corporate-safe",
        "tone": "Professional, clear, courteous. Neither stiff nor salesy.",
        "opening": "State the role and a calm one-line fit statement. No hooks or hype.",
        "structure": "Short intro, one proof paragraph, work-style paragraph, polite close.",
        "emphasis": "Role fit, relevant experience, reliability, clear communication.",
        "avoid": "Slang, overselling, resume dumps, buzzword lists.",
        "certainty_style": "Use balanced phrasing: 'My experience aligns with...' 'I can contribute to...'",
        "proof_style": "One concrete example tied to the JD. Factual, modest confidence.",
        "company_fit_style": "Brief company fit from JD or research only.",
        "soft_skills_angle": "Frame traits as reliable, collaborative, and professional.",
        "salutation": "Dear Hiring Manager,",
        "closing": "Yours sincerely,",
        "call_to_action": "Politely request a conversation about the role.",
        "length": "150-200 words",
        "example_opening": "I am applying for the Software Engineer role and believe my experience aligns well with your team's needs.",
    },
    "Qualifications": {
        "summary": "Facts-first, credential-heavy, low hype",
        "tone": "Formal, precise, qualification-focused. Direct and factual.",
        "opening": "State the position and your relevant qualifications immediately.",
        "structure": "Brief motivation, detailed qualifications proof, work style, formal close.",
        "emphasis": "Degrees, years of experience, technical credentials, methodical delivery.",
        "avoid": "Emotional language, vague claims, marketing speak, excessive enthusiasm.",
        "certainty_style": "Be direct: 'I am applying because...' 'My experience includes...'",
        "proof_style": "Concrete delivery details from resume. Credentials before adjectives.",
        "company_fit_style": "Tie reliability and structured delivery to role responsibilities.",
        "soft_skills_angle": "Frame traits as methodical, precise, structured, and dependable.",
        "salutation": "Dear Hiring Team,",
        "closing": "Yours sincerely,",
        "call_to_action": "Request an interview and confirm readiness to contribute.",
        "length": "150-200 words",
        "example_opening": "I am applying for the Backend Engineer position. My qualifications in Python, APIs, and production systems match your requirements.",
    },
    "Hype": {
        "summary": "Confident, enthusiastic, impact-driven",
        "tone": "Confident, energetic, outcome-focused. Strong but still believable.",
        "opening": "Lead with your strongest relevant win or impact in sentence one.",
        "structure": "Hook intro, impact proof, bold work-style close with clear CTA.",
        "emphasis": "Metrics, scale, ownership, speed, business outcomes where resume supports them.",
        "avoid": "Humble hedging, passive voice, long letters, invented metrics.",
        "certainty_style": "Use action verbs: 'led', 'shipped', 'scaled', 'delivered'.",
        "proof_style": "One strong measurable story. Outcome-first framing.",
        "company_fit_style": "Connect your impact to product and business goals from the JD.",
        "soft_skills_angle": "Frame traits boldly: ownership, bias for action, results-oriented.",
        "salutation": "Dear Hiring Manager,",
        "closing": "Best regards,",
        "call_to_action": "Confidently ask for next steps and a discussion.",
        "length": "150-200 words",
        "example_opening": "I shipped FastAPI services handling 2M+ monthly requests and would love to bring that delivery speed to your platform team.",
    },
    "Mix": {
        "summary": "Professional polish plus clear proof points",
        "tone": "Warm-professional blend: credible proof with approachable voice.",
        "opening": "Role plus one-line fit, then a hint of enthusiasm without overselling.",
        "structure": "Friendly intro, solid proof, personable work style, warm close.",
        "emphasis": "Balance facts with motivation. Team fit and outcomes together.",
        "avoid": "Extreme formality, extreme hype, resume dumps.",
        "certainty_style": "Mix evidence and motivation: 'I have delivered X and am keen to contribute Y.'",
        "proof_style": "One proof point with light enthusiasm. Link clearly to JD.",
        "company_fit_style": "Show genuine interest in the company or mission from JD/research.",
        "soft_skills_angle": "Frame traits as collaborative, adaptable, and motivated.",
        "salutation": "Dear Hiring Manager,",
        "closing": "Kind regards,",
        "call_to_action": "Invite a discussion with polite enthusiasm.",
        "length": "150-200 words",
        "example_opening": "I am applying for the Senior Developer role. I have built scalable APIs in agile teams and am keen to contribute to your product roadmap.",
    },
    "Bold": {
        "summary": "High-energy, memorable, attention-grabbing",
        "tone": "Bold, distinctive, high-energy. Memorable opening hook. Still professional for tech.",
        "opening": "Open with a striking hook: a bold claim, sharp contrast, or memorable one-liner tied to the JD. Stand out.",
        "structure": "Punchy hook, vivid proof, confident work-style, strong CTA.",
        "emphasis": "Differentiation, confidence, memorable phrasing, ownership. Make the reader pause.",
        "avoid": "Clichés, generic openings, false claims, arrogance without evidence.",
        "certainty_style": "Write with conviction. Short sentences allowed. Personality is OK.",
        "proof_style": "One vivid proof point. Make it stick. One metric max if real.",
        "company_fit_style": "Show you understand what makes this company/role different.",
        "soft_skills_angle": "Frame traits as fearless problem-solvers who thrive on ambiguity.",
        "salutation": "Dear Hiring Manager,",
        "closing": "Best regards,",
        "call_to_action": "End with a memorable, direct call to action.",
        "length": "150-200 words",
        "example_opening": "Most engineers ship features. I ship systems that stay up under load, and your platform role is exactly where that matters.",
    },
}

STYLE_IDS: list[str] = list(LETTER_STYLES.keys())


def get_style_cfg(style: str) -> dict[str, Any]:
    if style not in LETTER_STYLES:
        raise KeyError(style)
    return dict(LETTER_STYLES[style])


def get_style_summaries() -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for style_id in STYLE_IDS:
        cfg = get_style_cfg(style_id)
        summaries.append(
            {
                "id": style_id,
                "summary": cfg["summary"],
                "example_opening": cfg.get("example_opening", ""),
                "salutation": cfg.get("salutation", ""),
                "closing": cfg.get("closing", ""),
            }
        )
    return summaries
