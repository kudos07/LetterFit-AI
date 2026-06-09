"""Generate sample_resume.docx for testing uploads."""

from pathlib import Path

from docx import Document
from docx.shared import Pt

SAMPLES_DIR = Path(__file__).resolve().parent
RESUME_TXT = SAMPLES_DIR / "sample_resume.txt"
OUTPUT = SAMPLES_DIR / "sample_resume.docx"


def main():
    text = RESUME_TXT.read_text(encoding="utf-8")
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    for line in text.split("\n"):
        doc.add_paragraph(line)

    doc.save(OUTPUT)
    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    main()
