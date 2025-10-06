import requests
import json

# Test data
base_url = "http://localhost:9090/api/v1"

# First, let's register a user and get a token
register_data = {
    "email": "student2@university.edu",
    "username": "student456",
    "password": "password123",
    "full_name": "Jane Student"
}

print("1. Registering a new user...")
response = requests.post(f"{base_url}/auth/register", json=register_data)
print(f"Register Status: {response.status_code}")
if response.status_code == 201:
    user_data = response.json()
    print(f"User created: {user_data['username']}")
else:
    print(f"Register failed: {response.text}")
    exit(1)

# Login to get token
login_data = {
    "username": "student2@university.edu",
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

# Test updating profile with dream_role instead of pronouns
profile_update = {
    "university": "Tech University",
    "campus": "Downtown Campus",
    "major": "Software Engineering",
    "current_class": "senior",
    "graduation_year": 2025,
    "current_role": "student",
    "one_line_bio": "Software Engineering student passionate about AI and Machine Learning",
    "interests": ["Artificial Intelligence", "Machine Learning", "Web Development", "Mobile Apps"],
    "hobbies": ["Coding", "Reading Tech Blogs", "Gaming", "Photography"],
    "dream_role": "Senior Software Engineer at a Tech Startup"
}

print("\n3. Updating profile with dream_role...")
response = requests.put(f"{base_url}/profile/me", json=profile_update, headers=headers)
print(f"Update Profile Status: {response.status_code}")
if response.status_code == 200:
    updated_profile = response.json()
    print(f"Updated profile: {updated_profile['university']} - {updated_profile['major']}")
    print(f"Dream Role: {updated_profile['dream_role']}")
    print(f"Interests: {updated_profile['interests']}")
    print(f"Hobbies: {updated_profile['hobbies']}")
else:
    print(f"Update profile failed: {response.text}")

# Test getting public profile
user_id = updated_profile['id']
print(f"\n4. Getting public profile for user {user_id}...")
response = requests.get(f"{base_url}/profile/{user_id}")
print(f"Get Public Profile Status: {response.status_code}")
if response.status_code == 200:
    public_profile = response.json()
    print(f"Public profile: {public_profile['username']} - {public_profile['university']}")
    print(f"Major: {public_profile['major']}")
    print(f"Dream Role: {public_profile['dream_role']}")
    print(f"Interests: {public_profile['interests']}")
else:
    print(f"Get public profile failed: {response.text}")

print("\n5. Testing partial update with dream_role...")
partial_update = {
    "dream_role": "Lead AI Engineer at Google",
    "one_line_bio": "Updated bio: Senior CS student aspiring to be an AI Engineer"
}
response = requests.patch(f"{base_url}/profile/me", json=partial_update, headers=headers)
print(f"Partial Update Status: {response.status_code}")
if response.status_code == 200:
    partial_updated = response.json()
    print(f"Updated dream role: {partial_updated['dream_role']}")
    print(f"Updated bio: {partial_updated['one_line_bio']}")
else:
    print(f"Partial update failed: {response.text}")

print("\nProfile CRUD testing with dream_role completed!")
