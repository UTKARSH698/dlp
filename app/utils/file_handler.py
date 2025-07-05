import os
from pdfminer.high_level import extract_text as pdfminer_extract
from docx import Document

def extract_text(file_path):
    try:
        ext = os.path.splitext(file_path)[1].lower()

        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()

        elif ext == '.docx':
            doc = Document(file_path)
            return '\n'.join([para.text for para in doc.paragraphs])

        elif ext == '.pdf':
            text = pdfminer_extract(file_path)
            if not text.strip():
                raise ValueError("PDF parsed, but no text was extracted. File may be image-only or scanned.")
            return text

        else:
            raise ValueError(f"Unsupported file extension: {ext}")

    except Exception as e:
        print(f"[extract_text ERROR] {e}")
        return f"ERROR: {e}"