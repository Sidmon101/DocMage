import fitz  # PyMuPDF
import docx
import os

def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_text_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def extract_text(file_path, doc_type):
    if os.path.exists(file_path):
        if doc_type == 'pdf':
            return extract_text_from_pdf(file_path)
        elif doc_type == 'docx':
            return extract_text_from_docx(file_path)
        elif doc_type == 'txt':
            return extract_text_from_txt(file_path)
    return ""

