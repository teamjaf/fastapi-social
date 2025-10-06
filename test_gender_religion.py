import requests
import json

# Test data
base_url = "http://localhost:9090/api/v1"

# Register a new user
register_data = {
    "email": "testuser2@university.edu",
    "username": "testuser456",
    "password": "password123",
    "full_name": "Test User 2",
    "university": "Test University 2"
}

print("1. Registering a new user...")
response = requests.post(f"{base_url}/auth/register", json=register_data)
print(f"Register Status: {response.status_code}")
if response.status_code == 201:
    user_data = response.json()
    print(f"User created: {user_data['username']} - {user_data['email']}")
else:
    print(f"Register failed: {response.text}")
    exit(1)

# Login to get token
login_data = {
    "username": "testuser2@university.edu",
    "password": "password123"
}

print("\n2. Logging in...")
response = requests.post(f"{base_url}/auth/login", json=login_data)
print(f"Login Status: {response.status_code}")
if response.status_code == 200:
    token_data = response.json()
    token = token_data['access_token']
    print(f"Token received: {token[:20]}...")
else:
    print(f"Login failed: {response.text}")
    exit(1)

# Set up headers for authenticated requests
headers = {"Authorization": f"Bearer {token}"}

# Test updating profile with new fields
print("\n3. Testing profile update with gender and religion...")
update_data = {
    "gender": "male",
    "religion": "islam",
    "university": "Updated University",
    "major": "Computer Science",
    "one_line_bio": "Testing new gender and religion fields"
}

response = requests.put(f"{base_url}/profile/me", json=update_data, headers=headers)
print(f"Update Profile Status: {response.status_code}")
if response.status_code == 200:
    profile = response.json()
    print(f"Profile updated successfully!")
    print(f"Gender: {profile.get('gender')}")
    print(f"Religion: {profile.get('religion')}")
    print(f"University: {profile.get('university')}")
    print(f"Major: {profile.get('major')}")
else:
    print(f"Update failed: {response.text}")

# Test getting profile to verify fields are saved
print("\n4. Getting updated profile...")
response = requests.get(f"{base_url}/profile/me", headers=headers)
print(f"Get Profile Status: {response.status_code}")
if response.status_code == 200:
    profile = response.json()
    print(f"Profile retrieved successfully!")
    print(f"Gender: {profile.get('gender')}")
    print(f"Religion: {profile.get('religion')}")
    print(f"University: {profile.get('university')}")
    print(f"Major: {profile.get('major')}")
else:
    print(f"Get profile failed: {response.text}")

print("\nGender and religion fields testing completed!")
