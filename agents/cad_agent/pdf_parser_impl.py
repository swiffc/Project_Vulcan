import pypdf
import logging
from typing import Dict, List, Any

logger = logging.getLogger("vulcan.cad.pdf_parser")


def extract_pdf_metadata(file_path: str) -> Dict[str, Any]:
    """Extract metadata and text from a PDF drawing."""
    try:
        reader = pypdf.PdfReader(file_path)
        meta = reader.metadata
        text_content = []

        for page in reader.pages:
            text_content.append(page.extract_text())

        full_text = "\n".join(text_content)

        return {
            "title": meta.title if meta else None,
            "author": meta.author if meta else None,
            "page_count": len(reader.pages),
            "raw_text": full_text,
        }
    except Exception as e:
        logger.error(f"Failed to parse PDF {file_path}: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    # Test stub
    print("PDF Parser Module Loaded")
