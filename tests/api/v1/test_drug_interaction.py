"""
Tests for drug interaction endpoints.
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


def create_sample_medications():
    """Helper to create sample medications for testing."""
    url = f"{BASE_URL}/medication/"
    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    med1_data = {
        "commercial_name": "TestMed1",
        "active_ingredients": "TestIngredient1",
        "dosage_form": "Tablet",
        "strength": "50mg",
        "manufacturer": "Test Pharma"
    }

    med2_data = {
        "commercial_name": "TestMed2",
        "active_ingredients": "TestIngredient2",
        "dosage_form": "Capsule",
        "strength": "100mg",
        "manufacturer": "Test Pharma"
    }

    response1 = requests.post(url, json=med1_data, headers=headers)
    response2 = requests.post(url, json=med2_data, headers=headers)

    return response1.json()["id"], response2.json()["id"]


def test_create_drug_interaction(med1_id, med2_id):
    """Test create drug interaction endpoint (admin only)."""
    url = f"{BASE_URL}/drug-interaction/"

    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    data = {
        "medication_id_1": str(med1_id),
        "medication_id_2": str(med2_id),
        "severity": "moderate",
        "description": "May cause increased drowsiness"
    }

    response = requests.post(url, json=data, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 201
    assert "id" in response.json()

    return response.json()["id"]


def test_get_drug_interactions():
    """Test get all drug interactions endpoint."""
    url = f"{BASE_URL}/drug-interaction/"

    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_check_drug_interaction(med1_id, med2_id):
    """Test check drug interaction endpoint."""
    url = f"{BASE_URL}/drug-interaction/check"

    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "medication_id_1": str(med1_id),
        "medication_id_2": str(med2_id)
    }

    response = requests.get(url, headers=headers, params=params)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200


def test_get_interactions_for_medication(med_id):
    """Test get interactions for a medication endpoint."""
    url = f"{BASE_URL}/drug-interaction/medication/{med_id}"

    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_drug_interaction_by_id(interaction_id):
    """Test get drug interaction by ID endpoint."""
    url = f"{BASE_URL}/drug-interaction/{interaction_id}"

    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert "id" in response.json()


def test_update_drug_interaction(interaction_id):
    """Test update drug interaction endpoint (admin only)."""
    url = f"{BASE_URL}/drug-interaction/{interaction_id}"

    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    data = {
        "severity": "severe",
        "description": "Updated: May cause serious drowsiness"
    }

    response = requests.put(url, json=data, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert response.json()["severity"] == data["severity"]


def test_delete_drug_interaction(interaction_id):
    """Test delete drug interaction endpoint (admin only)."""
    url = f"{BASE_URL}/drug-interaction/{interaction_id}"

    token = get_admin_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.delete(url, headers=headers)

    print(f"Status Code: {response.status_code}")

    assert response.status_code == 204


if __name__ == "__main__":
    print("Testing Drug Interaction Endpoints")
    print("=" * 50)

    med1_id, med2_id = None, None
    interaction_id = None

    print("\n0. Creating Sample Medications...")
    try:
        med1_id, med2_id = create_sample_medications()
        print(f"✓ Sample medications created (IDs: {med1_id}, {med2_id})")
    except Exception as e:
        print(f"✗ Creating sample medications failed: {e}")

    if med1_id and med2_id:
        print("\n1. Testing Create Drug Interaction...")
        try:
            interaction_id = test_create_drug_interaction(med1_id, med2_id)
            print(f"✓ Create drug interaction test passed (ID: {interaction_id})")
        except Exception as e:
            print(f"✗ Create drug interaction test failed: {e}")

        print("\n2. Testing Get Drug Interactions...")
        try:
            test_get_drug_interactions()
            print("✓ Get drug interactions test passed")
        except Exception as e:
            print(f"✗ Get drug interactions test failed: {e}")

        print("\n3. Testing Check Drug Interaction...")
        try:
            test_check_drug_interaction(med1_id, med2_id)
            print("✓ Check drug interaction test passed")
        except Exception as e:
            print(f"✗ Check drug interaction test failed: {e}")

        print(f"\n4. Testing Get Interactions for Medication ({med1_id})...")
        try:
            test_get_interactions_for_medication(med1_id)
            print("✓ Get interactions for medication test passed")
        except Exception as e:
            print(f"✗ Get interactions for medication test failed: {e}")

        if interaction_id:
            print(f"\n5. Testing Get Drug Interaction by ID ({interaction_id})...")
            try:
                test_get_drug_interaction_by_id(interaction_id)
                print("✓ Get drug interaction by ID test passed")
            except Exception as e:
                print(f"✗ Get drug interaction by ID test failed: {e}")

            print(f"\n6. Testing Update Drug Interaction ({interaction_id})...")
            try:
                test_update_drug_interaction(interaction_id)
                print("✓ Update drug interaction test passed")
            except Exception as e:
                print(f"✗ Update drug interaction test failed: {e}")

            print(f"\n7. Testing Delete Drug Interaction ({interaction_id})...")
            try:
                test_delete_drug_interaction(interaction_id)
                print("✓ Delete drug interaction test passed")
            except Exception as e:
                print(f"✗ Delete drug interaction test failed: {e}")
