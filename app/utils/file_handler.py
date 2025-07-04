import os
import pytesseract
from pdf2image import convert_from_path
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
            pages = convert_from_path(file_path)
            text = ""
            for page in pages:
                text += pytesseract.image_to_string(page)
            return text

        else:
            return "ERROR: Unsupported file format"

    except Exception as e:
        print(f"[ERROR in extract_text] {e}")
        return f"ERROR: {e}"
