"""PDF text extraction utilities."""
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def extract_text_pymupdf(pdf_path: Path) -> Optional[str]:
    """Extract text using PyMuPDF (fitz)."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        return "\n".join(text_parts)
    except ImportError:
        logger.warning("PyMuPDF not available")
        return None
    except Exception as e:
        logger.error(f"PyMuPDF extraction failed: {e}")
        return None


def extract_text_pdfminer(pdf_path: Path) -> Optional[str]:
    """Extract text using pdfminer."""
    try:
        from pdfminer.high_level import extract_text
        return extract_text(pdf_path)
    except ImportError:
        logger.warning("pdfminer not available")
        return None
    except Exception as e:
        logger.error(f"pdfminer extraction failed: {e}")
        return None


def extract_text_ocr(pdf_path: Path) -> Optional[str]:
    """Extract text using OCR (pytesseract + pdf2image)."""
    try:
        from pdf2image import convert_from_path
        import pytesseract
        
        images = convert_from_path(pdf_path)
        text_parts = []
        for image in images:
            text = pytesseract.image_to_string(image)
            text_parts.append(text)
        return "\n".join(text_parts)
    except ImportError:
        logger.warning("OCR libraries not available")
        return None
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        return None


def extract_pdf_text(pdf_path: Path) -> str:
    """
    Extract text from PDF using fallback chain:
    PyMuPDF -> pdfminer -> OCR
    """
    logger.info(f"Extracting text from {pdf_path}")
    
    # Try PyMuPDF first
    text = extract_text_pymupdf(pdf_path)
    if text and text.strip():
        logger.info("Successfully extracted text using PyMuPDF")
        return text.strip()
    
    # Try pdfminer
    text = extract_text_pdfminer(pdf_path)
    if text and text.strip():
        logger.info("Successfully extracted text using pdfminer")
        return text.strip()
    
    # Try OCR as last resort
    text = extract_text_ocr(pdf_path)
    if text and text.strip():
        logger.info("Successfully extracted text using OCR")
        return text.strip()
    
    # If all methods fail
    error_msg = "All PDF extraction methods failed"
    logger.error(error_msg)
    raise Exception(error_msg)

