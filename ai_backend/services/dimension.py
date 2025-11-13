"""
Dimension Service
=================

Handles all dimension calculations for rooms and furniture.
"""

import json
import logging
from typing import Dict, Optional, List, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

# Load furniture data
FURNITURE_DATA_PATH = Path(__file__).parent.parent / "data" / "furniture_data.json"

try:
    with open(FURNITURE_DATA_PATH, "r") as f:
        FURNITURE_DATA = json.load(f)
    logger.info(f"✅ Dimension service loaded furniture data")
except Exception as e:
    logger.error(f"❌ Failed to load furniture data: {e}")
    FURNITURE_DATA = {}


def calculate_room_area(length: float, width: float) -> float:
    """
    Calculate room area in square feet
    
    Args:
        length: Room length in feet
        width: Room width in feet
        
    Returns:
        Area in square feet
    """
    return length * width


def calculate_room_volume(length: float, width: float, height: float) -> float:
    """
    Calculate room volume in cubic feet
    
    Args:
        length: Room length in feet
        width: Room width in feet
        height: Room height in feet
        
    Returns:
        Volume in cubic feet
    """
    return length * width * height


def get_furniture_dimensions(
    room_type: str,
    furniture_type: str,
    subtype: str
) -> Optional[Dict[str, float]]:
    """
    Get furniture dimensions from data
    
    Args:
        room_type: Room type (e.g., "Living Room Furniture")
        furniture_type: Furniture category (e.g., "Sofa")
        subtype: Specific subtype (e.g., "3-Seater Sofa")
        
    Returns:
        Dictionary with width, depth, height in inches, or None if not found
    """
    try:
        return FURNITURE_DATA[room_type][furniture_type][subtype]
    except KeyError:
        logger.warning(f"Furniture not found: {room_type} > {furniture_type} > {subtype}")
        return None


def calculate_furniture_area(dimensions: Dict[str, float]) -> float:
    """
    Calculate furniture footprint in square feet
    
    Args:
        dimensions: Dictionary with width and depth in inches
        
    Returns:
        Area in square feet
    """
    # Convert inches to feet: (width * depth) / 144
    width_inches = dimensions.get("width", 0)
    depth_inches = dimensions.get("depth", 0)
    
    return (width_inches * depth_inches) / 144.0


def check_furniture_fit(
    room_area: float,
    furniture_items: List[Dict],
    max_percentage: float = 60.0
) -> Tuple[bool, str, Dict]:
    """
    Check if furniture fits in room with proper circulation space
    
    Args:
        room_area: Room area in square feet
        furniture_items: List of furniture items with dimensions
        max_percentage: Maximum % of room that furniture can occupy
        
    Returns:
        Tuple of (fits: bool, message: str, details: dict)
    """
    # Calculate total furniture area
    total_furniture_area = sum(
        item.get("sqft", 0) for item in furniture_items
    )
    
    # Calculate usage percentage
    usage_percentage = (total_furniture_area / room_area) * 100
    remaining_percentage = 100 - usage_percentage
    
    # Determine if it fits
    fits = usage_percentage <= max_percentage
    
    # Generate message
    if usage_percentage > 70:
        message = "⚠️ Room is very crowded. Consider removing furniture."
        recommendation = "Remove at least one large item for better circulation."
    elif usage_percentage > 60:
        message = "❌ Too much furniture. Please remove items to proceed."
        recommendation = "Remove furniture until usage is below 60%."
        fits = False
    elif usage_percentage > 50:
        message = "✅ Good furniture placement. Room will be comfortable."
        recommendation = "Optimal furniture arrangement."
    elif usage_percentage > 40:
        message = "✅ Excellent! Plenty of space for movement."
        recommendation = "Great balance of furniture and open space."
    else:
        message = "✅ Very spacious. You can add more furniture if desired."
        recommendation = "Consider adding accent pieces."
    
    details = {
        "room_area_sqft": round(room_area, 2),
        "furniture_area_sqft": round(total_furniture_area, 2),
        "usage_percentage": round(usage_percentage, 2),
        "remaining_percentage": round(remaining_percentage, 2),
        "max_allowed_percentage": max_percentage,
        "fits": fits,
        "recommendation": recommendation
    }
    
    logger.info(
        f"Fit check: {usage_percentage:.1f}% usage "
        f"({total_furniture_area:.1f}/{room_area:.1f} sq ft) - "
        f"{'✅ FITS' if fits else '❌ TOO MUCH'}"
    )
    
    return fits, message, details


def get_clearance_recommendations(room_type: str) -> Dict[str, float]:
    """
    Get recommended clearance distances for different room types
    
    Args:
        room_type: Type of room
        
    Returns:
        Dictionary with recommended clearances in feet
    """
    clearances = {
        "Living Room Furniture": {
            "walkway": 3.0,  # feet
            "sofa_to_coffee_table": 1.5,
            "sofa_to_wall": 1.0,
            "tv_viewing_distance": 8.0
        },
        "Bedroom Furniture": {
            "walkway": 2.5,
            "bed_to_wall": 1.5,
            "bed_to_dresser": 3.0,
            "door_clearance": 2.5
        },
        "Dining Room Furniture": {
            "walkway": 3.0,
            "chair_pullout": 2.5,
            "table_to_wall": 3.0,
            "buffet_clearance": 3.0
        },
        "Kitchen": {
            "walkway": 3.5,
            "work_triangle": 4.0,
            "cabinet_clearance": 2.5,
            "island_clearance": 3.5
        },
        "Home Office Furniture": {
            "walkway": 2.5,
            "desk_to_wall": 2.0,
            "chair_pullout": 2.5,
            "bookshelf_clearance": 1.5
        }
    }
    
    return clearances.get(room_type, {
        "walkway": 3.0,
        "general_clearance": 2.0
    })


def convert_inches_to_feet(inches: float) -> float:
    """Convert inches to feet"""
    return inches / 12.0


def convert_feet_to_inches(feet: float) -> float:
    """Convert feet to inches"""
    return feet * 12.0


def format_dimensions(dimensions: Dict[str, float], unit: str = "inches") -> str:
    """
    Format dimensions as a readable string
    
    Args:
        dimensions: Dictionary with width, depth, height
        unit: Unit of measurement
        
    Returns:
        Formatted string like "84\" W × 36\" D × 34\" H"
    """
    width = dimensions.get("width", 0)
    depth = dimensions.get("depth", 0)
    height = dimensions.get("height", 0)
    
    if unit == "inches":
        return f'{width}" W × {depth}" D × {height}" H'
    else:
        return f"{width}' W × {depth}' D × {height}' H"