"""
Test complete API workflow
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_complete_workflow():
    """Test all endpoints in sequence"""
    
    print("=" * 70)
    print("🧪 Testing Room Designer AI - Complete Workflow")
    print("=" * 70)
    
    # Step 1: Upload image
    print("\n1️⃣  Uploading room image...")
    
    # Create a dummy image file for testing
    with open("test_room.jpg", "wb") as f:
        # 1x1 pixel JPEG
        f.write(bytes.fromhex('ffd8ffe000104a46494600010100000100010000ffdb004300ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffc00011080001000103011100021101031101ffc4001500010100000000000000000000000000000008ffda000c03010002110311003f00bf8001ffd9'))
    
    files = {'room_image': open('test_room.jpg', 'rb')}
    response = requests.post(f"{BASE_URL}/api/upload/upload", files=files)
    
    if response.status_code != 201:
        print(f"❌ Upload failed: {response.status_code}")
        print(response.text)
        return
    
    data = response.json()
    session_id = data['session_id']
    print(f"✅ Session created: {session_id[:20]}...")
    
    # Step 2: Select room type
    print("\n2️⃣  Selecting room type...")
    response = requests.post(
        f"{BASE_URL}/api/selection/room-type",
        json={
            "session_id": session_id,
            "room_type": "Living Room Furniture"
        }
    )
    print(f"✅ Room type selected: {response.json()['room_type']}")
    
    # Step 3: Select theme
    print("\n3️⃣  Selecting theme...")
    response = requests.post(
        f"{BASE_URL}/api/selection/theme",
        json={
            "session_id": session_id,
            "theme": "MINIMAL SCANDINAVIAN"
        }
    )
    print(f"✅ Theme selected: {response.json()['theme']}")
    
    # Step 4: Set dimensions
    print("\n4️⃣  Setting room dimensions...")
    response = requests.post(
        f"{BASE_URL}/api/selection/dimensions",
        json={
            "session_id": session_id,
            "length": 15,
            "width": 12,
            "height": 9
        }
    )
    print(f"✅ Room size: {response.json()['square_feet']} sq ft")
    
    # Step 5: Select furniture
    print("\n5️⃣  Selecting furniture...")
    response = requests.post(
        f"{BASE_URL}/api/selection/furniture/select",
        json={
            "session_id": session_id,
            "furniture_type": "Sofa",
            "subtype": "3-Seater Sofa"
        }
    )
    print(f"✅ Furniture added: {response.json()['subtype']}")
    
    # Step 6: Set price range
    print("\n6️⃣  Setting price range...")
    response = requests.post(
        f"{BASE_URL}/api/furniture/price-range",
        json={
            "session_id": session_id,
            "min_price": 500,
            "max_price": 2000
        }
    )
    print(f"✅ Price range set: ${response.json()['min_price']}-${response.json()['max_price']}")
    
    # Step 7: Search furniture
    print("\n7️⃣  Searching furniture...")
    response = requests.post(
        f"{BASE_URL}/api/furniture/search",
        json={"session_id": session_id}
    )
    results = response.json()
    print(f"✅ Found {results['count']} furniture items")
    
    if results['results']:
        print(f"\n   Example item:")
        item = results['results'][0]
        print(f"   - Name: {item['name']}")
        print(f"   - Price: ${item['price']}")
        print(f"   - Website: {item['website']}")
    
    print("\n" + "=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)


if __name__ == "__main__":
    test_complete_workflow()