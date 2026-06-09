"""Optional local quality enrichment helpers.

Primary quality analysis is produced by Mistral during generation.
These utilities can augment scores when needed in future iterations.
"""

from models.schemas import QualityAnalysis


def clamp_score(value: int) -> int:
    return max(0, min(100, value))


def merge_analysis(
    primary: QualityAnalysis,
    *,
    extra_missing: list[str] | None = None,
    extra_matches: list[str] | None = None,
) -> QualityAnalysis:
    missing = list(primary.missing_skills)
    matches = list(primary.strongest_matches)

    if extra_missing:
        seen = {s.lower() for s in missing}
        for skill in extra_missing:
            if skill.lower() not in seen:
                missing.append(skill)
                seen.add(skill.lower())

    if extra_matches:
        seen = {s.lower() for s in matches}
        for match in extra_matches:
            if match.lower() not in seen:
                matches.append(match)
                seen.add(match.lower())

    return QualityAnalysis(
        ats_keyword_match_score=clamp_score(primary.ats_keyword_match_score),
        missing_skills=missing[:10],
        strongest_matches=matches[:10],
        tone_score=clamp_score(primary.tone_score),
        improvement_suggestions=primary.improvement_suggestions[:6],
    )
