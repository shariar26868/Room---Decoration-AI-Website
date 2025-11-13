"""
Upload API Endpoint
===================

Handles room image uploads (Step 1 of the workflow).
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from ai_backend.services.storage import upload_to_s3
from ai_backend.models import RoomImageUploadResponse, UserSession
from ai_backend.config import MAX_IMAGE_SIZE_MB
import uuid
import logging
from typing import Dict

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# In-memory session storage (use Redis in production)
user_sessions: Dict[str, UserSession] = {}


@router.post(
    "/upload",
    response_model=RoomImageUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Room Image",
    description="Upload a room image to start the design process. Returns a session ID for tracking progress."
)
async def upload_room_image(room_image: UploadFile = File(..., description="Room photo (JPEG/PNG, max 10MB)")):
    """
    Step 1: Upload room image
    
    Args:
        room_image: Image file (JPEG or PNG)
        
    Returns:
        - image_url: S3 URL of uploaded image
        - session_id: Unique ID for tracking user session
        
    Raises:
        HTTPException: If upload fails or file is invalid
    """
    
    try:
        # Validate file type
        if not room_image.content_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not determine file type"
            )
        
        if not room_image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type: {room_image.content_type}. Please upload JPEG or PNG image."
            )
        
        # Read image
        logger.info(f"Receiving image upload: {room_image.filename}")
        image_bytes = await room_image.read()
        
        # Check file size
        file_size_mb = len(image_bytes) / (1024 * 1024)
        if file_size_mb > MAX_IMAGE_SIZE_MB:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Image too large ({file_size_mb:.1f}MB). Maximum size is {MAX_IMAGE_SIZE_MB}MB."
            )
        
        logger.info(f"Image size: {file_size_mb:.2f}MB")
        
        # Save to temporary file
        import tempfile
        import os
        
        file_extension = os.path.splitext(room_image.filename)[1] or ".jpg"
        
        with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as temp:
            temp.write(image_bytes)
            temp_path = temp.name
        
        logger.info(f"Saved to temp file: {temp_path}")
        
        # Upload to S3
        try:
            s3_url = upload_to_s3(temp_path, folder="rooms")
            logger.info(f"✅ Uploaded to S3: {s3_url}")
        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload image to storage: {str(e)}"
            )
        finally:
            # Cleanup temp file
            try:
                os.remove(temp_path)
            except:
                pass
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create user session
        session = UserSession(
            session_id=session_id,
            room_image_url=s3_url
        )
        
        user_sessions[session_id] = session
        
        logger.info(f"🆔 Session created: {session_id}")
        logger.info(f"📊 Active sessions: {len(user_sessions)}")
        
        return RoomImageUploadResponse(
            success=True,
            image_url=s3_url,
            session_id=session_id,
            message="Room image uploaded successfully. You can now proceed to select room type."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during upload: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.delete(
    "/session/{session_id}",
    summary="Delete Session",
    description="Delete a user session and cleanup resources"
)
async def delete_session(session_id: str):
    """
    Delete a user session
    
    Args:
        session_id: Session ID to delete
        
    Returns:
        Success confirmation
    """
    
    if session_id not in user_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Remove from memory
    del user_sessions[session_id]
    
    logger.info(f"🗑️  Session deleted: {session_id}")
    
    return {
        "success": True,
        "message": "Session deleted successfully"
    }


@router.get(
    "/sessions/count",
    summary="Get Active Sessions Count",
    description="Get the number of currently active sessions"
)
async def get_sessions_count():
    """Get count of active sessions"""
    return {
        "active_sessions": len(user_sessions),
        "sessions": [
            {
                "session_id": sid,
                "created_at": session.created_at,
                "last_updated": session.last_updated,
                "has_image": session.room_image_url is not None,
                "room_type": session.room_type,
                "theme": session.theme
            }
            for sid, session in user_sessions.items()
        ]
    }