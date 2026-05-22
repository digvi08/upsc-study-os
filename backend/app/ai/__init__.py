from .mentor_service import MentorService

__all__ = ["MentorService"]

try:
    from .ocr_service import OCRService
    __all__.append("OCRService")
except ImportError:
    pass
