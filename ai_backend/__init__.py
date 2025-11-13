"""
Room Designer AI Backend
========================

AI-powered interior design system with:
- Room image upload
- Furniture selection with dimensions
- Web scraping for furniture search
- AI image generation with Replicate
- AWS S3 storage

Author: Room Designer Team
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Room Designer Team"

# Import main components for easy access
from .config import THEMES, ROOM_TYPES
from .models import (
    UserSession,
    RoomImageUploadResponse,
    RoomTypeResponse,
    ThemeResponse,
    RoomDimensionResponse,
    FurnitureSelectionResponse,
    FurnitureSearchResponse,
    ImageGenerationResponse
)

__all__ = [
    "THEMES",
    "ROOM_TYPES",
    "UserSession",
    "RoomImageUploadResponse",
    "RoomTypeResponse",
    "ThemeResponse",
    "RoomDimensionResponse",
    "FurnitureSelectionResponse",
    "FurnitureSearchResponse",
    "ImageGenerationResponse"
]