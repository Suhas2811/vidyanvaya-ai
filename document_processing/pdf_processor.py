import io
import os
import shutil

import pymupdf
import pytesseract
from PIL import Image


# Local Windows Tesseract executable location
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def _configure_tesseract():
    """
    Configure Tesseract only when OCR is actually required.

    This allows normal text-based PDFs to work on platforms
    where Tesseract is not installed, such as Streamlit Cloud.
    """

    # Check if tesseract is already available in PATH
    tesseract_executable = shutil.which("tesseract")

    if tesseract_executable:
        pytesseract.pytesseract.tesseract_cmd = tesseract_executable
        return True

    # Check the local Windows installation path
    if os.path.exists(TESSERACT_PATH):
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
        return True

    return False


def extract_text_from_pdf(file):
    """
    Extract text from a PDF.

    Normal text-based PDF pages are processed using PyMuPDF.

    OCR is used only when a page contains little or no
    extractable text.

    Returns:
        List of dictionaries containing page number and text.
    """

    # ---------------------------------------------------------
    # 1. Read PDF
    # ---------------------------------------------------------

    pdf_bytes = file.read()

    document = pymupdf.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    pages = []

    # ---------------------------------------------------------
    # 2. Process each page
    # ---------------------------------------------------------

    for page_number, page in enumerate(document, start=1):

        # -----------------------------------------------------
        # Try normal PDF text extraction first
        # -----------------------------------------------------

        text = page.get_text("text").strip()

        # -----------------------------------------------------
        # OCR only if normal text extraction is insufficient
        # -----------------------------------------------------

        if len(text) < 20:

            # Configure Tesseract only now
            # This is the important fix for Streamlit Cloud.
            if not _configure_tesseract():
                document.close()

                raise RuntimeError(
                    "This PDF appears to contain scanned/image-based "
                    "pages that require OCR, but Tesseract OCR is not "
                    "available in the current environment."
                )

            # Render the PDF page as an image
            pixmap = page.get_pixmap(
                matrix=pymupdf.Matrix(2, 2),
                alpha=False
            )

            # Convert PyMuPDF image to PIL image
            image = Image.open(
                io.BytesIO(
                    pixmap.tobytes("png")
                )
            )

            # Run OCR
            text = pytesseract.image_to_string(
                image,
                lang="eng"
            ).strip()

        # -----------------------------------------------------
        # Store page result
        # -----------------------------------------------------

        pages.append(
            {
                "page_number": page_number,
                "text": text
            }
        )

    # ---------------------------------------------------------
    # 3. Close document
    # ---------------------------------------------------------

    document.close()

    return pages