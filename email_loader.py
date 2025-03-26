# email_loader.py

import email
from email import policy
from email.parser import BytesParser
from pathlib import Path
from docx import Document
from bs4 import BeautifulSoup
import pytesseract
from pdf2image import convert_from_path
import fitz  # PyMuPDF
import tempfile
import os

def extract_text_from_pdf(pdf_bytes):
    text = ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_bytes)
        tmp.flush()
        tmp_path = tmp.name

    try:
        with fitz.open(tmp_path) as doc:
            for page in doc:
                text += page.get_text()
    except Exception:
        images = convert_from_path(tmp_path)
        for img in images:
            text += pytesseract.image_to_string(img)

    os.remove(tmp_path)
    return text.strip()

def extract_text_from_docx(docx_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(docx_bytes)
        tmp.flush()
        tmp_path = tmp.name

    doc = Document(tmp_path)
    text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    os.remove(tmp_path)
    return text.strip()

def extract_text_from_image(image_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(image_bytes)
        tmp.flush()
        text = pytesseract.image_to_string(tmp.name)
    os.remove(tmp.name)
    return text.strip()

def parse_eml_file(eml_path):
    with open(eml_path, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)

    email_data = {
        "subject": msg["subject"],
        "from": msg["from"],
        "to": msg["to"],
        "date": msg["date"],
        "body": "",
        "attachments": []
    }

    for part in msg.walk():
        content_type = part.get_content_type()
        filename = part.get_filename()

        if content_type == "text/plain":
            email_data["body"] += part.get_content()
        elif content_type == "text/html" and not email_data["body"]:
            soup = BeautifulSoup(part.get_content(), "html.parser")
            email_data["body"] += soup.get_text()
        elif filename:
            ext = Path(filename).suffix.lower()
            content_bytes = part.get_payload(decode=True)

            if ext == ".pdf":
                extracted = extract_text_from_pdf(content_bytes)
            elif ext == ".docx":
                extracted = extract_text_from_docx(content_bytes)
            elif ext in [".jpg", ".jpeg", ".png"]:
                extracted = extract_text_from_image(content_bytes)
            else:
                extracted = "[UNSUPPORTED ATTACHMENT TYPE]"

            email_data["attachments"].append({
                "filename": filename,
                "content": extracted
            })

    return email_data

def parse_email_file(filepath):
    ext = Path(filepath).suffix.lower()
    if ext == ".eml":
        return parse_eml_file(filepath)
    elif ext == ".txt":
        with open(filepath, "r", encoding="utf-8") as f:
            return {
                "subject": Path(filepath).stem,
                "from": "unknown",
                "to": "unknown",
                "date": "unknown",
                "body": f.read(),
                "attachments": []
            }
    elif ext == ".docx":
        text = extract_text_from_docx(Path(filepath).read_bytes())
        return {
            "subject": Path(filepath).stem,
            "from": "unknown",
            "to": "unknown",
            "date": "unknown",
            "body": text,
            "attachments": []
        }
    elif ext == ".pdf":
        text = extract_text_from_pdf(Path(filepath).read_bytes())
        return {
            "subject": Path(filepath).stem,
            "from": "unknown",
            "to": "unknown",
            "date": "unknown",
            "body": text,
            "attachments": []
        }
    else:
        raise ValueError(f"Unsupported file type: {filepath}")