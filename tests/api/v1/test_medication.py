"""
Tests for medication endpoints.
"""

import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"


def get_auth_token():
    """Helper function to get authentication token."""
    url = f"{BASE_URL}/auth/login"
    data = {"national_id": "12345678901", "password": "securepassword123"}
    response = requests.post(url, json=data)
    return response.json()["access_token"]


def get_admin_token():
    """Helper function to get admin authentication token."""
    url = f"{BASE_URL}/auth/login"
    data = {"national_id": "00000000000", "password": "adminpassword"}
    response = requests.post(url, json=data)
    return response.json()["access_token"]


def test_create_medication():
    """Test create medication endpoint (admin only)."""
    url = f"{BASE_URL}/medication/"

    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    data = {
        "commercial_name": "Aspirin",
        "active_ingredients": "Acetylsalicylic acid",
        "dosage_form": "Tablet",
        "strength": "100mg",
        "manufacturer": "Generic Pharma",
        "description": "Pain reliever and anti-inflammatory",
    }

    response = requests.post(url, json=data, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["commercial_name"] == data["commercial_name"]

    return response.json()["id"]


def test_get_medications():
    """Test get all medications endpoint."""
    url = f"{BASE_URL}/medication/"

    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_search_medications():
    """Test search medications endpoint."""
    url = f"{BASE_URL}/medication/search"

    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {"name": "Aspirin"}

    response = requests.get(url, headers=headers, params=params)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_medication_by_id(medication_id):
    """Test get medication by ID endpoint."""
    url = f"{BASE_URL}/medication/{medication_id}"

    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert "id" in response.json()
    assert "commercial_name" in response.json()


def test_update_medication(medication_id):
    """Test update medication endpoint (admin only)."""
    url = f"{BASE_URL}/medication/{medication_id}"

    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    data = {"description": "Updated description for Aspirin"}

    response = requests.put(url, json=data, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert response.json()["description"] == data["description"]


def test_delete_medication(medication_id):
    """Test delete medication endpoint (admin only)."""
    url = f"{BASE_URL}/medication/{medication_id}"

    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.delete(url, headers=headers)

    print(f"Status Code: {response.status_code}")

    assert response.status_code == 204


if __name__ == "__main__":
    print("Testing Medication Endpoints")
    print("=" * 50)

    medication_id = None

    print("\n1. Testing Create Medication...")
    try:
        medication_id = test_create_medication()
        print(f"✓ Create medication test passed (ID: {medication_id})")
    except Exception as e:
        print(f"✗ Create medication test failed: {e}")

    print("\n2. Testing Get Medications...")
    try:
        test_get_medications()
        print("✓ Get medications test passed")
    except Exception as e:
        print(f"✗ Get medications test failed: {e}")

    print("\n3. Testing Search Medications...")
    try:
        test_search_medications()
        print("✓ Search medications test passed")
    except Exception as e:
        print(f"✗ Search medications test failed: {e}")

    if medication_id:
        print(f"\n4. Testing Get Medication by ID ({medication_id})...")
        try:
            test_get_medication_by_id(medication_id)
            print("✓ Get medication by ID test passed")
        except Exception as e:
            print(f"✗ Get medication by ID test failed: {e}")

        print(f"\n5. Testing Update Medication ({medication_id})...")
        try:
            test_update_medication(medication_id)
            print("✓ Update medication test passed")
        except Exception as e:
            print(f"✗ Update medication test failed: {e}")

        print(f"\n6. Testing Delete Medication ({medication_id})...")
        try:
            test_delete_medication(medication_id)
            print("✓ Delete medication test passed")
        except Exception as e:
            print(f"✗ Delete medication test failed: {e}")
