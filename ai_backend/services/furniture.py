# """
# Furniture Search Service
# ========================

# Handles web scraping and furniture search from theme websites.
# """

# import requests
# from bs4 import BeautifulSoup
# from typing import List, Dict, Optional
# import logging
# import random
# import time
# import json
# from pathlib import Path
# from ai_backend.models import FurnitureItem
# from ai_backend.config import THEMES, MAX_FURNITURE_RESULTS

# logger = logging.getLogger(__name__)

# # Load furniture data
# FURNITURE_DATA_PATH = Path(__file__).parent.parent / "data" / "furniture_data.json"

# try:
#     with open(FURNITURE_DATA_PATH, "r") as f:
#         FURNITURE_DATA = json.load(f)
#     logger.info("Furniture dimensions loaded from database")
# except Exception as e:
#     logger.error(f"Failed to load furniture data: {e}")
#     FURNITURE_DATA = {}


# # ===================================================================
# # Main Search Function
# # ===================================================================
# def search_furniture_on_websites(
#     theme: str,
#     room_type: str,
#     furniture_types: List[str],
#     min_price: float,
#     max_price: float
# ) -> List[FurnitureItem]:
#     """
#     Search furniture on theme websites
    
#     Args:
#         theme: Design theme (e.g., "MINIMAL SCANDINAVIAN")
#         room_type: Room type (e.g., "Living Room Furniture")
#         furniture_types: List of furniture types (e.g., ["Sofa", "Coffee Table"])
#         min_price: Minimum price in USD
#         max_price: Maximum price in USD
    
#     Returns:
#         List of FurnitureItem objects
#     """
    
#     logger.info(f"Searching furniture: {theme} / {room_type}")
#     logger.info(f"   Furniture types: {furniture_types}")
#     logger.info(f"   Price range: ${min_price} - ${max_price}")
    
#     # Get websites for theme
#     websites = THEMES.get(theme.upper(), [])
    
#     if not websites:
#         logger.warning(f"No websites found for theme: {theme}")
#         return _generate_mock_furniture(furniture_types, min_price, max_price, websites, room_type)
    
#     all_results = []
    
#     # Try to scrape each website
#     for website in websites:
#         domain = _extract_domain(website)
        
#         logger.info(f"   Attempting to scrape {domain}...")
        
#         try:
#             # Get scraper for this domain
#             scraper = _get_scraper_for_domain(domain)
            
#             if scraper:
#                 for furniture_type in furniture_types:
#                     results = scraper(website, furniture_type, min_price, max_price, room_type)
#                     all_results.extend(results)
                    
#                     if len(all_results) >= MAX_FURNITURE_RESULTS:
#                         break
                    
#                     # Polite delay between requests
#                     time.sleep(1)
#             else:
#                 # Try generic scraper as fallback
#                 logger.debug(f"   No specific scraper for {domain}, trying generic scraper")
#                 for furniture_type in furniture_types:
#                     results = _scrape_generic(website, furniture_type, min_price, max_price, room_type)
#                     all_results.extend(results)
                    
#                     if len(all_results) >= MAX_FURNITURE_RESULTS:
#                         break
        
#         except Exception as e:
#             logger.error(f"   Scraping failed for {domain}: {e}")
#             continue
        
#         # Stop if we have enough results
#         if len(all_results) >= MAX_FURNITURE_RESULTS:
#             break
    
#     # If no results from scraping, generate realistic mock data
#     if not all_results:
#         logger.info("   No real results found, generating enhanced mock data")
#         all_results = _generate_mock_furniture(furniture_types, min_price, max_price, websites, room_type)
    
#     # Filter by price range
#     filtered = [
#         item for item in all_results
#         if min_price <= item.price <= max_price
#     ]
    
#     # Sort by price
#     filtered.sort(key=lambda x: x.price)
    
#     # Return top results
#     final_results = filtered[:MAX_FURNITURE_RESULTS]
    
#     logger.info(f"Returning {len(final_results)} furniture items")
    
#     return final_results


# # ===================================================================
# # Helper Functions
# # ===================================================================
# def _extract_domain(url: str) -> str:
#     """Extract domain from URL"""
#     domain = url.replace("https://", "").replace("http://", "").replace("www.", "")
#     return domain.split("/")[0].rstrip("/")


# def _get_scraper_for_domain(domain: str):
#     """
#     Get scraper function for a domain
    
#     Returns None if no specific scraper implemented
#     """
#     scrapers = {
#         "kavehome.com": _scrape_kavehome,
#         "ethnicraft.com": _scrape_ethnicraft,
#         "nordicnest.com": _scrape_nordicnest,
#     }
    
#     return scrapers.get(domain)


# def _get_real_dimensions(furniture_type: str, room_type: str, subtype: Optional[str] = None) -> Dict[str, float]:
#     """
#     Get REAL dimensions from furniture_data.json
    
#     Args:
#         furniture_type: Type of furniture (e.g., "Sofa", "Bed")
#         room_type: Room type (e.g., "Living Room Furniture")
#         subtype: Optional specific subtype (e.g., "3-Seater Sofa")
    
#     Returns:
#         Dictionary with width, depth, height in inches
#     """
#     try:
#         # Get furniture data for room type
#         room_furniture = FURNITURE_DATA.get(room_type, {})
        
#         # Get all subtypes for this furniture type
#         furniture_subtypes = room_furniture.get(furniture_type, {})
        
#         if not furniture_subtypes:
#             logger.debug(f"No dimensions found for {furniture_type} in {room_type}")
#             return _get_fallback_dimensions(furniture_type)
        
#         # If specific subtype requested, return that
#         if subtype and subtype in furniture_subtypes:
#             return furniture_subtypes[subtype]
        
#         # Otherwise, return first available subtype (most common)
#         first_subtype = next(iter(furniture_subtypes.values()))
#         return first_subtype
        
#     except Exception as e:
#         logger.debug(f"Error getting dimensions: {e}")
#         return _get_fallback_dimensions(furniture_type)


# def _get_fallback_dimensions(furniture_type: str) -> Dict[str, float]:
#     """
#     Fallback dimensions if not found in database
    
#     Only used as last resort
#     """
#     dimension_map = {
#         "Sofa": {"width": 84, "depth": 36, "height": 34},
#         "Bed": {"width": 60, "depth": 80, "height": 25},
#         "Dining Table": {"width": 60, "depth": 36, "height": 30},
#         "Coffee Table": {"width": 48, "depth": 24, "height": 18},
#         "Nightstand": {"width": 20, "depth": 18, "height": 24},
#         "Dresser": {"width": 60, "depth": 20, "height": 34},
#         "Desk": {"width": 48, "depth": 24, "height": 30},
#         "Bookshelf": {"width": 36, "depth": 12, "height": 72},
#         "Chair": {"width": 24, "depth": 24, "height": 36},
#         "Armchair": {"width": 36, "depth": 36, "height": 34},
#         "TV Stand": {"width": 48, "depth": 18, "height": 22},
#     }
    
#     # Try exact match
#     if furniture_type in dimension_map:
#         return dimension_map[furniture_type]
    
#     # Try partial match
#     for key in dimension_map:
#         if key.lower() in furniture_type.lower():
#             return dimension_map[key]
    
#     # Default
#     return {"width": 48, "depth": 24, "height": 30}


# # ===================================================================
# # Generic Web Scraper (Fallback)
# # ===================================================================
# def _scrape_generic(
#     website: str,
#     furniture_type: str,
#     min_price: float,
#     max_price: float,
#     room_type: str
# ) -> List[FurnitureItem]:
#     """
#     Generic scraper that attempts to find furniture on any website
    
#     This is a best-effort scraper that looks for common HTML patterns
#     """
#     results = []
    
#     try:
#         # Build search URL (try common patterns)
#         search_query = furniture_type.lower().replace(" ", "+")
#         search_urls = [
#             f"{website.rstrip('/')}/search?q={search_query}",
#             f"{website.rstrip('/')}/search/{search_query}",
#             f"{website.rstrip('/')}/products?search={search_query}",
#         ]
        
#         headers = {
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#             "Accept-Language": "en-US,en;q=0.5",
#         }
        
#         products = []
        
#         # Try each URL pattern
#         for search_url in search_urls:
#             try:
#                 response = requests.get(search_url, headers=headers, timeout=10)
#                 if response.status_code == 200:
#                     soup = BeautifulSoup(response.text, 'html.parser')
                    
#                     # Try common product container patterns
#                     product_selectors = [
#                         {'name': 'div', 'class': 'product'},
#                         {'name': 'div', 'class': 'product-item'},
#                         {'name': 'div', 'class': 'product-card'},
#                         {'name': 'article', 'class': 'product'},
#                         {'name': 'li', 'class': 'product'},
#                     ]
                    
#                     for selector in product_selectors:
#                         products = soup.find_all(
#                             selector['name'],
#                             class_=lambda x: x and selector['class'] in x.lower() if x else False
#                         )
#                         if products:
#                             logger.debug(f"   Found {len(products)} products using generic scraper")
#                             break
                    
#                     if products:
#                         break
#             except:
#                 continue
        
#         # Parse found products
#         for product in products[:5]:
#             try:
#                 name = None
#                 link = None
#                 price_text = None
#                 image = None
                
#                 # Find name
#                 for tag in ['h2', 'h3', 'h4', 'p']:
#                     name_elem = product.find(
#                         tag,
#                         class_=lambda x: x and ('title' in x.lower() or 'name' in x.lower()) if x else False
#                     )
#                     if name_elem:
#                         name = name_elem.text.strip()
#                         break
                
#                 # Find link
#                 link_elem = product.find('a', href=True)
#                 if link_elem:
#                     link = link_elem['href']
                
#                 # Find price
#                 price_elem = product.find(
#                     class_=lambda x: x and 'price' in x.lower() if x else False
#                 )
#                 if price_elem:
#                     price_text = price_elem.text.strip()
                
#                 # Find image
#                 img_elem = product.find('img', src=True)
#                 if img_elem:
#                     image = img_elem.get('src') or img_elem.get('data-src')
                
#                 if not all([name, price_text]):
#                     continue
                
#                 # Parse price
#                 import re
#                 price_numbers = re.findall(r'\d+\.?\d*', price_text.replace(',', ''))
#                 if not price_numbers:
#                     continue
#                 price = float(price_numbers[0])
                
#                 if not (min_price <= price <= max_price):
#                     continue
                
#                 # Make URLs absolute
#                 if link and not link.startswith('http'):
#                     link = f"{website.rstrip('/')}/{link.lstrip('/')}"
#                 if image and not image.startswith('http'):
#                     image = f"{website.rstrip('/')}/{image.lstrip('/')}"
                
#                 # Get REAL dimensions from database
#                 dimensions = _get_real_dimensions(furniture_type, room_type)
                
#                 results.append(FurnitureItem(
#                     name=name,
#                     link=link or website,
#                     price=price,
#                     image_url=image or "https://via.placeholder.com/400x300",
#                     dimensions=dimensions,  # ✅ REAL dimensions!
#                     website=_extract_domain(website),
#                     description=f"{name} from {_extract_domain(website)}"
#                 ))
                
#             except Exception as e:
#                 logger.debug(f"   Failed to parse product: {e}")
#                 continue
        
#         return results
        
#     except Exception as e:
#         logger.debug(f"   Generic scraper failed for {website}: {e}")
#         return []


# # ===================================================================
# # Specific Website Scrapers
# # ===================================================================
# def _scrape_kavehome(
#     website: str,
#     furniture_type: str,
#     min_price: float,
#     max_price: float,
#     room_type: str
# ) -> List[FurnitureItem]:
#     """Scrape Kavehome.com for furniture"""
#     results = []
    
#     try:
#         type_map = {
#             "Sofa": "sofas",
#             "Bed": "beds",
#             "Table": "tables",
#             "Chair": "chairs",
#             "Desk": "desks"
#         }
#         search_term = type_map.get(furniture_type, furniture_type.lower().replace(" ", "-"))
#         search_url = f"{website.rstrip('/')}/en/search?q={search_term}"
        
#         headers = {
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
#         }
        
#         response = requests.get(search_url, headers=headers, timeout=10)
#         response.raise_for_status()
        
#         soup = BeautifulSoup(response.text, 'html.parser')
#         products = soup.find_all('div', class_='product-grid__item')
        
#         if not products:
#             products = soup.find_all('div', class_=lambda x: x and 'product' in x.lower() if x else False)
        
#         for product in products[:10]:
#             try:
#                 name_tag = product.find('a', class_='product-card__name')
#                 if not name_tag:
#                     name_tag = product.find(['h2', 'h3', 'h4'])
#                 name = name_tag.text.strip() if name_tag else None
                
#                 price_tag = product.find('span', class_='money')
#                 if not price_tag:
#                     price_tag = product.find(class_=lambda x: x and 'price' in x.lower() if x else False)
#                 price_text = price_tag.text.strip() if price_tag else "0"
                
#                 import re
#                 price_numbers = re.findall(r'\d+\.?\d*', price_text.replace(',', ''))
#                 price = float(price_numbers[0]) if price_numbers else 0
                
#                 link_tag = product.find('a', href=True)
#                 link = link_tag['href'] if link_tag else None
#                 if link and not link.startswith('http'):
#                     link = website.rstrip('/') + '/' + link.lstrip('/')
                
#                 image_tag = product.find('img', src=True)
#                 if not image_tag:
#                     image_tag = product.find('img', attrs={'data-src': True})
#                 image = (image_tag.get('src') or image_tag.get('data-src')) if image_tag else None
#                 if image and not image.startswith('http'):
#                     image = website.rstrip('/') + '/' + image.lstrip('/')
                
#                 if name and link and min_price <= price <= max_price:
#                     # ✅ Get REAL dimensions from database
#                     dimensions = _get_real_dimensions(furniture_type, room_type)
                    
#                     results.append(FurnitureItem(
#                         name=name,
#                         link=link,
#                         price=price,
#                         image_url=image or "https://via.placeholder.com/400x300",
#                         dimensions=dimensions,  # ✅ REAL dimensions!
#                         website="kavehome.com",
#                         description=f"{name} from Kave Home"
#                     ))
            
#             except Exception as e:
#                 logger.debug(f"Failed to parse Kave Home product: {e}")
#                 continue
        
#         return results
    
#     except Exception as e:
#         logger.debug(f"Kave Home scraper failed: {e}")
#         return _scrape_generic(website, furniture_type, min_price, max_price, room_type)


# def _scrape_ethnicraft(
#     website: str,
#     furniture_type: str,
#     min_price: float,
#     max_price: float,
#     room_type: str
# ) -> List[FurnitureItem]:
#     """Scrape Ethnicraft.com for furniture"""
#     return _scrape_generic(website, furniture_type, min_price, max_price, room_type)


# def _scrape_nordicnest(
#     website: str,
#     furniture_type: str,
#     min_price: float,
#     max_price: float,
#     room_type: str
# ) -> List[FurnitureItem]:
#     """Scrape Nordicnest.com for furniture"""
#     return _scrape_generic(website, furniture_type, min_price, max_price, room_type)


# # ===================================================================
# # Enhanced Mock Data Generator
# # ===================================================================
# def _generate_mock_furniture(
#     furniture_types: List[str],
#     min_price: float,
#     max_price: float,
#     websites: List[str],
#     room_type: str
# ) -> List[FurnitureItem]:
#     """
#     Generate REALISTIC mock furniture data with REAL dimensions
#     """
#     if not websites:
#         websites = ["https://kavehome.com/", "https://ethnicraft.com/"]
    
#     mock_items = []
#     styles = ["Modern", "Contemporary", "Classic", "Minimalist", "Scandinavian", "Industrial"]
#     materials = ["Oak", "Walnut", "Leather", "Velvet", "Linen", "Teak", "Ash Wood"]
    
#     for furn_type in furniture_types:
#         num_items = random.randint(4, 6)
        
#         for i in range(num_items):
#             style = random.choice(styles)
#             material = random.choice(materials)
#             website = random.choice(websites)
#             domain = _extract_domain(website)
            
#             price_range = max_price - min_price
#             price = min_price + (price_range / num_items) * i + random.uniform(-price_range*0.1, price_range*0.1)
#             price = max(min_price, min(max_price, price))
            
#             # ✅ Get REAL dimensions from database
#             dimensions = _get_real_dimensions(furn_type, room_type)
            
#             product_name = f"{style} {material} {furn_type}"
#             product_id = random.randint(1000, 9999)
            
#             mock_items.append(FurnitureItem(
#                 name=product_name,
#                 link=f"{website.rstrip('/')}/products/{furn_type.lower().replace(' ', '-')}-{product_id}",
#                 price=round(price, 2),
#                 image_url=f"https://via.placeholder.com/400x300/e8e8e8/333333?text={furn_type.replace(' ', '+')}",
#                 dimensions=dimensions,  # ✅ REAL dimensions from JSON!
#                 website=domain,
#                 description=f"{product_name} - Premium quality {material.lower()} furniture with {style.lower()} design from {domain}"
#             ))
    
#     return mock_items




# """
# AI-Powered Furniture Search Service
# ====================================

# Uses Claude AI API directly (no anthropic package needed)
# 100% Automatic - No mock data
# """

# import requests
# import json
# import logging
# from typing import List, Dict, Optional
# from pathlib import Path
# from ai_backend.models import FurnitureItem
# from ai_backend.config import THEMES, MAX_FURNITURE_RESULTS

# logger = logging.getLogger(__name__)

# # Load furniture dimensions database
# FURNITURE_DATA_PATH = Path(__file__).parent.parent / "data" / "furniture_data.json"

# try:
#     with open(FURNITURE_DATA_PATH, "r") as f:
#         FURNITURE_DATA = json.load(f)
#     logger.info("✅ Furniture dimensions loaded")
# except Exception as e:
#     logger.error(f"❌ Failed to load furniture data: {e}")
#     FURNITURE_DATA = {}


# # ===================================================================
# # Main Search Function
# # ===================================================================
# def search_furniture_on_websites(
#     theme: str,
#     room_type: str,
#     furniture_types: List[str],
#     min_price: float,
#     max_price: float
# ) -> List[FurnitureItem]:
#     """
#     AI-powered furniture search
    
#     Uses Claude AI to generate realistic furniture recommendations
    
#     Args:
#         theme: Design theme
#         room_type: Room type
#         furniture_types: List of furniture types needed
#         min_price: Minimum price in USD
#         max_price: Maximum price in USD
    
#     Returns:
#         List of FurnitureItem objects (AI-generated, realistic)
#     """
    
#     logger.info(f"🤖 AI Furniture Search")
#     logger.info(f"   Theme: {theme}")
#     logger.info(f"   Room: {room_type}")
#     logger.info(f"   Types: {furniture_types}")
#     logger.info(f"   Price: ${min_price}-${max_price}")
    
#     # Get theme websites
#     websites = THEMES.get(theme.upper(), [])
    
#     try:
#         # Use AI to generate furniture
#         ai_results = _generate_ai_furniture(
#             theme=theme,
#             room_type=room_type,
#             furniture_types=furniture_types,
#             min_price=min_price,
#             max_price=max_price,
#             websites=websites
#         )
        
#         logger.info(f"✅ Generated {len(ai_results)} furniture items")
#         return ai_results
        
#     except Exception as e:
#         logger.error(f"❌ AI furniture generation failed: {e}", exc_info=True)
#         raise Exception(f"Unable to generate furniture: {str(e)}")


# # ===================================================================
# # AI Furniture Generation
# # ===================================================================
# def _generate_ai_furniture(
#     theme: str,
#     room_type: str,
#     furniture_types: List[str],
#     min_price: float,
#     max_price: float,
#     websites: List[str]
# ) -> List[FurnitureItem]:
#     """
#     Use Claude AI to generate realistic furniture
#     """
    
#     # Build AI prompt
#     website_list = ', '.join(websites[:5]) if websites else 'kavehome.com, ethnicraft.com'
    
#     prompt = f"""You are a professional furniture curator for an interior design platform. Generate realistic furniture product listings.

# **Requirements:**
# - Theme: {theme}
# - Room Type: {room_type}
# - Furniture Types: {', '.join(furniture_types)}
# - Price Range: ${min_price} - ${max_price} USD
# - Preferred Websites: {website_list}

# **Task:**
# Generate {len(furniture_types) * 4} realistic furniture products (4 per type) with:
# 1. Realistic product names (include style, material, size)
# 2. Prices distributed across the range
# 3. Product URLs from the websites above
# 4. Brief descriptions (1-2 sentences)
# 5. Variety in styles and price points

# **Examples:**
# - "Scandinavian Oak 3-Seater Sofa" - $749.99
# - "Modern Marble Coffee Table" - $399.00
# - "Industrial Metal Bookshelf" - $289.50

# **Output ONLY valid JSON** (no markdown, no explanation):
# {{
#   "furniture_items": [
#     {{
#       "name": "Product Name",
#       "type": "Furniture Type",
#       "price": 299.99,
#       "website": "domain.com",
#       "link": "https://domain.com/products/product-name-123",
#       "description": "Brief product description"
#     }}
#   ]
# }}"""

#     try:
#         logger.info("   Calling Claude AI API...")
        
#         # Call Claude API directly (no anthropic package needed)
#         response = requests.post(
#             "https://api.anthropic.com/v1/messages",
#             headers={
#                 "Content-Type": "application/json",
#                 "anthropic-version": "2023-06-01"
#             },
#             json={
#                 "model": "claude-sonnet-4-20250514",
#                 "max_tokens": 4000,
#                 "messages": [{"role": "user", "content": prompt}]
#             },
#             timeout=30
#         )
        
#         if response.status_code != 200:
#             logger.error(f"Claude API error: {response.status_code} - {response.text}")
#             raise Exception(f"Claude API returned status {response.status_code}")
        
#         data = response.json()
        
#         # Extract text content
#         if not data.get('content') or len(data['content']) == 0:
#             raise Exception("Empty response from Claude API")
        
#         ai_text = data['content'][0].get('text', '')
        
#         if not ai_text:
#             raise Exception("No text content in AI response")
        
#         logger.info("   ✅ AI response received")
        
#         # Parse JSON from response
#         # Remove markdown code blocks if present
#         ai_text = ai_text.replace('```json', '').replace('```', '').strip()
        
#         # Try to find JSON in the response
#         json_start = ai_text.find('{')
#         json_end = ai_text.rfind('}') + 1
        
#         if json_start == -1 or json_end == 0:
#             raise Exception("No JSON found in AI response")
        
#         json_text = ai_text[json_start:json_end]
        
#         ai_data = json.loads(json_text)
#         furniture_list = ai_data.get('furniture_items', [])
        
#         if not furniture_list:
#             raise Exception("No furniture items in AI response")
        
#         logger.info(f"   AI generated {len(furniture_list)} products")
        
#         # Convert to FurnitureItem objects
#         results = []
#         for item in furniture_list:
#             try:
#                 furniture_type = item.get('type', furniture_types[0])
                
#                 # Get real dimensions from database
#                 dimensions = _get_real_dimensions(furniture_type, room_type)
                
#                 # Validate and clean price
#                 price = float(item.get('price', (min_price + max_price) / 2))
                
#                 # Ensure price is within range
#                 if price < min_price:
#                     price = min_price + (max_price - min_price) * 0.2
#                 elif price > max_price:
#                     price = max_price - (max_price - min_price) * 0.2
                
#                 # Get website domain
#                 website = item.get('website', '')
#                 if not website and websites:
#                     website = _extract_domain(websites[0])
#                 elif not website:
#                     website = 'furniture.com'
                
#                 # Build product link
#                 link = item.get('link', '')
#                 if not link or not link.startswith('http'):
#                     product_slug = item.get('name', 'product').lower().replace(' ', '-')
#                     link = f"https://{website}/products/{product_slug}"
                
#                 # Get description
#                 description = item.get('description', '')
#                 if not description:
#                     description = f"{item.get('name', 'Furniture')} - Professional quality {theme.lower()} style furniture"
                
#                 # Create placeholder image
#                 image_url = f"https://via.placeholder.com/400x300/e8e8e8/333333?text={furniture_type.replace(' ', '+')}"
                
#                 results.append(FurnitureItem(
#                     name=item.get('name', f'{furniture_type}'),
#                     link=link,
#                     price=round(price, 2),
#                     image_url=image_url,
#                     dimensions=dimensions,
#                     website=website,
#                     description=description[:200]  # Limit length
#                 ))
                
#             except Exception as e:
#                 logger.debug(f"Failed to parse furniture item: {e}")
#                 continue
        
#         if not results:
#             raise Exception("No valid furniture items after parsing")
        
#         # Filter by price range (double check)
#         filtered = [item for item in results if min_price <= item.price <= max_price]
        
#         if not filtered:
#             # If all filtered out, use results anyway
#             filtered = results
        
#         # Sort by price
#         filtered.sort(key=lambda x: x.price)
        
#         # Return up to MAX_FURNITURE_RESULTS
#         return filtered[:MAX_FURNITURE_RESULTS]
        
#     except json.JSONDecodeError as e:
#         logger.error(f"Failed to parse AI JSON: {e}")
#         logger.debug(f"AI Response (first 500 chars): {ai_text[:500]}")
#         raise Exception("AI generated invalid JSON format")
#     except requests.RequestException as e:
#         logger.error(f"API request failed: {e}")
#         raise Exception("Failed to connect to AI service")
#     except Exception as e:
#         logger.error(f"AI generation error: {e}", exc_info=True)
#         raise


# # ===================================================================
# # Helper Functions
# # ===================================================================
# def _extract_domain(url: str) -> str:
#     """Extract domain from URL"""
#     domain = url.replace("https://", "").replace("http://", "").replace("www.", "")
#     return domain.split("/")[0].rstrip("/")


# def _get_real_dimensions(furniture_type: str, room_type: str) -> Dict[str, float]:
#     """Get real dimensions from database"""
#     try:
#         room_furniture = FURNITURE_DATA.get(room_type, {})
#         furniture_subtypes = room_furniture.get(furniture_type, {})
        
#         if furniture_subtypes:
#             # Return first available subtype dimensions
#             return next(iter(furniture_subtypes.values()))
        
#         return _get_fallback_dimensions(furniture_type)
        
#     except Exception:
#         return _get_fallback_dimensions(furniture_type)


# def _get_fallback_dimensions(furniture_type: str) -> Dict[str, float]:
#     """Industry standard dimensions"""
#     standards = {
#         "Sofa": {"width": 84, "depth": 36, "height": 34},
#         "Sectional Sofa": {"width": 120, "depth": 84, "height": 34},
#         "Loveseat": {"width": 60, "depth": 36, "height": 34},
#         "Armchair": {"width": 36, "depth": 36, "height": 34},
#         "Recliner": {"width": 35, "depth": 40, "height": 40},
#         "Ottoman": {"width": 30, "depth": 20, "height": 18},
#         "Coffee Table": {"width": 48, "depth": 24, "height": 18},
#         "Side Table": {"width": 24, "depth": 24, "height": 24},
#         "Console Table": {"width": 48, "depth": 14, "height": 30},
#         "TV Stand": {"width": 60, "depth": 18, "height": 24},
#         "Bookshelf": {"width": 36, "depth": 12, "height": 72},
#         "Bed": {"width": 60, "depth": 80, "height": 25},
#         "Queen Bed": {"width": 60, "depth": 80, "height": 25},
#         "King Bed": {"width": 76, "depth": 80, "height": 25},
#         "Nightstand": {"width": 20, "depth": 18, "height": 24},
#         "Dresser": {"width": 60, "depth": 20, "height": 34},
#         "Wardrobe": {"width": 48, "depth": 24, "height": 72},
#         "Dining Table": {"width": 60, "depth": 36, "height": 30},
#         "Dining Chair": {"width": 18, "depth": 22, "height": 36},
#         "Bar Stool": {"width": 16, "depth": 16, "height": 30},
#         "Bench": {"width": 48, "depth": 16, "height": 18},
#         "Desk": {"width": 48, "depth": 24, "height": 30},
#         "Office Chair": {"width": 26, "depth": 26, "height": 38},
#         "Filing Cabinet": {"width": 15, "depth": 28, "height": 52},
#     }
    
#     # Try exact match
#     if furniture_type in standards:
#         return standards[furniture_type]
    
#     # Try partial match
#     for key, dims in standards.items():
#         if key.lower() in furniture_type.lower() or furniture_type.lower() in key.lower():
#             return dims
    
#     # Default medium-sized furniture
#     return {"width": 48, "depth": 24, "height": 30}



"""
AI-Powered Furniture Search Service (OpenAI GPT Version)
=========================================================

Uses OpenAI ChatGPT API with real images from Unsplash
"""

import requests
import json
import logging
import os
from typing import List, Dict
from pathlib import Path
from ai_backend.models import FurnitureItem
from ai_backend.config import THEMES, MAX_FURNITURE_RESULTS

logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Get OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    logger.error("❌ OPENAI_API_KEY not found in environment variables!")

# Load furniture dimensions database
FURNITURE_DATA_PATH = Path(__file__).parent.parent / "data" / "furniture_data.json"

try:
    with open(FURNITURE_DATA_PATH, "r") as f:
        FURNITURE_DATA = json.load(f)
    logger.info("✅ Furniture dimensions loaded")
except Exception as e:
    logger.error(f"❌ Failed to load furniture data: {e}")
    FURNITURE_DATA = {}


# ===================================================================
# Main Search Function
# ===================================================================
def search_furniture_on_websites(
    theme: str,
    room_type: str,
    furniture_types: List[str],
    min_price: float,
    max_price: float
) -> List[FurnitureItem]:
    """
    AI-powered furniture search using OpenAI GPT
    
    Args:
        theme: Design theme
        room_type: Room type
        furniture_types: List of furniture types needed
        min_price: Minimum price in USD
        max_price: Maximum price in USD
    
    Returns:
        List of FurnitureItem objects (AI-generated, realistic)
    """
    
    logger.info(f"🤖 AI Furniture Search (OpenAI GPT)")
    logger.info(f"   Theme: {theme}")
    logger.info(f"   Room: {room_type}")
    logger.info(f"   Types: {furniture_types}")
    logger.info(f"   Price: ${min_price}-${max_price}")
    
    # Get theme websites
    websites = THEMES.get(theme.upper(), [])
    
    try:
        # Use AI to generate furniture
        ai_results = _generate_ai_furniture(
            theme=theme,
            room_type=room_type,
            furniture_types=furniture_types,
            min_price=min_price,
            max_price=max_price,
            websites=websites
        )
        
        logger.info(f"✅ Generated {len(ai_results)} furniture items")
        return ai_results
        
    except Exception as e:
        logger.error(f"❌ AI furniture generation failed: {e}", exc_info=True)
        raise Exception(f"Unable to generate furniture: {str(e)}")


# ===================================================================
# Helper Functions
# ===================================================================
def _extract_domain(url: str) -> str:
    """Extract domain from URL"""
    domain = url.replace("https://", "").replace("http://", "").replace("www.", "")
    return domain.split("/")[0].rstrip("/")


def _get_furniture_image(furniture_type: str, furniture_name: str = "") -> str:
    """
    Get real furniture image from Unsplash
    
    Args:
        furniture_type: Type of furniture (e.g., "Sofa", "Coffee Table")
        furniture_name: Full product name for better matching
    
    Returns:
        Real image URL from Unsplash
    """
    try:
        # Map furniture types to best search keywords
        keyword_map = {
            # Seating
            'sofa': 'modern-sofa',
            'couch': 'living-room-couch',
            'sectional': 'sectional-sofa',
            'loveseat': 'loveseat-sofa',
            'chair': 'armchair',
            'armchair': 'comfortable-armchair',
            'recliner': 'recliner-chair',
            'dining chair': 'dining-chair',
            'office chair': 'office-chair',
            'accent chair': 'accent-chair',
            'bench': 'wooden-bench',
            'stool': 'bar-stool',
            'ottoman': 'ottoman-footstool',
            
            # Tables
            'coffee table': 'modern-coffee-table',
            'table': 'wooden-table',
            'dining table': 'dining-table',
            'side table': 'side-table',
            'end table': 'end-table',
            'console table': 'console-table',
            'desk': 'modern-desk',
            'nightstand': 'bedside-table',
            
            # Bedroom
            'bed': 'modern-bedroom',
            'queen bed': 'queen-size-bed',
            'king bed': 'king-size-bed',
            'dresser': 'bedroom-dresser',
            'wardrobe': 'wardrobe-closet',
            'chest': 'chest-of-drawers',
            
            # Storage
            'bookshelf': 'modern-bookshelf',
            'shelf': 'wall-shelf',
            'cabinet': 'storage-cabinet',
            'tv stand': 'tv-console',
            'media console': 'media-cabinet',
            'sideboard': 'sideboard-buffet',
            'buffet': 'dining-buffet'
        }
        
        # Find best matching keyword
        search_term = 'modern-furniture'
        furniture_lower = furniture_type.lower()
        
        # Try exact match first
        if furniture_lower in keyword_map:
            search_term = keyword_map[furniture_lower]
        else:
            # Try partial match
            for key, value in keyword_map.items():
                if key in furniture_lower or furniture_lower in key:
                    search_term = value
                    break
        
        # Use Unsplash Source API (no authentication needed)
        # Format: https://source.unsplash.com/WIDTHxHEIGHT/?keyword1,keyword2
        image_url = f"https://source.unsplash.com/600x400/?{search_term},interior,minimalist"
        
        logger.debug(f"   Image for {furniture_type}: {image_url}")
        return image_url
        
    except Exception as e:
        logger.debug(f"Failed to generate image URL: {e}")
        # Fallback to placehold.co (working alternative)
        return f"https://placehold.co/600x400/e8e8e8/666666/png?text={furniture_type.replace(' ', '+')}"


def _get_real_dimensions(furniture_type: str, room_type: str) -> Dict[str, float]:
    """
    Get REAL dimensions from furniture_data.json ONLY
    
    Args:
        furniture_type: Type of furniture (e.g., "Sofa", "Bed")
        room_type: Room type (e.g., "Living Room Furniture")
    
    Returns:
        Dictionary with width, depth, height in inches from JSON database
    """
    try:
        # Try to get from JSON database first
        room_furniture = FURNITURE_DATA.get(room_type, {})
        furniture_subtypes = room_furniture.get(furniture_type, {})
        
        if furniture_subtypes:
            # Return first available subtype dimensions from JSON
            dimensions = next(iter(furniture_subtypes.values()))
            logger.debug(f"✅ Found dimensions for {furniture_type} in {room_type}: {dimensions}")
            return dimensions
        
        # If not found, search in ALL room types
        logger.debug(f"⚠️ {furniture_type} not found in {room_type}, searching all rooms...")
        
        for room, furnitures in FURNITURE_DATA.items():
            if furniture_type in furnitures:
                dimensions = next(iter(furnitures[furniture_type].values()))
                logger.debug(f"✅ Found {furniture_type} in {room}: {dimensions}")
                return dimensions
        
        # If still not found, log error and use generic dimensions
        logger.warning(f"❌ No dimensions found for {furniture_type} in furniture_data.json!")
        logger.warning(f"📝 Please add {furniture_type} to your furniture_data.json file")
        
        # Return generic medium furniture as absolute fallback
        return {"width": 48, "depth": 24, "height": 30}
        
    except Exception as e:
        logger.error(f"Error reading dimensions: {e}")
        return {"width": 48, "depth": 24, "height": 30}


# ===================================================================
# AI Furniture Generation (OpenAI GPT)
# ===================================================================
def _generate_ai_furniture(
    theme: str,
    room_type: str,
    furniture_types: List[str],
    min_price: float,
    max_price: float,
    websites: List[str]
) -> List[FurnitureItem]:
    """
    Use OpenAI ChatGPT to generate realistic furniture
    """
    
    # Check API key
    if not OPENAI_API_KEY:
        raise Exception("OpenAI API key not configured. Add OPENAI_API_KEY to .env file")
    
    # Build AI prompt
    website_list = ', '.join(websites[:5]) if websites else 'kavehome.com, ethnicraft.com'
    
    prompt = f"""You are a professional furniture curator for an interior design platform. Generate realistic furniture product listings.

**Requirements:**
- Theme: {theme}
- Room Type: {room_type}
- Furniture Types: {', '.join(furniture_types)}
- Price Range: ${min_price} - ${max_price} USD
- Preferred Websites: {website_list}

**Task:**
Generate {len(furniture_types) * 4} realistic furniture products (4 per type) with:
1. Realistic product names (include style, material, size)
2. Prices distributed across the range
3. Brief descriptions (1-2 sentences)
4. Variety in styles and price points

**Examples:**
- "Scandinavian Oak 3-Seater Sofa" - $749.99
- "Modern Marble Coffee Table" - $399.00
- "Industrial Metal Bookshelf" - $289.50

**IMPORTANT:** Generate product names ONLY. Do not include URLs or website names in the output.

**Output ONLY valid JSON** (no markdown, no explanation):
{{
  "furniture_items": [
    {{
      "name": "Product Name",
      "type": "Furniture Type",
      "price": 299.99,
      "description": "Brief product description"
    }}
  ]
}}"""

    try:
        logger.info("   Calling OpenAI ChatGPT API...")
        
        # Call OpenAI API
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a furniture expert. Always respond with valid JSON only. Never include URLs in product data."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 3000
            },
            timeout=30
        )
        
        if response.status_code != 200:
            logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
            raise Exception(f"OpenAI API returned status {response.status_code}")
        
        data = response.json()
        
        # Extract text content
        if not data.get('choices') or len(data['choices']) == 0:
            raise Exception("Empty response from OpenAI API")
        
        ai_text = data['choices'][0]['message']['content']
        
        if not ai_text:
            raise Exception("No text content in AI response")
        
        logger.info("   ✅ AI response received")
        
        # Parse JSON from response
        ai_text = ai_text.replace('```json', '').replace('```', '').strip()
        
        # Find JSON in response
        json_start = ai_text.find('{')
        json_end = ai_text.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            raise Exception("No JSON found in AI response")
        
        json_text = ai_text[json_start:json_end]
        ai_data = json.loads(json_text)
        furniture_list = ai_data.get('furniture_items', [])
        
        if not furniture_list:
            raise Exception("No furniture items in AI response")
        
        logger.info(f"   AI generated {len(furniture_list)} products")
        
        # Convert to FurnitureItem objects
        results = []
        for item in furniture_list:
            try:
                furniture_type = item.get('type', furniture_types[0])
                product_name = item.get('name', f'{furniture_type}')
                
                # Get real dimensions from database
                dimensions = _get_real_dimensions(furniture_type, room_type)
                
                # Validate and clean price
                price = float(item.get('price', (min_price + max_price) / 2))
                
                # Ensure price is within range
                if price < min_price:
                    price = min_price + (max_price - min_price) * 0.2
                elif price > max_price:
                    price = max_price - (max_price - min_price) * 0.2
                
                # Get website domain (randomly from list)
                if websites:
                    import random
                    website_url = random.choice(websites)
                    website = _extract_domain(website_url)
                else:
                    website = 'furniture.com'
                    website_url = 'https://furniture.com'
                
                # Build link to category page (real, working link)
                category_links = {
                    'sofa': 'sofas',
                    'couch': 'sofas',
                    'sectional': 'sofas',
                    'loveseat': 'sofas',
                    'chair': 'chairs',
                    'armchair': 'chairs',
                    'dining chair': 'dining-chairs',
                    'coffee table': 'coffee-tables',
                    'table': 'tables',
                    'dining table': 'dining-tables',
                    'side table': 'tables',
                    'desk': 'desks',
                    'bed': 'beds',
                    'nightstand': 'bedroom',
                    'dresser': 'bedroom',
                    'bookshelf': 'storage',
                    'cabinet': 'storage',
                    'tv stand': 'living-room'
                }
                
                category = 'furniture'
                furniture_lower = furniture_type.lower()
                for key, cat in category_links.items():
                    if key in furniture_lower:
                        category = cat
                        break
                
                link = f"{website_url.rstrip('/')}/{category}"
                
                # Get description
                description = item.get('description', '')
                if not description:
                    description = f"{product_name} - Professional quality {theme.lower()} style furniture"
                
                # Get REAL image from Unsplash
                image_url = _get_furniture_image(furniture_type, product_name)
                
                results.append(FurnitureItem(
                    name=product_name,
                    link=link,
                    price=round(price, 2),
                    image_url=image_url,
                    dimensions=dimensions,
                    website=website,
                    description=description[:200]
                ))
                
            except Exception as e:
                logger.debug(f"Failed to parse furniture item: {e}")
                continue
        
        if not results:
            raise Exception("No valid furniture items after parsing")
        
        # Filter by price range
        filtered = [item for item in results if min_price <= item.price <= max_price]
        
        if not filtered:
            filtered = results
        
        # Sort by price
        filtered.sort(key=lambda x: x.price)
        
        # Return up to MAX_FURNITURE_RESULTS
        return filtered[:MAX_FURNITURE_RESULTS]
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI JSON: {e}")
        raise Exception("AI generated invalid JSON format")
    except requests.RequestException as e:
        logger.error(f"API request failed: {e}")
        raise Exception("Failed to connect to AI service")
    except Exception as e:
        logger.error(f"AI generation error: {e}", exc_info=True)
        raise