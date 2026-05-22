"""OCR service using Tesseract (optional dependency)."""
import io
import base64
import logging
from typing import Optional

logger = logging.getLogger(__name__)

_tesseract_available: Optional[bool] = None


def _check_tesseract() -> bool:
    global _tesseract_available
    if _tesseract_available is not None:
        return _tesseract_available
    try:
        import pytesseract  # noqa: F401
        from PIL import Image  # noqa: F401
        _tesseract_available = True
    except ImportError:
        _tesseract_available = False
        logger.warning("pytesseract/Pillow not installed — OCR features disabled")
    return _tesseract_available


class OCRService:
    def extract_text_from_image(self, image_bytes: bytes) -> str:
        """Extract text from image bytes using Tesseract OCR."""
        if not _check_tesseract():
            raise RuntimeError(
                "OCR is not available. Install pytesseract, Pillow, and Tesseract OCR."
            )
        import pytesseract
        from PIL import Image

        try:
            image = Image.open(io.BytesIO(image_bytes))
            # Preprocess: convert to grayscale for better accuracy
            image = image.convert("L")
            text = pytesseract.image_to_string(image, lang="eng")
            return text.strip()
        except Exception as e:
            logger.error(f"OCR extraction error: {e}")
            raise

    def extract_text_from_base64(self, base64_string: str) -> str:
        """Extract text from base64-encoded image."""
        if not _check_tesseract():
            raise RuntimeError("OCR is not available.")
        try:
            # Remove data URL prefix if present
            if "," in base64_string:
                base64_string = base64_string.split(",")[1]
            image_bytes = base64.b64decode(base64_string)
            return self.extract_text_from_image(image_bytes)
        except Exception as e:
            logger.error(f"OCR base64 extraction error: {e}")
            raise

    def get_confidence_score(self, image_bytes: bytes) -> float:
        """Get OCR confidence score for an image."""
        if not _check_tesseract():
            return 0.0
        import pytesseract
        from PIL import Image

        try:
            image = Image.open(io.BytesIO(image_bytes))
            image = image.convert("L")
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            confidences = [int(c) for c in data["conf"] if c != "-1"]
            return sum(confidences) / len(confidences) if confidences else 0.0
        except Exception as e:
            logger.error(f"OCR confidence error: {e}")
            return 0.0
