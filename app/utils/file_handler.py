import os
from pdfminer.high_level import extract_text as pdfminer_extract
from docx import Document

def extract_text(file_path):
    try:
        file_path = file_path.lower()

        if file_path.endswith(".txt"):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()

        elif file_path.endswith(".docx"):
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])

        elif file_path.endswith(".pdf"):
            return pdfminer_extract(file_path)

        else:
            return "ERROR: Unsupported file format"

    except Exception as e:
        print(f"[ERROR in extract_text] {e}")
        return f"ERROR: {e}"
