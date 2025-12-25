"""
Tests for user endpoints.
"""

import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"


def get_auth_token():
    """Helper function to get authentication token."""
    url = f"{BASE_URL}/auth/login"
    data = {"national_id": "12345678901", "password": "securepassword123"}
    response = requests.post(url, json=data)
    return response.json()["access_token"]


def test_get_user_profile():
    """Test get user profile endpoint."""
    url = f"{BASE_URL}/user/profile"

    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert "success" in response.json()
    assert response.json()["success"] is True
    assert "data" in response.json()
    assert "first_name" in response.json()["data"]
    assert "last_name" in response.json()["data"]


if __name__ == "__main__":
    print("Testing User Endpoints")
    print("=" * 50)

    print("\n1. Testing Get User Profile...")
    try:
        test_get_user_profile()
        print("✓ Get user profile test passed")
    except Exception as e:
        print(f"✗ Get user profile test failed: {e}")
