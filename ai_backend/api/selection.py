# # """
# # Selection API Endpoints
# # =======================

# # Progressive workflow with session-based data carry-forward.
# # """

# # from fastapi import APIRouter, HTTPException, status
# # from ai_backend.models import (
# #     RoomTypeRequest, RoomTypeResponse,
# #     ThemeRequest, ThemeResponse,
# #     RoomDimensionRequest, RoomDimensionResponse,
# #     FurnitureSelectionRequest, FurnitureSelectionResponse,
# #     FurnitureFitCheckResponse
# # )
# # from ai_backend.config import THEMES, ROOM_TYPES, MAX_FURNITURE_PERCENTAGE
# # import json
# # import logging
# # from pathlib import Path
# # from typing import Dict, Any

# # # Configure logging
# # logger = logging.getLogger(__name__)

# # # Initialize router
# # router = APIRouter()

# # # Load furniture data
# # FURNITURE_DATA_PATH = Path(__file__).parent.parent / "data" / "furniture_data.json"

# # try:
# #     with open(FURNITURE_DATA_PATH, "r", encoding='utf-8') as f:
# #         FURNITURE_DATA = json.load(f)
# #     logger.info(f"Loaded furniture data from {FURNITURE_DATA_PATH}")
# # except Exception as e:
# #     logger.error(f"Failed to load furniture data: {e}")
# #     FURNITURE_DATA = {}

# # # Import session storage
# # from ai_backend.api.upload import user_sessions


# # def get_session(session_id: str):
# #     """Get session or raise 404 error"""
# #     if session_id not in user_sessions:
# #         raise HTTPException(
# #             status_code=status.HTTP_404_NOT_FOUND,
# #             detail="Session not found. Please upload room image first."
# #         )
    
# #     session = user_sessions[session_id]
# #     session.update_timestamp()
# #     return session


# # # ===================================================================
# # # DROPDOWN ENDPOINTS (Options Only - No Session Required for Basic Lists)
# # # ===================================================================

# # @router.get(
# #     "/options/room-types",
# #     summary="Get Room Type Dropdown",
# #     description="Get all available room types for dropdown (no session needed)"
# # )
# # async def get_room_type_options() -> Dict[str, Any]:
# #     """Get room type dropdown options"""
    
# #     options = [
# #         {
# #             "value": rt,
# #             "label": rt,
# #             "furniture_count": len(FURNITURE_DATA.get(rt, {}))
# #         }
# #         for rt in ROOM_TYPES
# #     ]
    
# #     return {
# #         "success": True,
# #         "options": options,
# #         "count": len(options)
# #     }


# # @router.get(
# #     "/options/themes",
# #     summary="Get Theme Dropdown",
# #     description="Get all available themes for dropdown (no session needed)"
# # )
# # async def get_theme_options() -> Dict[str, Any]:
# #     """Get theme dropdown options"""
    
# #     options = [
# #         {
# #             "value": theme,
# #             "label": theme.replace('_', ' ').title(),
# #             "website_count": len(websites),
# #             "preview_websites": websites[:3]
# #         }
# #         for theme, websites in THEMES.items()
# #     ]
    
# #     return {
# #         "success": True,
# #         "options": options,
# #         "count": len(options)
# #     }


# # @router.get(
# #     "/options/furniture-types/{session_id}",
# #     summary="Get Furniture Type Dropdown",
# #     description="Get furniture types based on selected room type (session-dependent)"
# # )
# # async def get_furniture_type_options(session_id: str) -> Dict[str, Any]:
# #     """Get furniture type options based on room type in session"""
    
# #     session = get_session(session_id)
    
# #     if not session.room_type:
# #         raise HTTPException(
# #             status_code=status.HTTP_400_BAD_REQUEST,
# #             detail="Please select room type first (Step 2)"
# #         )
    
# #     room_furniture = FURNITURE_DATA.get(session.room_type, {})
    
# #     options = [
# #         {
# #             "value": furn_type,
# #             "label": furn_type,
# #             "subtype_count": len(subtypes),
# #             "example_subtypes": list(subtypes.keys())[:3]
# #         }
# #         for furn_type, subtypes in room_furniture.items()
# #     ]
    
# #     return {
# #         "success": True,
# #         "room_type": session.room_type,
# #         "options": options,
# #         "count": len(options),
# #         "message": f"Furniture types available for {session.room_type}"
# #     }


# # @router.get(
# #     "/options/furniture-subtypes/{session_id}/{furniture_type}",
# #     summary="Get Furniture Subtype Dropdown",
# #     description="Get subtypes for selected furniture type (session-dependent)"
# # )
# # async def get_furniture_subtype_options(session_id: str, furniture_type: str) -> Dict[str, Any]:
# #     """Get furniture subtype options"""
    
# #     session = get_session(session_id)
    
# #     if not session.room_type:
# #         raise HTTPException(
# #             status_code=status.HTTP_400_BAD_REQUEST,
# #             detail="Please select room type first"
# #         )
    
# #     room_furniture = FURNITURE_DATA.get(session.room_type, {})
# #     subtypes_data = room_furniture.get(furniture_type, {})
    
# #     if not subtypes_data:
# #         raise HTTPException(
# #             status_code=status.HTTP_404_NOT_FOUND,
# #             detail=f"No subtypes found for '{furniture_type}' in {session.room_type}"
# #         )
    
# #     options = []
# #     for subtype, dims in subtypes_data.items():
# #         sqft = round((dims["width"] * dims["depth"]) / 144.0, 2)
# #         options.append({
# #             "value": subtype,
# #             "label": subtype,
# #             "dimensions": {
# #                 "width": dims["width"],
# #                 "depth": dims["depth"],
# #                 "height": dims["height"],
# #                 "sqft": sqft
# #             },
# #             "description": f'{dims["width"]}" W x {dims["depth"]}" D x {dims["height"]}" H ({sqft} sq ft)'
# #         })
    
# #     return {
# #         "success": True,
# #         "furniture_type": furniture_type,
# #         "room_type": session.room_type,
# #         "options": options,
# #         "count": len(options)
# #     }


# # # ===================================================================
# # # STEP 2: Select Room Type (Saves to Session)
# # # ===================================================================
# # @router.post(
# #     "/room-type",
# #     response_model=RoomTypeResponse,
# #     summary="Step 2: Select Room Type",
# #     description="Select room type from dropdown - saves to session for next steps"
# # )
# # async def select_room_type(request: RoomTypeRequest):
# #     """
# #     Select room type and save to session.
# #     This data will be automatically available in next steps.
# #     """
    
# #     session = get_session(request.session_id)
    
# #     if request.room_type not in ROOM_TYPES:
# #         raise HTTPException(
# #             status_code=status.HTTP_400_BAD_REQUEST,
# #             detail=f"Invalid room type. Valid options: {', '.join(ROOM_TYPES)}"
# #         )
    
# #     # Save to session
# #     session.room_type = request.room_type
    
# #     available_furniture = list(FURNITURE_DATA.get(request.room_type, {}).keys())
    
# #     logger.info(f"✓ Room type saved to session: {request.room_type}")
    
# #     return RoomTypeResponse(
# #         success=True,
# #         room_type=request.room_type,
# #         available_furniture=available_furniture,
# #         message=f"Room type '{request.room_type}' saved to session. "
# #                 f"{len(available_furniture)} furniture types available. "
# #                 f"You can now select theme."
# #     )


# # # ===================================================================
# # # STEP 3: Select Theme (Uses Room Type from Session)
# # # ===================================================================
# # @router.post(
# #     "/theme",
# #     response_model=ThemeResponse,
# #     summary="Step 3: Select Theme",
# #     description="Select theme from dropdown - automatically uses room type from session"
# # )
# # async def select_theme(request: ThemeRequest):
# #     """
# #     Select theme and save to session.
# #     Room type from Step 2 is already in session.
# #     """
    
# #     session = get_session(request.session_id)
    
# #     # Check if room type was selected
# #     if not session.room_type:
# #         raise HTTPException(
# #             status_code=status.HTTP_400_BAD_REQUEST,
# #             detail="Please select room type first (Step 2)"
# #         )
    
# #     theme_upper = request.theme.upper()
    
# #     if theme_upper not in THEMES:
# #         raise HTTPException(
# #             status_code=status.HTTP_400_BAD_REQUEST,
# #             detail=f"Invalid theme. Valid options: {', '.join(THEMES.keys())}"
# #         )
    
# #     # Save to session
# #     session.theme = theme_upper
    
# #     websites = THEMES[theme_upper]
    
# #     logger.info(f"✓ Theme saved to session: {theme_upper}")
# #     logger.info(f"  Room type from session: {session.room_type}")
    
# #     return ThemeResponse(
# #         success=True,
# #         theme=theme_upper,
# #         websites=websites,
# #         website_count=len(websites),
# #         message=f"Theme '{theme_upper}' saved to session. "
# #                 f"Room type '{session.room_type}' is already set. "
# #                 f"You can now enter room dimensions."
# #     )


# # # ===================================================================
# # # STEP 4: Enter Room Dimensions (Uses Room Type + Theme from Session)
# # # ===================================================================
# # @router.post(
# #     "/dimensions",
# #     response_model=RoomDimensionResponse,
# #     summary="Step 4: Set Room Dimensions",
# #     description="Enter room dimensions - automatically uses room type and theme from session"
# # )
# # async def set_room_dimensions(request: RoomDimensionRequest):
# #     """
# #     Set room dimensions and save to session.
# #     Room type and theme from previous steps are already in session.
# #     """
    
# #     session = get_session(request.session_id)
    
# #     # Check prerequisites
# #     if not session.room_type:
# #         raise HTTPException(
# #             status_code=status.HTTP_400_BAD_REQUEST,
# #             detail="Please select room type first (Step 2)"
# #         )
    
# #     if not session.theme:
# #         raise HTTPException(
# #             status_code=status.HTTP_400_BAD_REQUEST,
# #             detail="Please select theme first (Step 3)"
# #         )
    
# #     # Calculate areas
# #     square_feet = request.length * request.width
# #     cubic_feet = request.length * request.width * request.height
    
# #     # Save to session
# #     session.length = request.length
# #     session.width = request.width
# #     session.height = request.height
# #     session.square_feet = square_feet
# #     session.cubic_feet = cubic_feet
    
# #     logger.info(f"✓ Dimensions saved to session: {request.length}' x {request.width}' x {request.height}'")
# #     logger.info(f"  Room type: {session.room_type}, Theme: {session.theme}")
    
# #     return RoomDimensionResponse(
# #         success=True,
# #         length=request.length,
# #         width=request.width,
# #         height=request.height,
# #         square_feet=round(square_feet, 2),
# #         cubic_feet=round(cubic_feet, 2),
# #         message=f"Room dimensions saved. Area: {square_feet:.2f} sq ft. "
# #                 f"Room: {session.room_type}, Theme: {session.theme}. "
# #                 f"You can now select furniture."
# #     )


# # # ===================================================================
# # # STEP 5: Select Furniture (Uses All Previous Data from Session)
# # # ===================================================================
# # @router.post(
# #     "/furniture/select",
# #     response_model=FurnitureSelectionResponse,
# #     summary="Step 5: Select Furniture",
# #     description="Select furniture - automatically uses room type, theme, and dimensions from session"
# # )
# # async def select_furniture(request: FurnitureSelectionRequest):
# #     """
# #     Select furniture and save to session.
# #     All previous data (room type, theme, dimensions) is already in session.
# #     """
    
# #     session = get_session(request.session_id)
    
# #     # Check all prerequisites
# #     if not session.room_type:
# #         raise HTTPException(
# #             status_code=status.HTTP_400_BAD_REQUEST,
# #             detail="Please select room type first (Step 2)"
# #         )
    
# #     if not session.theme:
# #         raise HTTPException(
# #             status_code=status.HTTP_400_BAD_REQUEST,
# #             detail="Please select theme first (Step 3)"
# #         )
    
# #     if not session.square_feet:
# #         raise HTTPException(
# #             status_code=status.HTTP_400_BAD_REQUEST,
# #             detail="Please set room dimensions first (Step 4)"
# #         )
    
# #     # Get furniture from JSON
# #     room_furniture = FURNITURE_DATA.get(session.room_type, {})
# #     furniture_types = room_furniture.get(request.furniture_type, {})
# #     dimensions = furniture_types.get(request.subtype)
    
# #     if not dimensions:
# #         raise HTTPException(
# #             status_code=status.HTTP_404_NOT_FOUND,
# #             detail=f"Furniture not found: {request.furniture_type} - {request.subtype}"
# #         )
    
# #     # Calculate size
# #     furniture_sqft = (dimensions["width"] * dimensions["depth"]) / 144.0
    
# #     # Check room capacity
# #     current_total = session.furniture_total_sqft or 0
# #     new_total = current_total + furniture_sqft
# #     room_usage = (new_total / session.square_feet) * 100
    
# #     if room_usage > MAX_FURNITURE_PERCENTAGE:
# #         raise HTTPException(
# #             status_code=status.HTTP_400_BAD_REQUEST,
# #             detail=f"Cannot add furniture. Room capacity exceeded. "
# #                    f"Usage would be {room_usage:.1f}%. Maximum: {MAX_FURNITURE_PERCENTAGE}%"
# #         )
    
# #     # Add to session
# #     furniture_item = {
# #         "type": request.furniture_type,
# #         "subtype": request.subtype,
# #         "dimensions": dimensions,
# #         "sqft": round(furniture_sqft, 2)
# #     }
    
# #     session.furniture_selections.append(furniture_item)
# #     session.furniture_total_sqft = sum(item["sqft"] for item in session.furniture_selections)
    
# #     logger.info(f"✓ Furniture added: {request.furniture_type} - {request.subtype}")
# #     logger.info(f"  Session data: Room={session.room_type}, Theme={session.theme}, Area={session.square_feet} sq ft")
    
# #     return FurnitureSelectionResponse(
# #         success=True,
# #         furniture_type=request.furniture_type,
# #         subtype=request.subtype,
# #         dimensions=dimensions,
# #         square_feet=round(furniture_sqft, 2),
# #         message=f"Added {request.subtype} to {session.room_type}. "
# #                 f"Total: {len(session.furniture_selections)} items, "
# #                 f"{session.furniture_total_sqft:.2f} sq ft "
# #                 f"({(session.furniture_total_sqft/session.square_feet)*100:.1f}% of room)"
# #     )


# # # ===================================================================
# # # GET SESSION INFO (Check What's in Session)
# # # ===================================================================
# # @router.get(
# #     "/session/{session_id}",
# #     summary="Get Session Info",
# #     description="Check what data is currently stored in session"
# # )
# # async def get_session_info(session_id: str):
# #     """Get current session data"""
    
# #     session = get_session(session_id)
    
# #     return {
# #         "success": True,
# #         "session_id": session_id,
# #         "data": {
# #             "room_type": session.room_type,
# #             "theme": session.theme,
# #             "dimensions": {
# #                 "length": session.length,
# #                 "width": session.width,
# #                 "height": session.height,
# #                 "square_feet": session.square_feet,
# #                 "cubic_feet": session.cubic_feet
# #             } if session.length else None,
# #             "furniture": {
# #                 "items": session.furniture_selections,
# #                 "total_count": len(session.furniture_selections),
# #                 "total_sqft": session.furniture_total_sqft
# #             },
# #             "price_range": {
# #                 "min": session.min_price,
# #                 "max": session.max_price
# #             } if session.min_price is not None else None
# #         },
# #         "progress": {
# #             "room_type_selected": session.room_type is not None,
# #             "theme_selected": session.theme is not None,
# #             "dimensions_set": session.square_feet is not None,
# #             "furniture_added": len(session.furniture_selections) > 0
# #         }
# #     }


# # # ===================================================================
# # # REMOVE FURNITURE
# # # ===================================================================
# # @router.delete(
# #     "/furniture/remove/{session_id}/{index}",
# #     summary="Remove Furniture",
# #     description="Remove furniture item by index"
# # )
# # async def remove_furniture(session_id: str, index: int):
# #     """Remove furniture from session"""
    
# #     session = get_session(session_id)
    
# #     if not session.furniture_selections:
# #         raise HTTPException(
# #             status_code=status.HTTP_400_BAD_REQUEST,
# #             detail="No furniture items to remove"
# #         )
    
# #     if index < 0 or index >= len(session.furniture_selections):
# #         raise HTTPException(
# #             status_code=status.HTTP_400_BAD_REQUEST,
# #             detail=f"Invalid index. Must be between 0 and {len(session.furniture_selections)-1}"
# #         )
    
# #     removed_item = session.furniture_selections.pop(index)
# #     session.furniture_total_sqft = sum(item["sqft"] for item in session.furniture_selections)
    
# #     logger.info(f"✓ Furniture removed: {removed_item['type']} - {removed_item['subtype']}")
    
# #     return {
# #         "success": True,
# #         "removed_item": removed_item,
# #         "remaining_furniture": session.furniture_selections,
# #         "total_sqft": session.furniture_total_sqft,
# #         "message": f"Removed {removed_item['subtype']}"
# #     }


# # # ===================================================================
# # # FIT CHECK
# # # ===================================================================
# # @router.post(
# #     "/furniture/fit-check",
# #     response_model=FurnitureFitCheckResponse,
# #     summary="Check Furniture Fit",
# #     description="Verify furniture fits in room"
# # )
# # async def check_furniture_fit(session_id: str):
# #     """Check if furniture fits"""
    
# #     session = get_session(session_id)
    
# #     if not session.square_feet:
# #         raise HTTPException(
# #             status_code=status.HTTP_400_BAD_REQUEST,
# #             detail="Please set room dimensions first (Step 4)"
# #         )
    
# #     if not session.furniture_selections:
# #         raise HTTPException(
# #             status_code=status.HTTP_400_BAD_REQUEST,
# #             detail="No furniture selected"
# #         )
    
# #     total_furniture_sqft = session.furniture_total_sqft or 0
# #     room_sqft = session.square_feet
# #     usage_percentage = (total_furniture_sqft / room_sqft) * 100
# #     remaining_percentage = 100 - usage_percentage
    
# #     fits = usage_percentage <= MAX_FURNITURE_PERCENTAGE
    
# #     if usage_percentage > 70:
# #         warning = "Room is crowded"
# #         message = "Furniture barely fits"
# #     elif usage_percentage > 60:
# #         warning = "Too much furniture"
# #         message = "Please remove items"
# #         fits = False
# #     elif usage_percentage > 50:
# #         warning = None
# #         message = "Good placement"
# #     else:
# #         warning = None
# #         message = "Plenty of space"
    
# #     return FurnitureFitCheckResponse(
# #         success=True,
# #         fits=fits,
# #         total_furniture_sqft=round(total_furniture_sqft, 2),
# #         room_sqft=round(room_sqft, 2),
# #         usage_percentage=round(usage_percentage, 2),
# #         remaining_space_percentage=round(remaining_percentage, 2),
# #         message=message,
# #         furniture_items=session.furniture_selections,
# #         warning=warning
# #     )




# """
# Selection API - Multiple Furniture Support
# ===========================================
# Supports adding/removing multiple furniture items dynamically
# """

# from fastapi import APIRouter, HTTPException, status
# from pydantic import BaseModel, Field
# from typing import List, Dict, Optional
# import json
# import logging
# from pathlib import Path

# logger = logging.getLogger(__name__)
# router = APIRouter()

# # Load furniture data
# FURNITURE_DATA_PATH = Path(__file__).parent.parent / "data" / "furniture_data.json"

# try:
#     with open(FURNITURE_DATA_PATH, "r", encoding='utf-8') as f:
#         FURNITURE_DATA = json.load(f)
#     logger.info(f"✅ Loaded furniture data")
# except Exception as e:
#     logger.error(f"❌ Failed to load furniture data: {e}")
#     FURNITURE_DATA = {}

# from ai_backend.api.upload import user_sessions
# from ai_backend.config import ROOM_TYPES, THEMES, MAX_FURNITURE_PERCENTAGE


# def get_session(session_id: str):
#     """Get session or raise 404"""
#     if session_id not in user_sessions:
#         raise HTTPException(404, "Session not found")
#     session = user_sessions[session_id]
#     session.update_timestamp()
#     return session


# # ===================================================================
# # PYDANTIC MODELS
# # ===================================================================

# class RoomTypeRequest(BaseModel):
#     session_id: str
#     room_type: str

# class ThemeRequest(BaseModel):
#     session_id: str
#     theme: str

# class RoomDimensionRequest(BaseModel):
#     session_id: str
#     length: float = Field(..., gt=0)
#     width: float = Field(..., gt=0)
#     height: float = Field(..., gt=0)

# class FurnitureSelectionRequest(BaseModel):
#     """Single furniture selection"""
#     session_id: str
#     furniture_type: str
#     subtype: str

# class MultipleFurnitureRequest(BaseModel):
#     """Add multiple furniture at once"""
#     session_id: str
#     furniture_list: List[Dict[str, str]] = Field(
#         ...,
#         example=[
#             {"type": "Sofa", "subtype": "3-Seater Sofa"},
#             {"type": "Coffee Table", "subtype": "Rectangular"}
#         ]
#     )


# # ===================================================================
# # DROPDOWN OPTIONS (No Session Required)
# # ===================================================================

# @router.get("/options/room-types")
# async def get_room_types():
#     """Get room type dropdown"""
#     return {
#         "success": True,
#         "options": [
#             {"value": rt, "label": rt, "furniture_count": len(FURNITURE_DATA.get(rt, {}))}
#             for rt in ROOM_TYPES
#         ],
#         "count": len(ROOM_TYPES)
#     }


# @router.get("/options/themes")
# async def get_themes():
#     """Get theme dropdown"""
#     return {
#         "success": True,
#         "options": [
#             {
#                 "value": theme,
#                 "label": theme.replace('_', ' ').title(),
#                 "website_count": len(websites)
#             }
#             for theme, websites in THEMES.items()
#         ],
#         "count": len(THEMES)
#     }


# @router.get("/options/furniture-types/{session_id}")
# async def get_furniture_types(session_id: str):
#     """Get furniture types based on room type in session"""
#     session = get_session(session_id)
    
#     if not session.room_type:
#         raise HTTPException(400, "Please select room type first")
    
#     room_furniture = FURNITURE_DATA.get(session.room_type, {})
    
#     return {
#         "success": True,
#         "room_type": session.room_type,
#         "options": [
#             {
#                 "value": ftype,
#                 "label": ftype,
#                 "subtype_count": len(subtypes)
#             }
#             for ftype, subtypes in room_furniture.items()
#         ],
#         "count": len(room_furniture)
#     }


# @router.get("/options/furniture-subtypes/{session_id}/{furniture_type}")
# async def get_furniture_subtypes(session_id: str, furniture_type: str):
#     """Get subtypes for a furniture type"""
#     session = get_session(session_id)
    
#     if not session.room_type:
#         raise HTTPException(400, "Please select room type first")
    
#     room_furniture = FURNITURE_DATA.get(session.room_type, {})
#     subtypes_data = room_furniture.get(furniture_type, {})
    
#     if not subtypes_data:
#         raise HTTPException(404, f"No subtypes found for '{furniture_type}'")
    
#     options = []
#     for subtype, dims in subtypes_data.items():
#         sqft = round((dims["width"] * dims["depth"]) / 144.0, 2)
#         options.append({
#             "value": subtype,
#             "label": subtype,
#             "dimensions": dims,
#             "sqft": sqft,
#             "description": f'{dims["width"]}" × {dims["depth"]}" × {dims["height"]}" ({sqft} sq ft)'
#         })
    
#     return {
#         "success": True,
#         "furniture_type": furniture_type,
#         "options": options,
#         "count": len(options)
#     }


# # ===================================================================
# # STEP 2: Select Room Type
# # ===================================================================

# @router.post("/room-type")
# async def select_room_type(request: RoomTypeRequest):
#     """Select room type and save to session"""
#     session = get_session(request.session_id)
    
#     if request.room_type not in ROOM_TYPES:
#         raise HTTPException(400, f"Invalid room type")
    
#     session.room_type = request.room_type
#     available_furniture = list(FURNITURE_DATA.get(request.room_type, {}).keys())
    
#     logger.info(f"✓ Room type: {request.room_type}")
    
#     return {
#         "success": True,
#         "room_type": request.room_type,
#         "available_furniture": available_furniture,
#         "message": f"Room type saved. {len(available_furniture)} furniture types available."
#     }


# # ===================================================================
# # STEP 3: Select Theme
# # ===================================================================

# @router.post("/theme")
# async def select_theme(request: ThemeRequest):
#     """Select theme and save to session"""
#     session = get_session(request.session_id)
    
#     if not session.room_type:
#         raise HTTPException(400, "Please select room type first")
    
#     theme_upper = request.theme.upper()
#     if theme_upper not in THEMES:
#         raise HTTPException(400, f"Invalid theme")
    
#     session.theme = theme_upper
#     websites = THEMES[theme_upper]
    
#     logger.info(f"✓ Theme: {theme_upper}")
    
#     return {
#         "success": True,
#         "theme": theme_upper,
#         "websites": websites,
#         "website_count": len(websites),
#         "message": f"Theme saved. Will search {len(websites)} websites."
#     }


# # ===================================================================
# # STEP 4: Room Dimensions
# # ===================================================================

# @router.post("/dimensions")
# async def set_dimensions(request: RoomDimensionRequest):
#     """Set room dimensions"""
#     session = get_session(request.session_id)
    
#     if not session.room_type or not session.theme:
#         raise HTTPException(400, "Please complete previous steps first")
    
#     square_feet = request.length * request.width
#     cubic_feet = square_feet * request.height
    
#     session.length = request.length
#     session.width = request.width
#     session.height = request.height
#     session.square_feet = square_feet
#     session.cubic_feet = cubic_feet
    
#     logger.info(f"✓ Dimensions: {request.length}' × {request.width}' = {square_feet} sq ft")
    
#     return {
#         "success": True,
#         "dimensions": {
#             "length": request.length,
#             "width": request.width,
#             "height": request.height,
#             "square_feet": round(square_feet, 2),
#             "cubic_feet": round(cubic_feet, 2)
#         },
#         "message": f"Room area: {square_feet:.2f} sq ft"
#     }


# # ===================================================================
# # STEP 5: Add Single Furniture (+ Button)
# # ===================================================================

# @router.post("/furniture/add")
# async def add_furniture(request: FurnitureSelectionRequest):
#     """
#     Add single furniture item (called when user clicks + button)
    
#     Auto-calculates dimensions and checks fit
#     """
#     session = get_session(request.session_id)
    
#     # Validate prerequisites
#     if not session.room_type or not session.theme or not session.square_feet:
#         raise HTTPException(400, "Please complete previous steps first")
    
#     # Get furniture dimensions
#     room_furniture = FURNITURE_DATA.get(session.room_type, {})
#     furniture_types = room_furniture.get(request.furniture_type, {})
#     dimensions = furniture_types.get(request.subtype)
    
#     if not dimensions:
#         raise HTTPException(404, f"Furniture not found: {request.furniture_type} - {request.subtype}")
    
#     # Calculate area
#     furniture_sqft = (dimensions["width"] * dimensions["depth"]) / 144.0
    
#     # Check room capacity BEFORE adding
#     current_total = session.furniture_total_sqft or 0
#     new_total = current_total + furniture_sqft
#     room_usage = (new_total / session.square_feet) * 100
    
#     if room_usage > MAX_FURNITURE_PERCENTAGE:
#         raise HTTPException(400, {
#             "error": "Room capacity exceeded",
#             "message": f"Cannot add furniture. Usage would be {room_usage:.1f}%. Max: {MAX_FURNITURE_PERCENTAGE}%",
#             "current_usage": round((current_total / session.square_feet) * 100, 2),
#             "furniture_sqft": round(furniture_sqft, 2),
#             "room_sqft": session.square_feet
#         })
    
#     # Add furniture
#     furniture_item = {
#         "type": request.furniture_type,
#         "subtype": request.subtype,
#         "dimensions": dimensions,
#         "sqft": round(furniture_sqft, 2)
#     }
    
#     session.furniture_selections.append(furniture_item)
#     session.furniture_total_sqft = sum(item["sqft"] for item in session.furniture_selections)
    
#     usage_percent = (session.furniture_total_sqft / session.square_feet) * 100
    
#     logger.info(f"✓ Added: {request.subtype} ({furniture_sqft:.2f} sq ft)")
    
#     return {
#         "success": True,
#         "added": furniture_item,
#         "furniture_list": session.furniture_selections,
#         "summary": {
#             "total_items": len(session.furniture_selections),
#             "total_sqft": round(session.furniture_total_sqft, 2),
#             "room_sqft": session.square_feet,
#             "usage_percentage": round(usage_percent, 2),
#             "remaining_percentage": round(100 - usage_percent, 2)
#         },
#         "message": f"Added {request.subtype}. Room usage: {usage_percent:.1f}%"
#     }


# # ===================================================================
# # STEP 5b: Add Multiple Furniture at Once
# # ===================================================================

# @router.post("/furniture/add-multiple")
# async def add_multiple_furniture(request: MultipleFurnitureRequest):
#     """
#     Add multiple furniture items at once
    
#     Validates all items before adding any
#     """
#     session = get_session(request.session_id)
    
#     if not session.room_type or not session.square_feet:
#         raise HTTPException(400, "Please complete previous steps first")
    
#     # Validate and calculate all items first
#     items_to_add = []
#     total_new_sqft = 0
    
#     for item in request.furniture_list:
#         ftype = item.get("type")
#         subtype = item.get("subtype")
        
#         if not ftype or not subtype:
#             raise HTTPException(400, "Each item must have 'type' and 'subtype'")
        
#         # Get dimensions
#         room_furniture = FURNITURE_DATA.get(session.room_type, {})
#         furniture_types = room_furniture.get(ftype, {})
#         dimensions = furniture_types.get(subtype)
        
#         if not dimensions:
#             raise HTTPException(404, f"Furniture not found: {ftype} - {subtype}")
        
#         sqft = (dimensions["width"] * dimensions["depth"]) / 144.0
#         total_new_sqft += sqft
        
#         items_to_add.append({
#             "type": ftype,
#             "subtype": subtype,
#             "dimensions": dimensions,
#             "sqft": round(sqft, 2)
#         })
    
#     # Check total capacity
#     current_total = session.furniture_total_sqft or 0
#     new_total = current_total + total_new_sqft
#     room_usage = (new_total / session.square_feet) * 100
    
#     if room_usage > MAX_FURNITURE_PERCENTAGE:
#         raise HTTPException(400, {
#             "error": "Room capacity exceeded",
#             "message": f"Cannot add all items. Usage would be {room_usage:.1f}%",
#             "current_usage": round((current_total / session.square_feet) * 100, 2),
#             "max_allowed": MAX_FURNITURE_PERCENTAGE
#         })
    
#     # Add all items
#     session.furniture_selections.extend(items_to_add)
#     session.furniture_total_sqft = sum(item["sqft"] for item in session.furniture_selections)
    
#     usage_percent = (session.furniture_total_sqft / session.square_feet) * 100
    
#     logger.info(f"✓ Added {len(items_to_add)} furniture items")
    
#     return {
#         "success": True,
#         "added_count": len(items_to_add),
#         "furniture_list": session.furniture_selections,
#         "summary": {
#             "total_items": len(session.furniture_selections),
#             "total_sqft": round(session.furniture_total_sqft, 2),
#             "usage_percentage": round(usage_percent, 2)
#         },
#         "message": f"Added {len(items_to_add)} items. Room usage: {usage_percent:.1f}%"
#     }


# # ===================================================================
# # REMOVE FURNITURE (- Button or Delete)
# # ===================================================================

# @router.delete("/furniture/remove/{session_id}/{index}")
# async def remove_furniture(session_id: str, index: int):
#     """
#     Remove furniture by index (0-based)
    
#     Called when user clicks remove/delete button
#     """
#     session = get_session(session_id)
    
#     if not session.furniture_selections:
#         raise HTTPException(400, "No furniture to remove")
    
#     if index < 0 or index >= len(session.furniture_selections):
#         raise HTTPException(400, f"Invalid index. Must be 0-{len(session.furniture_selections)-1}")
    
#     removed = session.furniture_selections.pop(index)
#     session.furniture_total_sqft = sum(item["sqft"] for item in session.furniture_selections)
    
#     usage_percent = (session.furniture_total_sqft / session.square_feet) * 100 if session.square_feet else 0
    
#     logger.info(f"✓ Removed: {removed['subtype']}")
    
#     return {
#         "success": True,
#         "removed": removed,
#         "furniture_list": session.furniture_selections,
#         "summary": {
#             "total_items": len(session.furniture_selections),
#             "total_sqft": round(session.furniture_total_sqft, 2),
#             "usage_percentage": round(usage_percent, 2)
#         },
#         "message": f"Removed {removed['subtype']}"
#     }


# # ===================================================================
# # CLEAR ALL FURNITURE
# # ===================================================================

# @router.delete("/furniture/clear/{session_id}")
# async def clear_all_furniture(session_id: str):
#     """Clear all furniture selections"""
#     session = get_session(session_id)
    
#     count = len(session.furniture_selections)
#     session.furniture_selections = []
#     session.furniture_total_sqft = 0.0
    
#     logger.info(f"✓ Cleared {count} furniture items")
    
#     return {
#         "success": True,
#         "cleared_count": count,
#         "message": f"Cleared all {count} furniture items"
#     }


# # ===================================================================
# # GET CURRENT FURNITURE LIST
# # ===================================================================

# @router.get("/furniture/list/{session_id}")
# async def get_furniture_list(session_id: str):
#     """Get current furniture list with summary"""
#     session = get_session(session_id)
    
#     usage_percent = (session.furniture_total_sqft / session.square_feet) * 100 if session.square_feet else 0
    
#     return {
#         "success": True,
#         "furniture_list": session.furniture_selections,
#         "summary": {
#             "total_items": len(session.furniture_selections),
#             "total_sqft": round(session.furniture_total_sqft, 2),
#             "room_sqft": session.square_feet,
#             "usage_percentage": round(usage_percent, 2),
#             "remaining_percentage": round(100 - usage_percent, 2),
#             "can_add_more": usage_percent < MAX_FURNITURE_PERCENTAGE
#         }
#     }


# # ===================================================================
# # FIT CHECK
# # ===================================================================

# @router.get("/furniture/fit-check/{session_id}")
# async def fit_check(session_id: str):
#     """Check if furniture fits in room"""
#     session = get_session(session_id)
    
#     if not session.square_feet:
#         raise HTTPException(400, "Room dimensions not set")
    
#     if not session.furniture_selections:
#         raise HTTPException(400, "No furniture selected")
    
#     usage = (session.furniture_total_sqft / session.square_feet) * 100
#     fits = usage <= MAX_FURNITURE_PERCENTAGE
    
#     if usage > 70:
#         status_msg = "⚠️ Very crowded"
#     elif usage > 60:
#         status_msg = "❌ Too much furniture"
#     elif usage > 50:
#         status_msg = "✅ Good placement"
#     else:
#         status_msg = "✅ Plenty of space"
    
#     return {
#         "success": True,
#         "fits": fits,
#         "status": status_msg,
#         "usage_percentage": round(usage, 2),
#         "room_sqft": session.square_feet,
#         "furniture_sqft": session.furniture_total_sqft,
#         "furniture_count": len(session.furniture_selections)
#     }


# # ===================================================================
# # GET SESSION INFO
# # ===================================================================

# @router.get("/session/{session_id}")
# async def get_session_info(session_id: str):
#     """Get complete session data"""
#     session = get_session(session_id)
    
#     return {
#         "success": True,
#         "session_id": session_id,
#         "data": {
#             "room_image_url": session.room_image_url,
#             "room_type": session.room_type,
#             "theme": session.theme,
#             "dimensions": {
#                 "length": session.length,
#                 "width": session.width,
#                 "height": session.height,
#                 "square_feet": session.square_feet
#             } if session.length else None,
#             "furniture": {
#                 "items": session.furniture_selections,
#                 "count": len(session.furniture_selections),
#                 "total_sqft": session.furniture_total_sqft,
#                 "usage_percentage": round(
#                     (session.furniture_total_sqft / session.square_feet * 100), 2
#                 ) if session.square_feet else 0
#             }
#         }
#     }



"""
Selection API Endpoints
=======================

Progressive workflow with session-based data carry-forward.
"""

from fastapi import APIRouter, HTTPException, status
from ai_backend.models import (
    RoomTypeRequest, RoomTypeResponse,
    ThemeRequest, ThemeResponse,
    RoomDimensionRequest, RoomDimensionResponse,
    FurnitureSelectionRequest, FurnitureSelectionResponse,
    FurnitureFitCheckResponse
)
from ai_backend.config import THEMES, ROOM_TYPES, MAX_FURNITURE_PERCENTAGE
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# Load furniture data
FURNITURE_DATA_PATH = Path(__file__).parent.parent / "data" / "furniture_data.json"

try:
    with open(FURNITURE_DATA_PATH, "r", encoding='utf-8') as f:
        FURNITURE_DATA = json.load(f)
    logger.info(f"✅ Loaded furniture data")
except Exception as e:
    logger.error(f"❌ Failed to load furniture data: {e}")
    FURNITURE_DATA = {}

# Import session storage
from ai_backend.api.upload import user_sessions


def get_session(session_id: str):
    """Get session or raise 404 error"""
    if session_id not in user_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found. Please upload room image first."
        )
    
    session = user_sessions[session_id]
    session.update_timestamp()
    return session


# ===================================================================
# Additional Pydantic Models
# ===================================================================
class MultipleFurnitureRequest(BaseModel):
    """Add multiple furniture at once"""
    session_id: str
    furniture_list: List[Dict[str, str]] = Field(
        ...,
        example=[
            {"type": "Sofa", "subtype": "3-Seater Sofa"},
            {"type": "Coffee Table", "subtype": "Rectangular"}
        ]
    )


# ===================================================================
# DROPDOWN ENDPOINTS (Options Only - No Session Required)
# ===================================================================

@router.get(
    "/options/room-types",
    summary="Get Room Type Dropdown",
    description="Get all available room types for dropdown (no session needed)"
)
async def get_room_type_options() -> Dict[str, Any]:
    """Get room type dropdown options"""
    
    options = [
        {
            "value": rt,
            "label": rt,
            "furniture_count": len(FURNITURE_DATA.get(rt, {}))
        }
        for rt in ROOM_TYPES
    ]
    
    return {
        "success": True,
        "options": options,
        "count": len(options)
    }


@router.get(
    "/options/themes",
    summary="Get Theme Dropdown",
    description="Get all available themes for dropdown (no session needed)"
)
async def get_theme_options() -> Dict[str, Any]:
    """Get theme dropdown options"""
    
    options = [
        {
            "value": theme,
            "label": theme.replace('_', ' ').title(),
            "website_count": len(websites),
            "preview_websites": websites[:3]
        }
        for theme, websites in THEMES.items()
    ]
    
    return {
        "success": True,
        "options": options,
        "count": len(options)
    }


# ===================================================================
# STEP 2: Select Room Type (Saves to Session)
# ===================================================================
@router.post(
    "/room-type",
    response_model=RoomTypeResponse,
    summary="Step 2: Select Room Type",
    description="Select room type from dropdown - saves to session for next steps"
)
async def select_room_type(request: RoomTypeRequest):
    """
    Select room type and save to session.
    This data will be automatically available in next steps.
    """
    
    session = get_session(request.session_id)
    
    if request.room_type not in ROOM_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid room type. Valid options: {', '.join(ROOM_TYPES)}"
        )
    
    # Save to session
    session.room_type = request.room_type
    
    available_furniture = list(FURNITURE_DATA.get(request.room_type, {}).keys())
    
    logger.info(f"✓ Room type saved to session: {request.room_type}")
    
    return RoomTypeResponse(
        success=True,
        room_type=request.room_type,
        available_furniture=available_furniture,
        message=f"Room type '{request.room_type}' saved to session. "
                f"{len(available_furniture)} furniture types available. "
                f"You can now select theme."
    )


# ===================================================================
# STEP 3: Select Theme (Uses Room Type from Session)
# ===================================================================
@router.post(
    "/theme",
    response_model=ThemeResponse,
    summary="Step 3: Select Theme",
    description="Select theme from dropdown - automatically uses room type from session"
)
async def select_theme(request: ThemeRequest):
    """
    Select theme and save to session.
    Room type from Step 2 is already in session.
    """
    
    session = get_session(request.session_id)
    
    # Check if room type was selected
    if not session.room_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please select room type first (Step 2)"
        )
    
    theme_upper = request.theme.upper()
    
    if theme_upper not in THEMES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid theme. Valid options: {', '.join(THEMES.keys())}"
        )
    
    # Save to session
    session.theme = theme_upper
    
    websites = THEMES[theme_upper]
    
    logger.info(f"✓ Theme saved to session: {theme_upper}")
    logger.info(f"  Room type from session: {session.room_type}")
    
    return ThemeResponse(
        success=True,
        theme=theme_upper,
        websites=websites,
        website_count=len(websites),
        message=f"Theme '{theme_upper}' saved to session. "
                f"Room type '{session.room_type}' is already set. "
                f"You can now enter room dimensions."
    )


# ===================================================================
# STEP 4: Enter Room Dimensions (Uses Room Type + Theme from Session)
# ===================================================================
@router.post(
    "/dimensions",
    response_model=RoomDimensionResponse,
    summary="Step 4: Set Room Dimensions",
    description="Enter room dimensions - automatically uses room type and theme from session"
)
async def set_room_dimensions(request: RoomDimensionRequest):
    """
    Set room dimensions and save to session.
    Room type and theme from previous steps are already in session.
    """
    
    session = get_session(request.session_id)
    
    # Check prerequisites
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
    
    # Calculate areas
    square_feet = request.length * request.width
    cubic_feet = request.length * request.width * request.height
    
    # Save to session
    session.length = request.length
    session.width = request.width
    session.height = request.height
    session.square_feet = square_feet
    session.cubic_feet = cubic_feet
    
    logger.info(f"✓ Dimensions saved to session: {request.length}' x {request.width}' x {request.height}'")
    logger.info(f"  Room type: {session.room_type}, Theme: {session.theme}")
    
    return RoomDimensionResponse(
        success=True,
        length=request.length,
        width=request.width,
        height=request.height,
        square_feet=round(square_feet, 2),
        cubic_feet=round(cubic_feet, 2),
        message=f"Room dimensions saved. Area: {square_feet:.2f} sq ft. "
                f"Room: {session.room_type}, Theme: {session.theme}. "
                f"You can now select furniture."
    )


# ===================================================================
# STEP 5: Select Furniture (Uses All Previous Data from Session)
# ===================================================================
@router.post(
    "/furniture/select",
    response_model=FurnitureSelectionResponse,
    summary="Step 5: Select Furniture",
    description="Select furniture - automatically uses room type, theme, and dimensions from session"
)
async def select_furniture(request: FurnitureSelectionRequest):
    """
    Select furniture and save to session.
    All previous data (room type, theme, dimensions) is already in session.
    """
    
    session = get_session(request.session_id)
    
    # Check all prerequisites
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
    
    if not session.square_feet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please set room dimensions first (Step 4)"
        )
    
    # Get furniture from JSON
    room_furniture = FURNITURE_DATA.get(session.room_type, {})
    furniture_types = room_furniture.get(request.furniture_type, {})
    dimensions = furniture_types.get(request.subtype)
    
    if not dimensions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Furniture not found: {request.furniture_type} - {request.subtype}"
        )
    
    # Calculate size
    furniture_sqft = (dimensions["width"] * dimensions["depth"]) / 144.0
    
    # Check room capacity
    current_total = session.furniture_total_sqft or 0
    new_total = current_total + furniture_sqft
    room_usage = (new_total / session.square_feet) * 100
    
    if room_usage > MAX_FURNITURE_PERCENTAGE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot add furniture. Room capacity exceeded. "
                   f"Usage would be {room_usage:.1f}%. Maximum: {MAX_FURNITURE_PERCENTAGE}%"
        )
    
    # Add to session
    furniture_item = {
        "type": request.furniture_type,
        "subtype": request.subtype,
        "dimensions": dimensions,
        "sqft": round(furniture_sqft, 2)
    }
    
    session.furniture_selections.append(furniture_item)
    session.furniture_total_sqft = sum(item["sqft"] for item in session.furniture_selections)
    
    logger.info(f"✓ Furniture added: {request.furniture_type} - {request.subtype}")
    logger.info(f"  Session data: Room={session.room_type}, Theme={session.theme}, Area={session.square_feet} sq ft")
    
    return FurnitureSelectionResponse(
        success=True,
        furniture_type=request.furniture_type,
        subtype=request.subtype,
        dimensions=dimensions,
        square_feet=round(furniture_sqft, 2),
        message=f"Added {request.subtype} to {session.room_type}. "
                f"Total: {len(session.furniture_selections)} items, "
                f"{session.furniture_total_sqft:.2f} sq ft "
                f"({(session.furniture_total_sqft/session.square_feet)*100:.1f}% of room)"
    )


# ===================================================================
# STEP 5b: Add Multiple Furniture at Once
# ===================================================================
@router.post(
    "/furniture/add-multiple",
    summary="Add Multiple Furniture",
    description="Add multiple furniture items at once"
)
async def add_multiple_furniture(request: MultipleFurnitureRequest):
    """
    Add multiple furniture items at once
    
    Validates all items before adding any
    """
    session = get_session(request.session_id)
    
    if not session.room_type or not session.square_feet:
        raise HTTPException(400, "Please complete previous steps first")
    
    # Validate and calculate all items first
    items_to_add = []
    total_new_sqft = 0
    
    for item in request.furniture_list:
        ftype = item.get("type")
        subtype = item.get("subtype")
        
        if not ftype or not subtype:
            raise HTTPException(400, "Each item must have 'type' and 'subtype'")
        
        # Get dimensions
        room_furniture = FURNITURE_DATA.get(session.room_type, {})
        furniture_types = room_furniture.get(ftype, {})
        dimensions = furniture_types.get(subtype)
        
        if not dimensions:
            raise HTTPException(404, f"Furniture not found: {ftype} - {subtype}")
        
        sqft = (dimensions["width"] * dimensions["depth"]) / 144.0
        total_new_sqft += sqft
        
        items_to_add.append({
            "type": ftype,
            "subtype": subtype,
            "dimensions": dimensions,
            "sqft": round(sqft, 2)
        })
    
    # Check total capacity
    current_total = session.furniture_total_sqft or 0
    new_total = current_total + total_new_sqft
    room_usage = (new_total / session.square_feet) * 100
    
    if room_usage > MAX_FURNITURE_PERCENTAGE:
        raise HTTPException(400, {
            "error": "Room capacity exceeded",
            "message": f"Cannot add all items. Usage would be {room_usage:.1f}%",
            "current_usage": round((current_total / session.square_feet) * 100, 2),
            "max_allowed": MAX_FURNITURE_PERCENTAGE
        })
    
    # Add all items
    session.furniture_selections.extend(items_to_add)
    session.furniture_total_sqft = sum(item["sqft"] for item in session.furniture_selections)
    
    usage_percent = (session.furniture_total_sqft / session.square_feet) * 100
    
    logger.info(f"✓ Added {len(items_to_add)} furniture items")
    
    return {
        "success": True,
        "added_count": len(items_to_add),
        "furniture_list": session.furniture_selections,
        "summary": {
            "total_items": len(session.furniture_selections),
            "total_sqft": round(session.furniture_total_sqft, 2),
            "usage_percentage": round(usage_percent, 2)
        },
        "message": f"Added {len(items_to_add)} items. Room usage: {usage_percent:.1f}%"
    }


# ===================================================================
# GET CURRENT FURNITURE LIST
# ===================================================================
@router.get(
    "/furniture/list/{session_id}",
    summary="Get Furniture List",
    description="Get current furniture list with summary"
)
async def get_furniture_list(session_id: str):
    """Get current furniture list with summary"""
    session = get_session(session_id)
    
    usage_percent = (session.furniture_total_sqft / session.square_feet) * 100 if session.square_feet else 0
    
    return {
        "success": True,
        "furniture_list": session.furniture_selections,
        "summary": {
            "total_items": len(session.furniture_selections),
            "total_sqft": round(session.furniture_total_sqft, 2),
            "room_sqft": session.square_feet,
            "usage_percentage": round(usage_percent, 2),
            "remaining_percentage": round(100 - usage_percent, 2),
            "can_add_more": usage_percent < MAX_FURNITURE_PERCENTAGE
        }
    }


# ===================================================================
# FIT CHECK
# ===================================================================
@router.post(
    "/furniture/fit-check",
    response_model=FurnitureFitCheckResponse,
    summary="Check Furniture Fit",
    description="Verify furniture fits in room"
)
async def check_furniture_fit(session_id: str):
    """Check if furniture fits"""
    
    session = get_session(session_id)
    
    if not session.square_feet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please set room dimensions first (Step 4)"
        )
    
    if not session.furniture_selections:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No furniture selected"
        )
    
    total_furniture_sqft = session.furniture_total_sqft or 0
    room_sqft = session.square_feet
    usage_percentage = (total_furniture_sqft / room_sqft) * 100
    remaining_percentage = 100 - usage_percentage
    
    fits = usage_percentage <= MAX_FURNITURE_PERCENTAGE
    
    if usage_percentage > 70:
        warning = "Room is crowded"
        message = "Furniture barely fits"
    elif usage_percentage > 60:
        warning = "Too much furniture"
        message = "Please remove items"
        fits = False
    elif usage_percentage > 50:
        warning = None
        message = "Good placement"
    else:
        warning = None
        message = "Plenty of space"
    
    return FurnitureFitCheckResponse(
        success=True,
        fits=fits,
        total_furniture_sqft=round(total_furniture_sqft, 2),
        room_sqft=round(room_sqft, 2),
        usage_percentage=round(usage_percentage, 2),
        remaining_space_percentage=round(remaining_percentage, 2),
        message=message,
        furniture_items=session.furniture_selections,
        warning=warning
    )