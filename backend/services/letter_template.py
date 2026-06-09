"""Deterministic short cover letter when the LLM keeps dumping the resume."""

from typing import Any


def _style_sentence_from_skills(skills: list[str] | None) -> str:
    if not skills:
        return (
            "I am disciplined, hardworking, and self-directed, especially when requirements "
            "are unclear. I turn vague problems into clear plans, communicate early with "
            "stakeholders, and deliver reliably in collaborative teams."
        )
    lowered = [s.strip().lower() for s in skills if s.strip()]
    if len(lowered) == 1:
        return (
            f"I am {lowered[0]}, especially when requirements are unclear. "
            "I communicate early with stakeholders and follow through reliably."
        )
    if len(lowered) == 2:
        return (
            f"I am {lowered[0]} and {lowered[1]}, especially when problems are underspecified. "
            "I communicate early with stakeholders and deliver consistently."
        )
    core = ", ".join(lowered[:-1])
    return (
        f"I am {core}, and {lowered[-1]}, especially when requirements are unclear. "
        "I turn vague asks into clear plans and follow through reliably in collaborative teams."
    )


def build_template_letter(
    evidence: dict[str, Any],
    *,
    company_name: str | None,
    job_title: str | None,
    target_country: str,
    europe_country: str | None,
    include_language_note: bool,
    language_focus: str,
    salutation: str = "Dear Hiring Manager,",
    closing: str = "Yours sincerely,",
    soft_skills: list[str] | None = None,
) -> str:
    name = evidence.get("candidate_name") or ""
    company = company_name or "your company"
    role = job_title or "this position"
    proof = evidence.get("evidence", "")
    jd_link = evidence.get("jd_link", "the role requirements")
    employer = evidence.get("employer", "")

    style_sentence = _style_sentence_from_skills(soft_skills)

    location = f" I am based in {europe_country}." if europe_country else ""
    lang_block = ""
    if include_language_note:
        lang_block = (
            f" I am happy to learn {language_focus} and am confident I can reach "
            "professional working proficiency within one year. Language will not be a "
            "barrier to my contribution in this role."
        )

    opening = (
        f"I am applying for the {role} at {company}. "
        f"I am interested in contributing to work that matches {jd_link}."
    )

    proof_para = proof
    if employer and employer.lower() not in proof_para.lower():
        proof_para = f"At {employer}, {proof_para[0].lower() + proof_para[1:] if proof_para else proof_para}"

    body = f"""{salutation}

{opening}

{proof_para} This maps directly to your focus on {jd_link}.

{style_sentence}{location}{lang_block}

I would welcome the opportunity to discuss how I can contribute to your team.

{closing},
{name}"""

    return body.strip()
