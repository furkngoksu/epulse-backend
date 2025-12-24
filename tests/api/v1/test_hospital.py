"""
Tests for hospital endpoints.
"""
import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"


def get_auth_token():
    """Helper function to get authentication token."""
    url = f"{BASE_URL}/auth/login"
    data = {
        "national_id": "12345678901",
        "password": "securepassword123"
    }
    response = requests.post(url, json=data)
    return response.json()["access_token"]


def get_admin_token():
    """Helper function to get admin authentication token."""
    # Assumes an admin user exists with these credentials
    url = f"{BASE_URL}/auth/login"
    data = {
        "national_id": "00000000000",  # Admin national ID
        "password": "adminpassword"
    }
    response = requests.post(url, json=data)
    return response.json()["access_token"]


def test_create_hospital():
    """Test create hospital endpoint (admin only)."""
    url = f"{BASE_URL}/hospital/"

    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    data = {
        "name": "City General Hospital",
        "address": "123 Main Street",
        "city": "New York",
        "district": "Manhattan",
        "phone": "+1234567890"
    }

    response = requests.post(url, json=data, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["name"] == data["name"]

    return response.json()["id"]


def test_get_hospitals():
    """Test get all hospitals endpoint."""
    url = f"{BASE_URL}/hospital/"

    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_hospital_by_id(hospital_id):
    """Test get hospital by ID endpoint."""
    url = f"{BASE_URL}/hospital/{hospital_id}"

    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert "id" in response.json()
    assert "name" in response.json()


def test_update_hospital(hospital_id):
    """Test update hospital endpoint (admin only)."""
    url = f"{BASE_URL}/hospital/{hospital_id}"

    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    data = {
        "name": "City General Hospital - Updated"
    }

    response = requests.put(url, json=data, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert response.json()["name"] == data["name"]


def test_delete_hospital(hospital_id):
    """Test delete hospital endpoint (admin only)."""
    url = f"{BASE_URL}/hospital/{hospital_id}"

    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.delete(url, headers=headers)

    print(f"Status Code: {response.status_code}")

    assert response.status_code == 204


if __name__ == "__main__":
    print("Testing Hospital Endpoints")
    print("=" * 50)

    hospital_id = None

    print("\n1. Testing Create Hospital...")
    try:
        hospital_id = test_create_hospital()
        print(f"✓ Create hospital test passed (ID: {hospital_id})")
    except Exception as e:
        print(f"✗ Create hospital test failed: {e}")

    print("\n2. Testing Get Hospitals...")
    try:
        test_get_hospitals()
        print("✓ Get hospitals test passed")
    except Exception as e:
        print(f"✗ Get hospitals test failed: {e}")

    if hospital_id:
        print(f"\n3. Testing Get Hospital by ID ({hospital_id})...")
        try:
            test_get_hospital_by_id(hospital_id)
            print("✓ Get hospital by ID test passed")
        except Exception as e:
            print(f"✗ Get hospital by ID test failed: {e}")

        print(f"\n4. Testing Update Hospital ({hospital_id})...")
        try:
            test_update_hospital(hospital_id)
            print("✓ Update hospital test passed")
        except Exception as e:
            print(f"✗ Update hospital test failed: {e}")

        print(f"\n5. Testing Delete Hospital ({hospital_id})...")
        try:
            test_delete_hospital(hospital_id)
            print("✓ Delete hospital test passed")
        except Exception as e:
            print(f"✗ Delete hospital test failed: {e}")
