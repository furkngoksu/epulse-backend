"""
Tests for appointment endpoints.
"""

import requests
from datetime import datetime, timedelta

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


def get_doctor_token():
    """Helper function to get doctor authentication token."""
    url = f"{BASE_URL}/auth/login"
    data = {
        "national_id": "11111111111",  # Doctor national ID
        "password": "doctorpassword",
    }
    response = requests.post(url, json=data)
    return response.json()["access_token"]


def get_patient_token():
    """Helper function to get patient authentication token."""
    url = f"{BASE_URL}/auth/login"
    data = {
        "national_id": "22222222222",  # Patient national ID
        "password": "patientpassword",
    }
    response = requests.post(url, json=data)
    return response.json()["access_token"]


def test_create_appointment():
    """Test create appointment endpoint (doctor/admin)."""
    url = f"{BASE_URL}/appointment/"

    token = get_doctor_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Create an appointment for tomorrow
    appointment_time = datetime.now() + timedelta(days=1)

    data = {
        "doctor_id": "00000000-0000-0000-0000-000000000001",  # Placeholder doctor ID
        "appointment_datetime": appointment_time.isoformat(),
        "duration_minutes": 30,
    }

    response = requests.post(url, json=data, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 201
    assert "id" in response.json()

    return response.json()["id"]


def test_get_all_appointments():
    """Test get all appointments endpoint (admin only)."""
    url = f"{BASE_URL}/appointment/"

    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_free_appointments():
    """Test get free appointments endpoint."""
    url = f"{BASE_URL}/appointment/free"

    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_appointments_by_doctor(doctor_id):
    """Test get appointments by doctor endpoint."""
    url = f"{BASE_URL}/appointment/doctor/{doctor_id}"

    token = get_doctor_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_appointments_by_patient(patient_id):
    """Test get appointments by patient endpoint."""
    url = f"{BASE_URL}/appointment/patient/{patient_id}"

    token = get_patient_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_appointment_by_id(appointment_id):
    """Test get appointment by ID endpoint."""
    url = f"{BASE_URL}/appointment/{appointment_id}"

    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert "id" in response.json()


def test_book_appointment(appointment_id):
    """Test book appointment endpoint (patient only)."""
    url = f"{BASE_URL}/appointment/{appointment_id}/book"

    token = get_patient_token()
    headers = {"Authorization": f"Bearer {token}"}

    data = {"reason": "Regular checkup"}

    response = requests.post(url, json=data, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert response.json()["status"] == "booked"


def test_cancel_appointment(appointment_id):
    """Test cancel appointment endpoint."""
    url = f"{BASE_URL}/appointment/{appointment_id}/cancel"

    token = get_patient_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.post(url, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200


def test_complete_appointment(appointment_id):
    """Test complete appointment endpoint (doctor/admin)."""
    url = f"{BASE_URL}/appointment/{appointment_id}/complete"

    token = get_doctor_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.post(url, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_mark_no_show(appointment_id):
    """Test mark appointment as no-show endpoint (doctor/admin)."""
    url = f"{BASE_URL}/appointment/{appointment_id}/no-show"

    token = get_doctor_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.post(url, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert response.json()["status"] == "no_show"


def test_update_appointment(appointment_id):
    """Test update appointment endpoint (admin only)."""
    url = f"{BASE_URL}/appointment/{appointment_id}"

    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    data = {"duration_minutes": 45}

    response = requests.put(url, json=data, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert response.json()["duration_minutes"] == data["duration_minutes"]


def test_delete_appointment(appointment_id):
    """Test delete appointment endpoint (admin only)."""
    url = f"{BASE_URL}/appointment/{appointment_id}"

    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.delete(url, headers=headers)

    print(f"Status Code: {response.status_code}")

    assert response.status_code == 204


if __name__ == "__main__":
    print("Testing Appointment Endpoints")
    print("=" * 50)

    appointment_id = None
    doctor_id = "00000000-0000-0000-0000-000000000001"  # Placeholder
    patient_id = "00000000-0000-0000-0000-000000000002"  # Placeholder

    print("\n1. Testing Create Appointment...")
    try:
        appointment_id = test_create_appointment()
        print(f"✓ Create appointment test passed (ID: {appointment_id})")
    except Exception as e:
        print(f"✗ Create appointment test failed: {e}")

    print("\n2. Testing Get All Appointments...")
    try:
        test_get_all_appointments()
        print("✓ Get all appointments test passed")
    except Exception as e:
        print(f"✗ Get all appointments test failed: {e}")

    print("\n3. Testing Get Free Appointments...")
    try:
        test_get_free_appointments()
        print("✓ Get free appointments test passed")
    except Exception as e:
        print(f"✗ Get free appointments test failed: {e}")

    print(f"\n4. Testing Get Appointments by Doctor ({doctor_id})...")
    try:
        test_get_appointments_by_doctor(doctor_id)
        print("✓ Get appointments by doctor test passed")
    except Exception as e:
        print(f"✗ Get appointments by doctor test failed: {e}")

    print(f"\n5. Testing Get Appointments by Patient ({patient_id})...")
    try:
        test_get_appointments_by_patient(patient_id)
        print("✓ Get appointments by patient test passed")
    except Exception as e:
        print(f"✗ Get appointments by patient test failed: {e}")

    if appointment_id:
        print(f"\n6. Testing Get Appointment by ID ({appointment_id})...")
        try:
            test_get_appointment_by_id(appointment_id)
            print("✓ Get appointment by ID test passed")
        except Exception as e:
            print(f"✗ Get appointment by ID test failed: {e}")

        print(f"\n7. Testing Book Appointment ({appointment_id})...")
        try:
            test_book_appointment(appointment_id)
            print("✓ Book appointment test passed")
        except Exception as e:
            print(f"✗ Book appointment test failed: {e}")

        print(f"\n8. Testing Cancel Appointment ({appointment_id})...")
        try:
            test_cancel_appointment(appointment_id)
            print("✓ Cancel appointment test passed")
        except Exception as e:
            print(f"✗ Cancel appointment test failed: {e}")

        # Note: These tests might fail depending on appointment state
        # print(f"\n9. Testing Complete Appointment ({appointment_id})...")
        # try:
        #     test_complete_appointment(appointment_id)
        #     print("✓ Complete appointment test passed")
        # except Exception as e:
        #     print(f"✗ Complete appointment test failed: {e}")

        # print(f"\n10. Testing Mark No-Show ({appointment_id})...")
        # try:
        #     test_mark_no_show(appointment_id)
        #     print("✓ Mark no-show test passed")
        # except Exception as e:
        #     print(f"✗ Mark no-show test failed: {e}")

        print(f"\n9. Testing Update Appointment ({appointment_id})...")
        try:
            test_update_appointment(appointment_id)
            print("✓ Update appointment test passed")
        except Exception as e:
            print(f"✗ Update appointment test failed: {e}")

        print(f"\n10. Testing Delete Appointment ({appointment_id})...")
        try:
            test_delete_appointment(appointment_id)
            print("✓ Delete appointment test passed")
        except Exception as e:
            print(f"✗ Delete appointment test failed: {e}")
