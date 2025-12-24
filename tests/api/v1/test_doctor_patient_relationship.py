"""
Tests for doctor-patient relationship endpoints.
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


def test_create_relationship():
    """Test create doctor-patient relationship endpoint."""
    url = f"{BASE_URL}/doctor-patient-relationship/"

    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    # These would need to be valid doctor and patient IDs from your database
    data = {
        "doctor_id": "00000000-0000-0000-0000-000000000001",  # Placeholder
        "patient_id": "00000000-0000-0000-0000-000000000002"  # Placeholder
    }

    response = requests.post(url, json=data, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 201
    assert "id" in response.json()

    return response.json()["id"]


def test_get_all_relationships():
    """Test get all relationships endpoint (admin only)."""
    url = f"{BASE_URL}/doctor-patient-relationship/"

    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_patients_for_doctor(doctor_id):
    """Test get patients for a doctor endpoint."""
    url = f"{BASE_URL}/doctor-patient-relationship/doctor/{doctor_id}/patients"

    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_doctors_for_patient(patient_id):
    """Test get doctors for a patient endpoint."""
    url = f"{BASE_URL}/doctor-patient-relationship/patient/{patient_id}/doctors"

    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_relationship_by_id(relationship_id):
    """Test get relationship by ID endpoint."""
    url = f"{BASE_URL}/doctor-patient-relationship/{relationship_id}"

    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert "id" in response.json()


def test_delete_relationship(relationship_id):
    """Test delete relationship endpoint (admin only)."""
    url = f"{BASE_URL}/doctor-patient-relationship/{relationship_id}"

    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.delete(url, headers=headers)

    print(f"Status Code: {response.status_code}")

    assert response.status_code == 204


if __name__ == "__main__":
    print("Testing Doctor-Patient Relationship Endpoints")
    print("=" * 50)

    relationship_id = None
    doctor_id = "00000000-0000-0000-0000-000000000001"  # Placeholder
    patient_id = "00000000-0000-0000-0000-000000000002"  # Placeholder

    print("\n1. Testing Create Relationship...")
    try:
        relationship_id = test_create_relationship()
        print(f"✓ Create relationship test passed (ID: {relationship_id})")
    except Exception as e:
        print(f"✗ Create relationship test failed: {e}")

    print("\n2. Testing Get All Relationships...")
    try:
        test_get_all_relationships()
        print("✓ Get all relationships test passed")
    except Exception as e:
        print(f"✗ Get all relationships test failed: {e}")

    print(f"\n3. Testing Get Patients for Doctor ({doctor_id})...")
    try:
        test_get_patients_for_doctor(doctor_id)
        print("✓ Get patients for doctor test passed")
    except Exception as e:
        print(f"✗ Get patients for doctor test failed: {e}")

    print(f"\n4. Testing Get Doctors for Patient ({patient_id})...")
    try:
        test_get_doctors_for_patient(patient_id)
        print("✓ Get doctors for patient test passed")
    except Exception as e:
        print(f"✗ Get doctors for patient test failed: {e}")

    if relationship_id:
        print(f"\n5. Testing Get Relationship by ID ({relationship_id})...")
        try:
            test_get_relationship_by_id(relationship_id)
            print("✓ Get relationship by ID test passed")
        except Exception as e:
            print(f"✗ Get relationship by ID test failed: {e}")

        print(f"\n6. Testing Delete Relationship ({relationship_id})...")
        try:
            test_delete_relationship(relationship_id)
            print("✓ Delete relationship test passed")
        except Exception as e:
            print(f"✗ Delete relationship test failed: {e}")
