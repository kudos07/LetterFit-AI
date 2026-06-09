from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import (
    CompareStylesRequest,
    CompareStylesResponse,
    ExportDocxRequest,
    ExportPdfRequest,
    GenerateCoverLetterRequest,
    GenerateCoverLetterResponse,
    QualityAnalysis,
    RegenerateParagraphRequest,
    RegenerateParagraphResponse,
    UploadResumeResponse,
)
from services.export_docx import docx_response
from services.export_pdf import pdf_response
from services.mistral_service import (
    compare_cover_letter_styles,
    generate_cover_letter,
    get_market_summaries,
)
from services.paragraph_regenerator import regenerate_paragraph
from services.parser import parse_resume
from services.style_config import STYLE_IDS

load_dotenv()

app = FastAPI(
    title="LetterFit AI",
    description="Generate English cover letters with tone presets, optional country and language context.",
    version="1.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/styles")
async def list_styles():
    return {"styles": STYLE_IDS, "presets": get_market_summaries()}


@app.get("/countries")
async def list_countries():
    return await list_styles()


@app.post("/upload-resume", response_model=UploadResumeResponse)
async def upload_resume(file: UploadFile = File(...)):
    resume_text, filename = await parse_resume(file)
    return UploadResumeResponse(resume_text=resume_text, filename=filename)


@app.post("/generate-cover-letter", response_model=GenerateCoverLetterResponse)
async def generate_cover_letter_route(payload: GenerateCoverLetterRequest):
    return await generate_cover_letter(
        resume_text=payload.resume_text,
        job_description=payload.job_description,
        letter_style=payload.letter_style,
        letter_length=payload.letter_length,
        country=payload.country,
        language=payload.language,
        is_citizen=payload.is_citizen,
        company_name=payload.company_name,
        role_title=payload.role_title,
        hiring_manager_name=payload.hiring_manager_name,
        soft_skills=payload.soft_skills,
    )


@app.post("/compare-styles", response_model=CompareStylesResponse)
async def compare_styles_route(payload: CompareStylesRequest):
    raw = await compare_cover_letter_styles(
        resume_text=payload.resume_text,
        job_description=payload.job_description,
        style_a=payload.style_a,
        style_b=payload.style_b,
        letter_length=payload.letter_length,
        country=payload.country,
        language=payload.language,
        is_citizen=payload.is_citizen,
        company_name=payload.company_name,
        role_title=payload.role_title,
        hiring_manager_name=payload.hiring_manager_name,
        soft_skills=payload.soft_skills,
    )
    return CompareStylesResponse(
        letters=raw["letters"],
        quality_analysis={
            k: QualityAnalysis(**v) for k, v in raw["quality_analysis"].items()
        },
        company_research=raw.get("company_research"),
    )


@app.post("/regenerate-paragraph", response_model=RegenerateParagraphResponse)
async def regenerate_paragraph_route(payload: RegenerateParagraphRequest):
    return await regenerate_paragraph(
        paragraph=payload.paragraph,
        cover_letter=payload.cover_letter,
        resume_text=payload.resume_text,
        job_description=payload.job_description,
        letter_style=payload.letter_style,
        letter_length=payload.letter_length,
        country=payload.country,
        language=payload.language,
        is_citizen=payload.is_citizen,
        company_name=payload.company_name,
        role_title=payload.role_title,
        hiring_manager_name=payload.hiring_manager_name,
        soft_skills=payload.soft_skills,
        focus_skill=payload.focus_skill,
    )


@app.post("/export-docx")
async def export_docx(payload: ExportDocxRequest):
    return docx_response(payload.cover_letter, payload.filename)


@app.post("/export-pdf")
async def export_pdf(payload: ExportPdfRequest):
    return pdf_response(payload.cover_letter, payload.filename)
