"""
Configuration Module
====================

Contains all application configuration including:
- Environment variables
- Design themes and their websites
- Room types
- Application constants
"""

import os
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing"""
    pass


def get_env_variable(var_name: str, required: bool = True) -> str:
    """
    Get environment variable with validation
    
    Args:
        var_name: Name of the environment variable
        required: Whether the variable is required
        
    Returns:
        Value of the environment variable
        
    Raises:
        ConfigurationError: If required variable is missing
    """
    value = os.getenv(var_name)
    
    if required and not value:
        raise ConfigurationError(
            f"❌ Missing required environment variable: {var_name}\n"
            f"Please set it in your .env file"
        )
    
    return value or ""


# ===================================================================
# Environment Variables
# ===================================================================
try:
    REPLICATE_API_TOKEN = get_env_variable("REPLICATE_API_TOKEN")
    AWS_ACCESS_KEY_ID = get_env_variable("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = get_env_variable("AWS_SECRET_ACCESS_KEY")
    AWS_S3_BUCKET = get_env_variable("AWS_S3_BUCKET")
    AWS_REGION = get_env_variable("AWS_REGION")
    
    print("✅ All environment variables loaded successfully")
    
except ConfigurationError as e:
    print(str(e))
    print("\n💡 Please check your .env file and ensure all required variables are set")
    exit(1)


# ===================================================================
# Design Themes with Associated Websites
# ===================================================================
THEMES: Dict[str, List[str]] = {
    "MINIMAL SCANDINAVIAN": [
        "https://ethnicraft.com/",
        "https://kavehome.com/",
        "https://www.nordicnest.com/",
        "https://nordicknots.com/",
        "https://swyfthome.com/",
        "https://www.boconcept.com/",
        "https://www.zarahome.com/",
        "https://fermliving.com/",
        "https://www.heals.com/"
    ],
    "TIMELESS LUXURY": [
        "https://rh.com/",
        "https://nordicknots.com/",
        "https://www.eichholtz.com/",
        "https://loaf.com/",
        "https://portaromana.com/",
        "https://www.starkcarpet.com/",
        "https://www.cultfurniture.com/",
        "https://www.dusk.com/",
        "https://www.oka.com/",
        "https://www.pooky.com/",
        "https://www.radilum.com/",
        "https://www.kavehome.com/"
    ],
    "MODERN LIVING": [
        "https://www.liangandeimil.com/",
        "https://www.eichholtz.com/",
        "https://www.gillmorespace.com/",
        "https://nordicknots.com/",
        "https://www.cultfurniture.com/",
        "https://www.sohohome.com/",
        "https://www.swooneditions.com/",
        "https://fermliving.com/",
        "https://www.heals.com/",
        "https://www2.hm.com/",
        "https://www.made.com/",
        "https://www.radilum.com/",
        "https://www.ligne-roset.com/",
        "https://loopandtwist.com/",
        "https://www.themasie.com/",
        "https://www.kavehome.com/"
    ],
    "MODERN MEDITERRANEAN": [
        "https://www.zarahome.com/",
        "https://loopandtwist.com/",
        "https://rh.com/",
        "https://swyfthome.com/",
        "https://nordicknots.com/",
        "https://www.kavehome.com/"
    ],
    "BOHO ECLECTIC": [
        "https://www.themasie.com/",
        "https://www.sklum.com/",
        "https://loopandtwist.com/",
        "https://www.dusk.com/",
        "https://www.cultfurniture.com/",
        "https://www.heals.com/",
        "https://www.kavehome.com/",
        "https://www.perchandparrow.com/"
    ]
}


# ===================================================================
# Room Types
# ===================================================================
ROOM_TYPES: List[str] = [
    "Living Room Furniture",
    "Bedroom Furniture",
    "Dining Room Furniture",
    "Kitchen",
    "Home Office Furniture",
    "Balcony Furniture",
    "Kids Room Furniture",
    "Study Room",
    "Guest Bedroom"
]


# ===================================================================
# Application Constants
# ===================================================================
MAX_IMAGE_SIZE_MB = 10
MAX_FURNITURE_PERCENTAGE = 60  # Max % of room that furniture can occupy
MIN_CIRCULATION_SPACE = 40  # Min % of room for walking space

# Session expiry (in seconds)
SESSION_EXPIRY = 3600  # 1 hour

# Search result limits
MAX_FURNITURE_RESULTS = 20
MAX_FURNITURE_PER_TYPE = 5

# Image generation settings
DEFAULT_IMAGE_STRENGTH = 0.65  # How much to preserve original room (0-1)
DEFAULT_GUIDANCE_SCALE = 7.5
DEFAULT_INFERENCE_STEPS = 40