"""
API Routers Package
===================

RESTful API endpoints for the Room Designer application.

Modules:
    - upload: Room image upload (Step 1)
    - selection: Room/theme/furniture selection (Steps 2-5)
    - furniture: Furniture search and pricing (Steps 6-7)
    - generation: AI image generation (Steps 8-9)
"""

from . import upload, selection, furniture, generation

__all__ = ["upload", "selection", "furniture", "generation"]