"""
utils.py - PDF text extraction and utility functions
"""

import re
import PyPDF2
import io


def extract_text_from_pdf(uploaded_file) -> str:
    """
    Extract text from an uploaded PDF file.
    Returns extracted text or empty string on failure.
    """
    try:
        pdf_bytes = uploaded_file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))

        if len(pdf_reader.pages) == 0:
            return ""

        text_parts = []
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        full_text = "\n".join(text_parts).strip()
        return full_text

    except Exception as e:
        return ""


def clean_text(text: str) -> str:
    """
    Clean and normalize extracted text for processing.
    """
    if not text:
        return ""

    # Replace multiple whitespace/newlines with single space
    text = re.sub(r'\s+', ' ', text)

    # Remove special characters but keep alphanumeric, spaces, dots, commas, slashes, plus
    text = re.sub(r'[^\w\s.,/+#@\-()]', ' ', text)

    # Collapse multiple spaces again after special char removal
    text = re.sub(r' +', ' ', text)

    return text.strip()


def truncate_text(text: str, max_chars: int = 1500) -> str:
    """
    Truncate text to max_chars for API calls to avoid token limits.
    """
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."


def count_words(text: str) -> int:
    """Return word count of text."""
    return len(text.split()) if text else 0


def get_text_preview(text: str, max_chars: int = 500) -> str:
    """Return a preview of the text."""
    if not text:
        return ""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."
