"""
Data Models Module
==================

Pydantic models for request/response validation and data structures.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict
from datetime import datetime


# ===================================================================
# Step 1: Upload Room Image
# ===================================================================
class RoomImageUploadResponse(BaseModel):
    """Response after uploading room image"""
    success: bool
    image_url: str
    session_id: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)


# ===================================================================
# Step 2: Select Room Type
# ===================================================================
class RoomTypeRequest(BaseModel):
    """Request to select room type"""
    session_id: str = Field(..., description="Session ID from upload")
    room_type: str = Field(
        ...,
        description="Room type from dropdown",
        example="Living Room Furniture"
    )


class RoomTypeResponse(BaseModel):
    """Response with available furniture for selected room"""
    success: bool
    room_type: str
    available_furniture: List[str]
    message: str


# ===================================================================
# Step 3: Select Theme
# ===================================================================
class ThemeRequest(BaseModel):
    """Request to select design theme"""
    session_id: str
    theme: str = Field(
        ...,
        description="Design theme from dropdown",
        example="MINIMAL SCANDINAVIAN"
    )


class ThemeResponse(BaseModel):
    """Response with theme websites"""
    success: bool
    theme: str
    websites: List[str]
    website_count: int
    message: str


# ===================================================================
# Step 4: Enter Room Dimensions
# ===================================================================
class RoomDimensionRequest(BaseModel):
    """Request to set room dimensions"""
    session_id: str
    length: float = Field(..., gt=0, description="Room length in feet")
    width: float = Field(..., gt=0, description="Room width in feet")
    height: float = Field(..., gt=0, description="Room height in feet")
    
    @validator('length', 'width', 'height')
    def validate_dimensions(cls, v):
        if v <= 0:
            raise ValueError("Dimension must be greater than 0")
        if v > 1000:
            raise ValueError("Dimension too large. Please enter realistic values.")
        return v


class RoomDimensionResponse(BaseModel):
    """Response with calculated area"""
    success: bool
    length: float
    width: float
    height: float
    square_feet: float
    cubic_feet: float
    message: str


# ===================================================================
# Step 5: Select Furniture with Subtypes
# ===================================================================
class FurnitureSelectionRequest(BaseModel):
    """Request to select furniture"""
    session_id: str
    furniture_type: str = Field(..., example="Bed", description="Main furniture category")
    subtype: str = Field(..., example="Queen Bed", description="Specific furniture subtype")


class FurnitureSelectionResponse(BaseModel):
    """Response with furniture dimensions"""
    success: bool
    furniture_type: str
    subtype: str
    dimensions: Dict[str, float]
    square_feet: float
    message: str


class MultipleFurnitureRequest(BaseModel):
    """Request to add multiple furniture items"""
    session_id: str
    furniture_list: List[Dict[str, str]] = Field(
        ...,
        example=[
            {"type": "Bed", "subtype": "Queen Bed"},
            {"type": "Nightstand", "subtype": "Standard Nightstand"}
        ]
    )


class FurnitureFitCheckResponse(BaseModel):
    """Check if all furniture fits in room"""
    success: bool
    fits: bool
    total_furniture_sqft: float
    room_sqft: float
    usage_percentage: float
    remaining_space_percentage: float
    message: str
    furniture_items: List[Dict]
    warning: Optional[str] = None


# ===================================================================
# Step 6: Enter Price Range
# ===================================================================
class PriceRangeRequest(BaseModel):
    """Request with price range for furniture search"""
    session_id: str
    min_price: float = Field(..., ge=0, description="Minimum price in USD")
    max_price: float = Field(..., gt=0, description="Maximum price in USD")
    
    @validator('max_price')
    def validate_price_range(cls, v, values):
        if 'min_price' in values and v <= values['min_price']:
            raise ValueError("Max price must be greater than min price")
        return v


# ===================================================================
# Step 7: Search Furniture on Websites
# ===================================================================
class FurnitureSearchRequest(BaseModel):
    """Complete search request"""
    session_id: str


class FurnitureItem(BaseModel):
    """Single furniture item from search"""
    name: str
    link: str
    price: float
    image_url: str
    dimensions: Dict[str, float]
    website: str
    description: Optional[str] = None


class FurnitureSearchResponse(BaseModel):
    """Response with found furniture"""
    success: bool
    results: List[FurnitureItem]
    count: int
    searched_websites: int
    message: str


# ===================================================================
# Step 8-9: Generate Final Image
# ===================================================================
class ImageGenerationRequest(BaseModel):
    """Request to generate final room image"""
    session_id: str
    prompt: str = Field(
        ...,
        description="Placement instructions for furniture",
        example="Place the queen bed against the left wall, nightstands on both sides"
    )
    furniture_links: List[str] = Field(
        ...,
        description="Selected furniture URLs from search results",
        min_items=1
    )


class ImageGenerationResponse(BaseModel):
    """Response with generated image"""
    success: bool
    generated_image_url: str
    original_image_url: str
    furniture_items: List[FurnitureItem]
    prompt_used: str
    generation_time_seconds: float
    message: str


# ===================================================================
# Session Storage Model
# ===================================================================
class UserSession(BaseModel):
    """Store user's selections and progress"""
    session_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    
    # Step 1: Room image
    room_image_url: Optional[str] = None
    
    # Step 2: Room type
    room_type: Optional[str] = None
    
    # Step 3: Theme
    theme: Optional[str] = None
    
    # Step 4: Dimensions
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    square_feet: Optional[float] = None
    cubic_feet: Optional[float] = None
    
    # Step 5: Furniture selections
    furniture_selections: List[Dict] = []
    furniture_total_sqft: float = 0.0
    
    # Step 6: Price range
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    
    # Step 7: Search results
    search_results: List[FurnitureItem] = []
    
    # Step 8-9: Generated images
    generated_images: List[str] = []
    
    def update_timestamp(self):
        """Update last_updated timestamp"""
        self.last_updated = datetime.now()
    
    def is_expired(self, expiry_seconds: int = 3600) -> bool:
        """Check if session has expired"""
        elapsed = (datetime.now() - self.last_updated).total_seconds()
        return elapsed > expiry_seconds


# ===================================================================
# Error Response Model
# ===================================================================
class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)