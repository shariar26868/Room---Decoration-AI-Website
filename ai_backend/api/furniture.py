"""
Furniture Search API Endpoints
===============================

Handles price range and furniture search (Steps 6-7).
"""

from fastapi import APIRouter, HTTPException, status
from ai_backend.models import (
    PriceRangeRequest,
    FurnitureSearchRequest,
    FurnitureSearchResponse,
    FurnitureItem
)
from ai_backend.services.furniture import search_furniture_on_websites
from ai_backend.config import THEMES
import logging

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
            detail="Session not found. Please start from step 1."
        )
    
    session = user_sessions[session_id]
    session.update_timestamp()
    return session


# ===================================================================
# STEP 6: Set Price Range
# ===================================================================
@router.post(
    "/price-range",
    summary="Set Price Range",
    description="Step 6: Set price range for furniture search (USD)"
)
async def set_price_range(request: PriceRangeRequest):
    """
    Step 6: Set price range for furniture search
    
    Args:
        request: Price range request (min and max in USD)
        
    Returns:
        Confirmation of price range
        
    Raises:
        HTTPException: If session not found or price range invalid
    """
    
    # Get session
    session = get_session(request.session_id)
    
    # Validate prerequisites
    if not session.furniture_selections:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please select furniture first (Step 5)"
        )
    
    # Update session
    session.min_price = request.min_price
    session.max_price = request.max_price
    
    logger.info(
        f"💰 Price range set: ${request.min_price:.2f} - ${request.max_price:.2f} "
        f"(Session: {request.session_id[:8]}...)"
    )
    
    return {
        "success": True,
        "min_price": request.min_price,
        "max_price": request.max_price,
        "currency": "USD",
        "message": f"Price range set: ${request.min_price:.2f} - ${request.max_price:.2f}. Ready to search furniture."
    }


# ===================================================================
# STEP 7: Search Furniture on Websites
# ===================================================================
@router.post(
    "/search",
    response_model=FurnitureSearchResponse,
    summary="Search Furniture",
    description="Step 7: Search for furniture on theme websites"
)
async def search_furniture(request: FurnitureSearchRequest):
    """
    Step 7: Search furniture on theme websites
    
    - Uses session data (room_type, theme, furniture selections)
    - Searches websites based on theme
    - Returns furniture with links, images, and prices
    
    Args:
        request: Search request (only requires session_id)
        
    Returns:
        List of furniture items matching criteria
        
    Raises:
        HTTPException: If prerequisites not met or search fails
    """
    
    # Get session
    session = get_session(request.session_id)
    
    # Validate all prerequisites
    if not session.room_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please select room type first (Step 2)"
        )
    
    if not session.theme:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please select theme first (Step 3)"
        )
    
    if not session.furniture_selections:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please select furniture first (Step 5)"
        )
    
    if session.min_price is None or session.max_price is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please set price range first (Step 6)"
        )
    
    # Get furniture types to search
    furniture_types = list(set([item["type"] for item in session.furniture_selections]))
    
    logger.info(f"🔍 Starting furniture search...")
    logger.info(f"   Room Type: {session.room_type}")
    logger.info(f"   Theme: {session.theme}")
    logger.info(f"   Furniture Types: {furniture_types}")
    logger.info(f"   Price Range: ${session.min_price:.2f} - ${session.max_price:.2f}")
    
    # Get websites for theme
    websites = THEMES.get(session.theme, [])
    
    # Search websites
    try:
        results = search_furniture_on_websites(
            theme=session.theme,
            room_type=session.room_type,
            furniture_types=furniture_types,
            min_price=session.min_price,
            max_price=session.max_price
        )
        
        # Store results in session
        session.search_results = results
        
        logger.info(f"✅ Found {len(results)} furniture items from {len(websites)} websites")
        
        return FurnitureSearchResponse(
            success=True,
            results=results,
            count=len(results),
            searched_websites=len(websites),
            message=f"Found {len(results)} furniture items matching your criteria. "
                    f"Select items to include in your design."
        )
        
    except Exception as e:
        logger.error(f"❌ Furniture search failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Furniture search failed: {str(e)}"
        )


# ===================================================================
# GET SESSION DATA (for debugging/frontend)
# ===================================================================
@router.get(
    "/session/{session_id}",
    summary="Get Session Data",
    description="Get current session progress and data"
)
async def get_session_data(session_id: str):
    """
    Get current session data
    
    Useful for frontend to display progress and current selections.
    
    Args:
        session_id: Session ID
        
    Returns:
        Complete session data
    """
    
    session = get_session(session_id)
    
    # Calculate progress
    steps_completed = 0
    if session.room_image_url:
        steps_completed += 1
    if session.room_type:
        steps_completed += 1
    if session.theme:
        steps_completed += 1
    if session.square_feet:
        steps_completed += 1
    if session.furniture_selections:
        steps_completed += 1
    if session.min_price is not None:
        steps_completed += 1
    if session.search_results:
        steps_completed += 1
    
    progress_percentage = (steps_completed / 7) * 100
    
    return {
        "success": True,
        "session_id": session_id,
        "created_at": session.created_at,
        "last_updated": session.last_updated,
        "progress": {
            "steps_completed": steps_completed,
            "total_steps": 7,
            "percentage": round(progress_percentage, 1)
        },
        "data": {
            "room_image_url": session.room_image_url,
            "room_type": session.room_type,
            "theme": session.theme,
            "dimensions": {
                "length": session.length,
                "width": session.width,
                "height": session.height,
                "square_feet": session.square_feet,
                "cubic_feet": session.cubic_feet
            } if session.length else None,
            "furniture": {
                "selections": session.furniture_selections,
                "total_items": len(session.furniture_selections),
                "total_sqft": session.furniture_total_sqft,
                "room_usage_percentage": round(
                    (session.furniture_total_sqft / session.square_feet * 100), 2
                ) if session.square_feet else 0
            },
            "price_range": {
                "min": session.min_price,
                "max": session.max_price,
                "currency": "USD"
            } if session.min_price is not None else None,
            "search_results": {
                "count": len(session.search_results),
                "items": session.search_results
            } if session.search_results else None,
            "generated_images": session.generated_images
        }
    }


# ===================================================================
# CLEAR SEARCH RESULTS
# ===================================================================
@router.delete(
    "/search/{session_id}",
    summary="Clear Search Results",
    description="Clear search results to start a new search"
)
async def clear_search_results(session_id: str):
    """
    Clear search results from session
    
    Args:
        session_id: Session ID
        
    Returns:
        Success confirmation
    """
    
    session = get_session(session_id)
    
    session.search_results = []
    
    logger.info(f"🗑️  Search results cleared (Session: {session_id[:8]}...)")
    
    return {
        "success": True,
        "message": "Search results cleared. You can now search again with different criteria."
    }