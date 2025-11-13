"""
Storage Service
===============

Wrapper for file upload/download operations.
Handles both S3 and local storage for development.
"""

import os
import uuid
import logging
import shutil
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def upload_to_s3(file_path: str, folder: str = "generated") -> str:
    """
    Upload image to S3 and return public URL
    
    Args:
        file_path: Local file path to upload
        folder: S3 folder/prefix (e.g., "rooms", "generated")
    
    Returns:
        Public S3 URL
        
    Raises:
        Exception: If upload fails
    """
    try:
        from ai_backend.services.aws_service import get_aws_service
        
        # Validate file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Validate file size (max 50MB)
        file_size = os.path.getsize(file_path)
        max_size = 50 * 1024 * 1024  # 50MB
        
        if file_size > max_size:
            raise ValueError(
                f"File too large: {file_size / (1024*1024):.2f}MB "
                f"(max: {max_size / (1024*1024):.0f}MB)"
            )
        
        # Get file extension
        file_extension = os.path.splitext(file_path)[1].lower()
        
        # Default to .jpg if no extension
        if not file_extension:
            file_extension = ".jpg"
        
        # Validate extension
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        if file_extension not in allowed_extensions:
            logger.warning(f"⚠️  Unusual file extension: {file_extension}, using .jpg")
            file_extension = ".jpg"
        
        # Generate S3 key with timestamp for organization
        timestamp = datetime.now().strftime("%Y%m%d")
        unique_id = uuid.uuid4()
        file_name = f"{folder}/{timestamp}/{unique_id}{file_extension}"
        
        logger.info(f"📤 Uploading to S3: {file_name} (size: {file_size / 1024:.2f}KB)")
        
        # Get AWS service
        try:
            aws_service = get_aws_service()
        except RuntimeError as e:
            logger.error("❌ AWS service not initialized")
            raise Exception(
                "AWS service not configured. "
                "Check your .env file and ensure setup_aws.py has been run."
            )
        
        # Upload file
        url = aws_service.upload_file(
            file_path=file_path,
            object_name=file_name,
            make_public=True
        )
        
        if not url:
            raise Exception("Failed to get upload URL from AWS")
        
        logger.info(f"✅ File uploaded to S3: {url}")
        
        # Cleanup local file
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"🗑️  Local file deleted: {file_path}")
        except Exception as e:
            logger.warning(f"⚠️  Failed to delete local file: {e}")
        
        return url
        
    except FileNotFoundError as e:
        logger.error(f"❌ File not found: {e}")
        raise
    except ValueError as e:
        logger.error(f"❌ Validation error: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Upload failed: {e}", exc_info=True)
        raise Exception(f"Failed to upload to S3: {str(e)}")


def delete_from_s3(url: str) -> bool:
    """
    Delete file from S3 using its URL
    
    Args:
        url: Full S3 URL of the file
    
    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        from ai_backend.services.aws_service import get_aws_service
        
        # Extract object name from URL
        # URL format: https://bucket.s3.region.amazonaws.com/folder/file.jpg
        if ".amazonaws.com/" in url:
            object_name = url.split(".amazonaws.com/")[-1]
        else:
            logger.error(f"❌ Invalid S3 URL format: {url}")
            return False
        
        logger.info(f"🗑️  Deleting from S3: {object_name}")
        
        # Get AWS service
        aws_service = get_aws_service()
        
        # Delete file
        result = aws_service.delete_file(object_name)
        
        if result:
            logger.info(f"✅ File deleted from S3: {object_name}")
        else:
            logger.warning(f"⚠️  Delete failed for: {object_name}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ S3 delete failed: {e}")
        return False


def save_to_local(file_path: str, folder: str = "uploads") -> str:
    """
    Save file locally (for development/testing without AWS)
    
    Args:
        file_path: Source file path
        folder: Destination folder
    
    Returns:
        Local file path
    """
    try:
        # Create folder if not exists
        os.makedirs(folder, exist_ok=True)
        
        # Generate unique filename
        file_extension = os.path.splitext(file_path)[1] or ".jpg"
        new_filename = f"{uuid.uuid4()}{file_extension}"
        new_path = os.path.join(folder, new_filename)
        
        # Copy file
        shutil.copy(file_path, new_path)
        
        logger.info(f"✅ File saved locally: {new_path}")
        return new_path
        
    except Exception as e:
        logger.error(f"❌ Local save failed: {e}")
        raise


# ===================================================================
# Configuration: Use local storage for development
# ===================================================================
USE_LOCAL_STORAGE = os.getenv("USE_LOCAL_STORAGE", "false").lower() == "true"


def upload_image(file_path: str, folder: str = "generated") -> str:
    """
    Upload image - uses S3 or local storage based on config
    
    Args:
        file_path: Local file path
        folder: Destination folder
    
    Returns:
        URL (S3) or local path
    """
    if USE_LOCAL_STORAGE:
        logger.info("📁 Using local storage (development mode)")
        return save_to_local(file_path, folder)
    else:
        return upload_to_s3(file_path, folder)