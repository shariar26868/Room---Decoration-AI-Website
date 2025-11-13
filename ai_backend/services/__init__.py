"""
Services Package
================

Business logic and external API integrations.

Modules:
    - dimension: Room and furniture dimension calculations
    - furniture: Web scraping and furniture search
    - ai_generator: AI image generation with Replicate
    - aws_service: AWS S3 storage management
    - storage: File upload/download wrapper
"""

from . import dimension, furniture, ai_generator, aws_service, storage

__all__ = ["dimension", "furniture", "ai_generator", "aws_service", "storage"]