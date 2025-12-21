"""
Tests for doctor profile endpoints.
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
    url = f"{BASE_URL}/auth/login"
    data = {
        "national_id": "00000000000",
        "password": "adminpassword"
    }
    response = requests.post(url, json=data)
    return response.json()["access_token"]


def create_sample_doctor_and_hospital():
    """Helper to create a sample doctor user and hospital."""
    # Create a hospital first
    hospital_url = f"{BASE_URL}/hospital/"
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    hospital_data = {
        "name": "Test Hospital for Doctor",
        "address": "456 Medical Ave",
        "city": "Boston",
        "district": "Suffolk",
        "phone": "+9876543210"
    }

    hospital_response = requests.post(hospital_url, json=hospital_data, headers=headers)
    hospital_id = hospital_response.json()["id"]

    # Create a doctor user (assuming registration creates a regular user)
    # You would need to update the user's role to DOCTOR via admin endpoint
    # For simplicity, we'll assume a doctor user exists or can be created
    # This is a placeholder for the actual doctor_id
    doctor_id = "00000000-0000-0000-0000-000000000001"  # Placeholder

    return doctor_id, hospital_id


def test_create_doctor_profile():
    """Test create doctor profile endpoint (admin only)."""
    url = f"{BASE_URL}/doctor-profile/"

    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    doctor_id, hospital_id = create_sample_doctor_and_hospital()

    data = {
        "doctor_id": str(doctor_id),
        "hospital_id": str(hospital_id),
        "specialty": "Cardiology",
        "license_number": "LIC123456",
        "years_of_experience": 10,
        "education": "MD from Harvard Medical School",
        "bio": "Experienced cardiologist specializing in heart disease"
    }

    response = requests.post(url, json=data, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 201
    assert "id" in response.json()

    return response.json()["id"]


def test_get_doctor_profiles():
    """Test get all doctor profiles endpoint."""
    url = f"{BASE_URL}/doctor-profile/"

    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_doctors_by_hospital(hospital_id):
    """Test get doctors by hospital endpoint."""
    url = f"{BASE_URL}/doctor-profile/hospital/{hospital_id}"

    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_doctor_profile_by_id(profile_id):
    """Test get doctor profile by ID endpoint."""
    url = f"{BASE_URL}/doctor-profile/{profile_id}"

    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert "id" in response.json()


def test_update_doctor_profile(profile_id):
    """Test update doctor profile endpoint (admin only)."""
    url = f"{BASE_URL}/doctor-profile/{profile_id}"

    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    data = {
        "years_of_experience": 15,
        "bio": "Updated: Highly experienced cardiologist"
    }

    response = requests.put(url, json=data, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert response.json()["years_of_experience"] == data["years_of_experience"]


def test_delete_doctor_profile(profile_id):
    """Test delete doctor profile endpoint (admin only)."""
    url = f"{BASE_URL}/doctor-profile/{profile_id}"

    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.delete(url, headers=headers)

    print(f"Status Code: {response.status_code}")

    assert response.status_code == 204


if __name__ == "__main__":
    print("Testing Doctor Profile Endpoints")
    print("=" * 50)

    profile_id = None
    hospital_id = None

    print("\n1. Testing Create Doctor Profile...")
    try:
        profile_id = test_create_doctor_profile()
        print(f"✓ Create doctor profile test passed (ID: {profile_id})")
    except Exception as e:
        print(f"✗ Create doctor profile test failed: {e}")

    print("\n2. Testing Get Doctor Profiles...")
    try:
        test_get_doctor_profiles()
        print("✓ Get doctor profiles test passed")
    except Exception as e:
        print(f"✗ Get doctor profiles test failed: {e}")

    if profile_id:
        print(f"\n3. Testing Get Doctor Profile by ID ({profile_id})...")
        try:
            test_get_doctor_profile_by_id(profile_id)
            print("✓ Get doctor profile by ID test passed")
        except Exception as e:
            print(f"✗ Get doctor profile by ID test failed: {e}")

        print(f"\n4. Testing Update Doctor Profile ({profile_id})...")
        try:
            test_update_doctor_profile(profile_id)
            print("✓ Update doctor profile test passed")
        except Exception as e:
            print(f"✗ Update doctor profile test failed: {e}")

        print(f"\n5. Testing Delete Doctor Profile ({profile_id})...")
        try:
            test_delete_doctor_profile(profile_id)
            print("✓ Delete doctor profile test passed")
        except Exception as e:
            print(f"✗ Delete doctor profile test failed: {e}")
