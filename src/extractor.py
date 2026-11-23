"""Extract readable text from PDF, DOCX and TXT resumes."""
from pathlib import Path
import pdfplumber
from docx import Document

SUPPORTED = {".pdf", ".docx", ".txt"}

def extract_text(file_path: str) -> str:
    path = Path(file_path)
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED:
        raise ValueError(f"Unsupported file type: {suffix}")

    if suffix == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")

    if suffix == ".docx":
        doc = Document(str(path))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        # Include text from tables, which are common in resumes.
        for table in doc.tables:
            for row in table.rows:
                paragraphs.extend(cell.text for cell in row.cells if cell.text.strip())
        return "\n".join(paragraphs)

    pages = []
    with pdfplumber.open(str(path)) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text() or "")
    return "\n".join(pages)
