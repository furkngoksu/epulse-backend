"""
Tests for authentication endpoints.
"""

import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"


def test_register():
    """Test user registration endpoint."""
    url = f"{BASE_URL}/auth/register"

    data = {
        "national_id": "12345678901",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone_number": "+1234567890",
        "password": "securepassword123",
        "date_of_birth": "1990-01-01",
        "gender": "male",
    }

    response = requests.post(url, json=data)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert "user" in response.json()
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


def test_login():
    """Test user login endpoint."""
    url = f"{BASE_URL}/auth/login"

    data = {"national_id": "12345678901", "password": "securepassword123"}

    response = requests.post(url, json=data)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert "success" in response.json()
    assert response.json()["success"] is True
    assert "user" in response.json()
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


if __name__ == "__main__":
    print("Testing Authentication Endpoints")
    print("=" * 50)

    print("\n1. Testing Registration...")
    try:
        test_register()
        print("✓ Registration test passed")
    except Exception as e:
        print(f"✗ Registration test failed: {e}")

    print("\n2. Testing Login...")
    try:
        test_login()
        print("✓ Login test passed")
    except Exception as e:
        print(f"✗ Login test failed: {e}")
