import io

from fastapi.responses import StreamingResponse
from fpdf import FPDF


def _safe_text(text: str) -> str:
    """Helvetica in PDF is Latin-1; replace unsupported chars."""
    return text.encode("latin-1", errors="replace").decode("latin-1")


def build_pdf_bytes(cover_letter: str) -> bytes:
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(25, 25, 25)
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)

    for line in cover_letter.split("\n"):
        pdf.multi_cell(0, 6, _safe_text(line) if line else "")
        pdf.ln(1)

    out = pdf.output()
    if isinstance(out, (bytes, bytearray)):
        return bytes(out)
    return out.encode("latin-1")


def pdf_response(cover_letter: str, filename: str = "cover_letter.pdf") -> StreamingResponse:
    safe_name = filename if filename.endswith(".pdf") else f"{filename}.pdf"
    content = build_pdf_bytes(cover_letter)

    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}"'},
    )
