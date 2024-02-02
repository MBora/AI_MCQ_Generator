import requests

# URL of your FastAPI application
BASE_URL = "http://127.0.0.1:8000"

def signup(username, email, password):
    url = f"{BASE_URL}/signup/"
    payload = {
        "username": username,
        "email": email,
        "password": password
    }
    response = requests.post(url, json=payload)
    return response.json()

def login(username, password):
    url = f"{BASE_URL}/token"
    payload = {
        "username": username,
        "password": password
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200 and response.headers.get('Content-Type') == 'application/json':
        return response.json()
    else:
        return {"error": response.text, "status_code": response.status_code}

    
def test_protected_endpoint(token, endpoint):
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    return response.json()

def test_protected_endpoint_with_wrong_token(endpoint):
    url = f"{BASE_URL}{endpoint}"
    # Using a deliberately incorrect token
    wrong_token = "incorrect_token"
    headers = {
        "Authorization": f"Bearer {wrong_token}"
    }
    response = requests.get(url, headers=headers)
    return response.status_code, response.text

# # Testing Signup
# print("Testing Signup...")
# signup_response = signup("testuser", "testuser@example.com", "password123")
# print(signup_response)

# Testing Login
print("\nTesting Login...")
login_response = login("testuser", "password123")
print(login_response)

# If login is successful, test a protected endpoint
if "access_token" in login_response:
    token = login_response["access_token"]
    print("\nTesting Protected Endpoint...")
    protected_endpoint_response = test_protected_endpoint(token, "/get-mcq/1")
    print(protected_endpoint_response)

# Testing with wrong access token
print("\nTesting Protected Endpoint with Wrong Token...")
status_code, response_text = test_protected_endpoint_with_wrong_token("/get-mcq/1")
print(f"Status Code: {status_code}, Response: {response_text}")
