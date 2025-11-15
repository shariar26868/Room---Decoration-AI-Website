"""
AI Image Generation Service - FINAL OPTIMIZED VERSION
======================================================
"""
import replicate
import os
import tempfile
import requests
import logging
from typing import List
from ai_backend.models import FurnitureItem

logger = logging.getLogger(__name__)

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

if not REPLICATE_API_TOKEN:
    logger.error("❌ REPLICATE_API_TOKEN not found in .env file!")
else:
    os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
    logger.info("✅ Replicate API token configured")


def generate_room_with_furniture(
    room_image_bytes: bytes,
    prompt: str,
    theme: str,
    furniture_items: List[FurnitureItem]
) -> str:
    """
    Generate room image with furniture - PRODUCTION READY
    
    Args:
        room_image_bytes: Original room photo
        prompt: User placement instructions
        theme: Design theme
        furniture_items: Selected furniture
    
    Returns:
        Path to generated image (temporary file)
    """
    
    logger.info(f"🎨 AI Image Generation Starting")
    logger.info(f"   Theme: {theme}")
    logger.info(f"   Furniture count: {len(furniture_items)}")
    logger.info(f"   Image size: {len(room_image_bytes) / 1024:.1f} KB")
    
    # Validate API token
    if not REPLICATE_API_TOKEN:
        raise Exception(
            "❌ Replicate API token not configured!\n"
            "Add REPLICATE_API_TOKEN=your_token to .env file\n"
            "Get token from: https://replicate.com/account/api-tokens"
        )
    
    # Save room image to temp file
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_room:
        temp_room.write(room_image_bytes)
        room_image_path = temp_room.name
    
    logger.info(f"📁 Room image saved temporarily")
    
    try:
        # Extract furniture names
        furniture_names = []
        for item in furniture_items[:5]:  # Limit to 5 for better results
            if isinstance(item, dict):
                name = item.get('name', '')
            else:
                name = item.name
            
            if name:
                furniture_names.append(name)
        
        furniture_desc = ", ".join(furniture_names) if furniture_names else "modern furniture"
        
        # Build prompts
        full_prompt = _build_prompt(theme, furniture_desc, prompt)
        negative_prompt = _build_negative_prompt()
        
        logger.info(f"📝 Prompt: {full_prompt[:150]}...")
        logger.info(f"🤖 Calling Replicate API...")
        
        # Open file for API
        with open(room_image_path, "rb") as image_file:
            
            # Try multiple models with fallback
            models = [
                {
                    "id": "adirik/interior-design:1b976f591a902eb9f897c7c7df9a681d6c5ebefbc727a618b64bfc2a109609ad",
                    "name": "Interior Design (Primary)",
                    "params": {
                        "image": image_file,
                        "prompt": full_prompt,
                        "negative_prompt": negative_prompt,
                        "num_inference_steps": 30,
                        "guidance_scale": 7.5,
                        "prompt_strength": 0.75
                    }
                },
                {
                    "id": "jagilley/controlnet-hough:854e8727697a057c525cdb45ab037f64ecca770a1769cc52287c2e56472a247b",
                    "name": "ControlNet Hough (Fallback 1)",
                    "params": {
                        "image": image_file,
                        "prompt": full_prompt,
                        "structure": "hough",
                        "num_outputs": 1
                    }
                },
                {
                    "id": "rossjillian/controlnet:795433b19458d0f4fa172a7ccf93178d2adb1cb8ab2ad6c8faecc48a7c47caa5",
                    "name": "ControlNet Scribble (Fallback 2)",
                    "params": {
                        "image": image_file,
                        "prompt": full_prompt,
                        "num_outputs": 1
                    }
                }
            ]
            
            output = None
            last_error = None
            
            for model in models:
                try:
                    logger.info(f"   🔄 Trying: {model['name']}...")
                    
                    # Reset file pointer
                    image_file.seek(0)
                    
                    # Run model
                    output = replicate.run(model["id"], input=model["params"])
                    
                    if output:
                        logger.info(f"   ✅ Success with: {model['name']}")
                        break
                    
                except Exception as e:
                    last_error = e
                    logger.warning(f"   ⚠️ {model['name']} failed: {str(e)[:100]}")
                    continue
            
            # Check if any model succeeded
            if not output:
                raise Exception(
                    f"❌ All AI models failed to generate image.\n"
                    f"Last error: {str(last_error)}\n"
                    f"Please check your Replicate API token and try again."
                )
        
        # Process output
        if isinstance(output, list):
            if len(output) == 0:
                raise Exception("Model returned empty output")
            output_url = str(output[0])
        else:
            output_url = str(output)
        
        logger.info(f"✅ Image generated successfully")
        logger.info(f"   URL: {output_url[:80]}...")
        
        # Download generated image
        logger.info(f"📥 Downloading generated image...")
        
        response = requests.get(output_url, timeout=120, stream=True)
        response.raise_for_status()
        
        # Read content
        image_content = response.content
        
        if len(image_content) == 0:
            raise Exception("Downloaded image is empty (0 bytes)")
        
        logger.info(f"✅ Downloaded {len(image_content) / 1024:.1f} KB")
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_gen:
            temp_gen.write(image_content)
            generated_path = temp_gen.name
        
        logger.info(f"✅ Generated image saved: {generated_path}")
        
        # Cleanup original room image
        try:
            os.remove(room_image_path)
            logger.debug("🗑️ Temporary room image cleaned")
        except Exception as e:
            logger.warning(f"Could not remove temp file: {e}")
        
        return generated_path
        
    except replicate.exceptions.ReplicateError as e:
        error_msg = str(e)
        logger.error(f"❌ Replicate API Error: {error_msg}")
        
        # Cleanup
        try:
            os.remove(room_image_path)
        except:
            pass
        
        # User-friendly error message
        if "authentication" in error_msg.lower():
            raise Exception(
                "❌ Replicate API authentication failed.\n"
                "Please check your REPLICATE_API_TOKEN in .env file.\n"
                "Get a new token from: https://replicate.com/account/api-tokens"
            )
        elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
            raise Exception(
                "❌ Replicate API quota exceeded.\n"
                "Please check your account at: https://replicate.com/account"
            )
        else:
            raise Exception(f"Replicate API error: {error_msg}")
    
    except requests.RequestException as e:
        logger.error(f"❌ Download failed: {e}")
        try:
            os.remove(room_image_path)
        except:
            pass
        raise Exception(f"Failed to download generated image: {str(e)}")
    
    except Exception as e:
        logger.error(f"❌ Image generation failed: {e}", exc_info=True)
        try:
            os.remove(room_image_path)
        except:
            pass
        raise Exception(f"Image generation failed: {str(e)}")


def _build_prompt(theme: str, furniture_desc: str, user_prompt: str) -> str:
    """
    Build optimized prompt for AI model
    """
    
    theme_styles = {
        "MINIMAL SCANDINAVIAN": "minimalist Scandinavian interior with clean lines, natural wood tones, white walls, bright natural lighting",
        "TIMELESS LUXURY": "luxurious elegant interior with premium materials, sophisticated color palette, ambient lighting",
        "MODERN LIVING": "contemporary modern interior with sleek furniture, neutral colors, professional design",
        "MODERN MEDITERRANEAN": "Mediterranean interior with warm earthy tones, natural textures, bright airy spaces",
        "BOHO ECLECTIC": "bohemian eclectic interior with mixed patterns, warm colorful accents, relaxed atmosphere"
    }
    
    style_desc = theme_styles.get(theme.upper(), "modern contemporary interior design")
    
    # Optimized prompt structure
    prompt = f"""Professional interior design photograph in {style_desc}.

Furniture to place: {furniture_desc}.

Placement instructions: {user_prompt}.

Style requirements: High quality, photorealistic, 4K resolution, realistic lighting and shadows, 
preserve original room layout and structure, magazine-quality interior design photography, 
professional composition, natural colors."""
    
    return prompt.strip()


def _build_negative_prompt() -> str:
    """
    Build negative prompt to avoid unwanted elements
    """
    return """blurry, distorted, cartoon, anime, unrealistic, low quality, bad lighting, 
oversaturated, cluttered, messy, unprofessional, amateur, ugly, deformed, distorted perspective,
watermark, text, signature, logo, grainy, pixelated, noise, artifacts, out of focus, 
poor composition, bad perspective, multiple rooms, structural changes, people, animals, 
doors changes, window changes, wall removal""".strip()