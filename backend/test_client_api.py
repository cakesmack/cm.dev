import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

def get_auth_token():
    """Get authentication token"""
    # Try to login with test credentials
    response = requests.post(
        f"{BASE_URL}/auth/token",
        data={
            "username": "admin@mackenzie.dev",
            "password": "admin123"
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]

    # If that fails, try another common test credential
    response = requests.post(
        f"{BASE_URL}/auth/token",
        data={
            "username": "test@example.com",
            "password": "testpassword123"
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]

    print(f"Login failed: {response.status_code} - {response.text}")
    return None

def test_create_client(token):
    """Test creating a client"""
    headers = {"Authorization": f"Bearer {token}"}
    client_data = {
        "company_name": "Test Company Inc",
        "contact_name": "John Doe",
        "contact_email": "john@testcompany.com",
        "phone": "555-1234",
        "address": "123 Test St",
        "city": "Test City",
        "state": "TS",
        "postal_code": "12345",
        "country": "USA",
        "notes": "Test client created via API"
    }

    response = requests.post(
        f"{BASE_URL}/admin/clients",
        headers=headers,
        json=client_data
    )

    print(f"\n1. Create Client: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"   Created client ID: {data['id']}")
        print(f"   Company: {data['company_name']}")
        print(f"   Contact: {data['contact_name']} ({data['contact_email']})")
        return data['id']
    else:
        print(f"   Error: {response.text}")
        return None

def test_list_clients(token):
    """Test listing clients"""
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(
        f"{BASE_URL}/admin/clients",
        headers=headers
    )

    print(f"\n2. List Clients: {response.status_code}")
    if response.status_code == 200:
        clients = response.json()
        print(f"   Total clients: {len(clients)}")
        for client in clients[:3]:  # Show first 3
            print(f"   - {client['contact_name']} ({client['contact_email']})")
    else:
        print(f"   Error: {response.text}")

def test_get_client(token, client_id):
    """Test getting a specific client"""
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(
        f"{BASE_URL}/admin/clients/{client_id}",
        headers=headers
    )

    print(f"\n3. Get Client {client_id}: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Company: {data['company_name']}")
        print(f"   Contact: {data['contact_name']}")
        print(f"   Email: {data['contact_email']}")
    else:
        print(f"   Error: {response.text}")

def test_update_client(token, client_id):
    """Test updating a client"""
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {
        "phone": "555-9999",
        "notes": "Updated test client"
    }

    response = requests.put(
        f"{BASE_URL}/admin/clients/{client_id}",
        headers=headers,
        json=update_data
    )

    print(f"\n4. Update Client {client_id}: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Updated phone: {data['phone']}")
        print(f"   Updated notes: {data['notes']}")
    else:
        print(f"   Error: {response.text}")

def test_create_lead(token):
    """Test creating a lead"""
    lead_data = {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "message": "I need a website for my business"
    }

    response = requests.post(
        f"{BASE_URL}/contact",
        json=lead_data
    )

    print(f"\n5. Create Lead: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"   Created lead ID: {data['id']}")
        print(f"   Name: {data['name']}")
        print(f"   Status: {data['status']}")
        return data['id']
    else:
        print(f"   Error: {response.text}")
        return None

def test_convert_lead_to_client(token, lead_id):
    """Test converting a lead to client"""
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.post(
        f"{BASE_URL}/admin/leads/{lead_id}/convert",
        headers=headers
    )

    print(f"\n6. Convert Lead {lead_id} to Client: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Created client ID: {data['id']}")
        print(f"   Contact: {data['contact_name']}")
        print(f"   Email: {data['contact_email']}")
        print(f"   Notes: {data['notes'][:50]}...")
        return data['id']
    else:
        print(f"   Error: {response.text}")
        return None

def test_delete_client(token, client_id):
    """Test deleting a client"""
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.delete(
        f"{BASE_URL}/admin/clients/{client_id}",
        headers=headers
    )

    print(f"\n7. Delete Client {client_id}: {response.status_code}")
    if response.status_code == 204:
        print(f"   Successfully deleted client {client_id}")
    else:
        print(f"   Error: {response.text}")

def main():
    print("=" * 60)
    print("Testing Client Management & Lead Conversion API")
    print("=" * 60)

    # Get authentication token
    token = get_auth_token()
    if not token:
        print("Failed to authenticate. Please create an admin user first.")
        return

    print("\nAuthentication successful!")

    # Test client CRUD operations
    client_id = test_create_client(token)
    if client_id:
        test_list_clients(token)
        test_get_client(token, client_id)
        test_update_client(token, client_id)

    # Test lead conversion
    lead_id = test_create_lead(token)
    if lead_id:
        converted_client_id = test_convert_lead_to_client(token, lead_id)
        if converted_client_id:
            test_get_client(token, converted_client_id)

    # Cleanup: delete test clients
    if client_id:
        test_delete_client(token, client_id)
    if 'converted_client_id' in locals() and converted_client_id:
        test_delete_client(token, converted_client_id)

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
