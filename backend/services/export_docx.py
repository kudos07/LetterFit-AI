import io

from docx import Document
from docx.shared import Pt
from fastapi.responses import StreamingResponse


def build_docx_bytes(cover_letter: str) -> bytes:
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    for paragraph in cover_letter.split("\n"):
        p = doc.add_paragraph(paragraph if paragraph else "")
        p.paragraph_format.space_after = Pt(6)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def docx_response(cover_letter: str, filename: str = "cover_letter.docx") -> StreamingResponse:
    safe_name = filename if filename.endswith(".docx") else f"{filename}.docx"
    content = build_docx_bytes(cover_letter)

    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}"'},
    )
