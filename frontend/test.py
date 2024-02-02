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


# Testing Signup
print("Testing Signup...")
signup_response = signup("testuser", "testuser@example.com", "password123")
print(signup_response)

# Testing Login
print("\nTesting Login...")
login_response = login("testuser", "password123")
print(login_response)
