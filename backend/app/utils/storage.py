"""File storage utility — Cloudinary or S3."""
import io
import uuid
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class StorageService:
    """Unified storage service supporting Cloudinary and S3."""

    def __init__(self):
        from app.config import settings
        self.settings = settings
        self._init_cloudinary()

    def _init_cloudinary(self):
        if self.settings.cloudinary_cloud_name:
            try:
                import cloudinary
                cloudinary.config(
                    cloud_name=self.settings.cloudinary_cloud_name,
                    api_key=self.settings.cloudinary_api_key,
                    api_secret=self.settings.cloudinary_api_secret,
                )
                self._provider = "cloudinary"
            except ImportError:
                self._provider = "local"
        else:
            self._provider = "local"

    def upload_image(
        self,
        file_bytes: bytes,
        folder: str = "upsc-study-os",
        filename: Optional[str] = None,
    ) -> Tuple[str, str]:
        """Upload image and return (url, public_id)."""
        if self._provider == "cloudinary":
            return self._upload_cloudinary(file_bytes, folder, filename)
        return self._upload_local(file_bytes, filename)

    def _upload_cloudinary(
        self, file_bytes: bytes, folder: str, filename: Optional[str]
    ) -> Tuple[str, str]:
        import cloudinary.uploader
        public_id = f"{folder}/{filename or uuid.uuid4().hex}"
        result = cloudinary.uploader.upload(
            file_bytes,
            public_id=public_id,
            resource_type="auto",
        )
        return result["secure_url"], result["public_id"]

    def _upload_local(self, file_bytes: bytes, filename: Optional[str]) -> Tuple[str, str]:
        """Fallback: save to local /tmp (dev only)."""
        import os
        name = filename or f"{uuid.uuid4().hex}.jpg"
        path = f"/tmp/{name}"
        with open(path, "wb") as f:
            f.write(file_bytes)
        return f"/static/{name}", name

    def delete_file(self, public_id: str) -> bool:
        if self._provider == "cloudinary":
            try:
                import cloudinary.uploader
                cloudinary.uploader.destroy(public_id)
                return True
            except Exception as e:
                logger.error(f"Cloudinary delete error: {e}")
                return False
        return True


# Singleton
_storage: Optional[StorageService] = None


def get_storage() -> StorageService:
    global _storage
    if _storage is None:
        _storage = StorageService()
    return _storage
