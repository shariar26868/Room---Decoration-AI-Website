"""
API Tests
=========

Test suite for Room Designer AI API endpoints.
"""

import pytest
import json
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

client = TestClient(app)


# ===================================================================
# Fixtures
# ===================================================================
@pytest.fixture
def sample_room():
    """Sample room dimensions"""
    return {"length": 15, "width": 12, "height": 9}


@pytest.fixture
def sample_session_id():
    """Sample session ID"""
    return "test-session-123"


@pytest.fixture
def mock_session(sample_session_id):
    """Mock user session"""
    from ai_backend.models import UserSession
    from ai_backend.api.upload import user_sessions
    
    session = UserSession(
        session_id=sample_session_id,
        room_image_url="https://example.com/room.jpg",
        room_type="Living Room Furniture",
        theme="MINIMAL SCANDINAVIAN",
        length=15,
        width=12,
        height=9,
        square_feet=180,
        furniture_selections=[
            {
                "type": "Sofa",
                "subtype": "3-Seater Sofa",
                "dimensions": {"width": 84, "depth": 36, "height": 34},
                "sqft": 21.0
            }
        ],
        furniture_total_sqft=21.0,
        min_price=500,
        max_price=2000
    )
    
    user_sessions[sample_session_id] = session
    yield session
    
    # Cleanup
    if sample_session_id in user_sessions:
        del user_sessions[sample_session_id]


# ===================================================================
# Test Root Endpoints
# ===================================================================
def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "workflow" in data


def test_health_check():
    """Test health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data


def test_get_room_types():
    """Test get room types"""
    response = client.get("/api/options/room-types")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["room_types"]) > 0


def test_get_themes():
    """Test get themes"""
    response = client.get("/api/options/themes")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "MINIMAL SCANDINAVIAN" in data["themes"]


# ===================================================================
# Test Upload Endpoint
# ===================================================================
@patch("ai_backend.services.storage.upload_to_s3")
def test_upload_room_image(mock_upload, tmp_path):
    """Test room image upload"""
    # Mock S3 upload
    mock_upload.return_value = "https://s3.example.com/room.jpg"
    
    # Create test image
    test_image = tmp_path / "room.jpg"
    test_image.write_bytes(b"fake image data")
    
    with open(test_image, "rb") as f:
        response = client.post(
            "/api/upload/upload",
            files={"room_image": ("room.jpg", f, "image/jpeg")}
        )
    
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "session_id" in data
    assert "image_url" in data


def test_upload_invalid_file_type():
    """Test upload with invalid file type"""
    response = client.post(
        "/api/upload/upload",
        files={"room_image": ("test.txt", b"not an image", "text/plain")}
    )
    
    assert response.status_code == 400


# ===================================================================
# Test Selection Endpoints
# ===================================================================
def test_select_room_type(mock_session, sample_session_id):
    """Test room type selection"""
    response = client.post(
        "/api/selection/room-type",
        json={
            "session_id": sample_session_id,
            "room_type": "Living Room Furniture"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["available_furniture"]) > 0


def test_select_theme(mock_session, sample_session_id):
    """Test theme selection"""
    response = client.post(
        "/api/selection/theme",
        json={
            "session_id": sample_session_id,
            "theme": "MINIMAL SCANDINAVIAN"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["websites"]) > 0


def test_set_dimensions(mock_session, sample_session_id):
    """Test setting room dimensions"""
    response = client.post(
        "/api/selection/dimensions",
        json={
            "session_id": sample_session_id,
            "length": 15,
            "width": 12,
            "height": 9
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["square_feet"] == 180.0


def test_select_furniture(mock_session, sample_session_id):
    """Test furniture selection"""
    response = client.post(
        "/api/selection/furniture/select",
        json={
            "session_id": sample_session_id,
            "furniture_type": "Coffee Table",
            "subtype": "Rectangular"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "dimensions" in data


def test_fit_check(mock_session, sample_session_id):
    """Test furniture fit check"""
    response = client.post(
        f"/api/selection/furniture/fit-check?session_id={sample_session_id}"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["fits"] is True


# ===================================================================
# Test Furniture Search
# ===================================================================
def test_set_price_range(mock_session, sample_session_id):
    """Test setting price range"""
    response = client.post(
        "/api/furniture/price-range",
        json={
            "session_id": sample_session_id,
            "min_price": 500,
            "max_price": 2000
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


@patch("ai_backend.services.furniture.search_furniture_on_websites")
def test_search_furniture(mock_search, mock_session, sample_session_id):
    """Test furniture search"""
    from ai_backend.models import FurnitureItem
    
    # Mock search results
    mock_search.return_value = [
        FurnitureItem(
            name="Modern Sofa",
            link="https://example.com/sofa",
            price=1500,
            image_url="https://example.com/sofa.jpg",
            dimensions={"width": 84, "depth": 36, "height": 34},
            website="example.com"
        )
    ]
    
    response = client.post(
        "/api/furniture/search",
        json={"session_id": sample_session_id}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["results"]) > 0


# ===================================================================
# Test Image Generation
# ===================================================================
@patch("ai_backend.services.ai_generator.generate_room_with_furniture")
@patch("ai_backend.services.storage.upload_to_s3")
@patch("requests.get")
def test_generate_image(mock_requests, mock_upload, mock_generate, mock_session, sample_session_id):
    """Test image generation"""
    # Mock dependencies
    mock_requests.return_value.content = b"fake image data"
    mock_requests.return_value.status_code = 200
    mock_generate.return_value = "/tmp/generated.jpg"
    mock_upload.return_value = "https://s3.example.com/generated.jpg"
    
    # Add search results to session
    from ai_backend.models import FurnitureItem
    from ai_backend.api.upload import user_sessions
    
    user_sessions[sample_session_id].search_results = [
        FurnitureItem(
            name="Test Sofa",
            link="https://example.com/sofa",
            price=1500,
            image_url="https://example.com/sofa.jpg",
            dimensions={"width": 84, "depth": 36, "height": 34},
            website="example.com"
        )
    ]
    
    response = client.post(
        "/api/generation/generate",
        json={
            "session_id": sample_session_id,
            "prompt": "Place sofa on left wall",
            "furniture_links": ["https://example.com/sofa"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "generated_image_url" in data


# ===================================================================
# Test Error Handling
# ===================================================================
def test_invalid_session():
    """Test with invalid session ID"""
    response = client.post(
        "/api/selection/room-type",
        json={
            "session_id": "invalid-session",
            "room_type": "Living Room Furniture"
        }
    )
    
    assert response.status_code == 404


def test_invalid_room_type(mock_session, sample_session_id):
    """Test with invalid room type"""
    response = client.post(
        "/api/selection/room-type",
        json={
            "session_id": sample_session_id,
            "room_type": "Invalid Room Type"
        }
    )
    
    assert response.status_code == 400


def test_invalid_dimensions(mock_session, sample_session_id):
    """Test with invalid dimensions"""
    response = client.post(
        "/api/selection/dimensions",
        json={
            "session_id": sample_session_id,
            "length": -10,
            "width": 12,
            "height": 9
        }
    )
    
    assert response.status_code == 422  # Validation error


# ===================================================================
# Run Tests
# ===================================================================
if __name__ == "__main__":
    pytest.main(["-v", __file__])