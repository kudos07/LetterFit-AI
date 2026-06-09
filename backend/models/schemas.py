from typing import Literal

from pydantic import BaseModel, Field


class UploadResumeResponse(BaseModel):
    resume_text: str
    filename: str


class CoverLetterContextRequest(BaseModel):
    resume_text: str = Field(..., min_length=10)
    job_description: str = Field(..., min_length=10)
    letter_length: Literal["short", "standard"] = Field(
        default="short",
        description="short = 150-200 words body; standard = 220-280 words",
    )
    country: str | None = Field(default=None)
    language: str | None = Field(default=None)
    is_citizen: bool | None = Field(default=None)
    company_name: str | None = Field(default=None)
    role_title: str | None = Field(
        default=None,
        description="Override role title in opening (if JD title is vague)",
    )
    hiring_manager_name: str | None = Field(
        default=None,
        description="Personalized salutation, e.g. Dear Alex Smith,",
    )
    soft_skills: list[str] | None = Field(default=None, max_length=6)


class GenerateCoverLetterRequest(CoverLetterContextRequest):
    letter_style: str = Field(
        ...,
        description="Tone preset: Professional, Qualifications, Hype, Mix, or Bold",
    )


class QualityAnalysis(BaseModel):
    ats_keyword_match_score: int = Field(..., ge=0, le=100)
    missing_skills: list[str]
    strongest_matches: list[str]
    tone_score: int = Field(..., ge=0, le=100)
    improvement_suggestions: list[str]


class CompanyResearch(BaseModel):
    company_name: str
    found: bool
    summary: str
    sources: list[str] = []


class GenerateCoverLetterResponse(BaseModel):
    cover_letter: str
    quality_analysis: QualityAnalysis
    company_research: CompanyResearch | None = None


class CompareStylesRequest(CoverLetterContextRequest):
    style_a: str
    style_b: str


class CompareStylesResponse(BaseModel):
    letters: dict[str, str]
    quality_analysis: dict[str, QualityAnalysis]
    company_research: CompanyResearch | None = None


class RegenerateParagraphRequest(BaseModel):
    paragraph: Literal["opening", "proof", "soft_skills", "close"]
    cover_letter: str = Field(..., min_length=20)
    resume_text: str = Field(..., min_length=10)
    job_description: str = Field(..., min_length=10)
    letter_style: str
    letter_length: Literal["short", "standard"] = "short"
    country: str | None = None
    language: str | None = None
    is_citizen: bool | None = None
    company_name: str | None = None
    role_title: str | None = None
    hiring_manager_name: str | None = None
    soft_skills: list[str] | None = Field(default=None, max_length=6)
    focus_skill: str | None = Field(
        default=None,
        description="When regenerating proof, prioritize addressing this JD skill",
    )


class RegenerateParagraphResponse(BaseModel):
    paragraph: str
    paragraph_text: str
    cover_letter: str


class ExportDocxRequest(BaseModel):
    cover_letter: str = Field(..., min_length=1)
    filename: str = "cover_letter.docx"


class ExportPdfRequest(BaseModel):
    cover_letter: str = Field(..., min_length=1)
    filename: str = "cover_letter.pdf"
