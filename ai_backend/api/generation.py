"""
Image Generation API Endpoint
==============================

Handles AI image generation (Steps 8-9).
"""

from fastapi import APIRouter, HTTPException, status
from ai_backend.models import ImageGenerationRequest, ImageGenerationResponse
from ai_backend.services.ai_generator import generate_room_with_furniture
from ai_backend.services.storage import upload_to_s3
import logging
import requests
import time

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# Import session storage
from ai_backend.api.upload import user_sessions


def get_session(session_id: str):
    """Get session or raise 404 error"""
    if session_id not in user_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    session = user_sessions[session_id]
    session.update_timestamp()
    return session


# ===================================================================
# STEP 8-9: Generate Final Image
# ===================================================================
@router.post(
    "/generate",
    response_model=ImageGenerationResponse,
    summary="Generate Design Image",
    description="Steps 8-9: Generate final room image with furniture placed using AI"
)
async def generate_final_image(request: ImageGenerationRequest):
    """
    Steps 8-9: Generate final room image with furniture placed
    
    Uses Replicate's Interior Design model to place furniture in the room
    according to the user's prompt.
    
    Args:
        request: Generation request with prompt and furniture links
        
    Returns:
        - generated_image_url: Final S3 URL of generated image
        - original_image_url: Original room image
        - furniture_items: List of furniture with purchase links
        
    Raises:
        HTTPException: If prerequisites not met or generation fails
    """
    
    start_time = time.time()
    
    # Get session
    session = get_session(request.session_id)
    
    # Validate prerequisites
    if not session.room_image_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No room image found. Please upload image first (Step 1)"
        )
    
    if not session.theme:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please select theme first (Step 3)"
        )
    
    if not session.search_results:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No search results found. Please search for furniture first (Step 7)"
        )
    
    if not request.furniture_links:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide at least one furniture link"
        )
    
    # Validate furniture links are from search results
    search_links = [item.link for item in session.search_results]
    invalid_links = [link for link in request.furniture_links if link not in search_links]
    
    if invalid_links:
        logger.warning(f"⚠️  Some links not from search results: {len(invalid_links)} links")
    
    logger.info(f"🎨 Starting image generation...")
    logger.info(f"   Session: {request.session_id[:8]}...")
    logger.info(f"   Theme: {session.theme}")
    logger.info(f"   Prompt: {request.prompt[:100]}...")
    logger.info(f"   Furniture items: {len(request.furniture_links)}")
    
    try:
        # Download original room image
        logger.info("📥 Downloading original room image from S3...")
        try:
            response = requests.get(session.room_image_url, timeout=30)
            response.raise_for_status()
            room_image_bytes = response.content
            
            if len(room_image_bytes) == 0:
                raise ValueError("Downloaded image is empty")
            
            logger.info(f"✅ Downloaded image ({len(room_image_bytes) / 1024:.1f} KB)")
        
        except requests.RequestException as e:
            logger.error(f"❌ Failed to download room image: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to download room image from S3: {str(e)}"
            )
        
        # Get selected furniture items
        selected_furniture = [
            item for item in session.search_results
            if item.link in request.furniture_links
        ]
        
        if not selected_furniture:
            logger.warning("⚠️  No matching furniture found in search results, using all results")
            selected_furniture = session.search_results[:5]
        
        logger.info(f"✅ Selected {len(selected_furniture)} furniture items for generation")
        
        # Generate image using Replicate
        logger.info("🤖 Generating image with AI (this may take 30-60 seconds)...")
        logger.info("   Using Replicate model: adirik/interior-design")
        
        try:
            generated_image_path = generate_room_with_furniture(
                room_image_bytes=room_image_bytes,
                prompt=request.prompt,
                theme=session.theme,
                furniture_items=selected_furniture
            )
            
            logger.info(f"✅ Image generated successfully: {generated_image_path}")
        
        except Exception as e:
            logger.error(f"❌ AI generation failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI image generation failed: {str(e)}"
            )
        
        # Upload to S3
        logger.info("☁️  Uploading generated image to S3...")
        try:
            generated_url = upload_to_s3(generated_image_path, folder="generated")
            logger.info(f"✅ Generated image uploaded: {generated_url}")
        
        except Exception as e:
            logger.error(f"❌ S3 upload failed: {e}", exc_info=True)
            # Cleanup temp file
            import os
            try:
                os.remove(generated_image_path)
            except:
                pass
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload generated image to S3: {str(e)}"
            )
        
        # Store in session
        session.generated_images.append(generated_url)
        
        # Calculate generation time
        generation_time = time.time() - start_time
        
        logger.info(f"🎉 Image generation complete! ({generation_time:.1f}s)")
        logger.info(f"   Generated URL: {generated_url}")
        
        return ImageGenerationResponse(
            success=True,
            generated_image_url=generated_url,
            original_image_url=session.room_image_url,
            furniture_items=selected_furniture,
            prompt_used=request.prompt,
            generation_time_seconds=round(generation_time, 2),
            message="Image generated successfully! You can regenerate with different prompts or furniture."
        )
        
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"❌ Unexpected error during generation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image generation failed: {str(e)}"
        )


# ===================================================================
# REGENERATE: Regenerate with new prompt (same furniture)
# ===================================================================
@router.post(
    "/regenerate",
    response_model=ImageGenerationResponse,
    summary="Regenerate Image",
    description="Regenerate image with new prompt using same furniture"
)
async def regenerate_image(session_id: str, new_prompt: str):
    """
    Regenerate image with new prompt
    
    Uses the same furniture from previous search but with different
    placement instructions.
    
    Args:
        session_id: Session ID
        new_prompt: New placement instructions
        
    Returns:
        New generated image
    """
    
    # Get session
    session = get_session(session_id)
    
    if not session.search_results:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No previous search results found. Please search for furniture first."
        )
    
    # Use all selected furniture from search results
    furniture_links = [item.link for item in session.search_results]
    
    # Call generate with new prompt
    request = ImageGenerationRequest(
        session_id=session_id,
        prompt=new_prompt,
        furniture_links=furniture_links
    )
    
    logger.info(f"🔄 Regenerating image with new prompt: {new_prompt[:50]}...")
    
    return await generate_final_image(request)