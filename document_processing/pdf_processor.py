import io
import shutil

import pymupdf
import pytesseract
from PIL import Image


# Tesseract executable location
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text_from_pdf(file):
    """
    Extract text from a PDF.

    Uses normal PDF text extraction first.
    If a page contains little or no text, OCR is used
    automatically for that page.

    Returns:
        List of dictionaries containing page number and text.
    """

    # Check whether Tesseract is available
    if not shutil.which("tesseract"):
        if not __import__("os").path.exists(TESSERACT_PATH):
            raise RuntimeError(
                "Tesseract OCR was not found.\n"
                "Please install Tesseract OCR or update "
                "TESSERACT_PATH in pdf_processor.py."
            )

        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

    # Read PDF
    pdf_bytes = file.read()

    document = pymupdf.open(stream=pdf_bytes, filetype="pdf")

    pages = []

    for page_number, page in enumerate(document, start=1):

        # -------------------------------------------------
        # 1. Try normal text extraction
        # -------------------------------------------------

        text = page.get_text("text").strip()

        # -------------------------------------------------
        # 2. If little/no text exists, use OCR
        # -------------------------------------------------

        if len(text) < 20:

            # Render page as an image
            pixmap = page.get_pixmap(
                matrix=pymupdf.Matrix(2, 2),
                alpha=False
            )

            # Convert PyMuPDF image to PIL image
            image = Image.open(
                io.BytesIO(pixmap.tobytes("png"))
            )

            # Run OCR
            text = pytesseract.image_to_string(
                image,
                lang="eng"
            ).strip()

        pages.append(
            {
                "page_number": page_number,
                "text": text
            }
        )

    document.close()

    return pages