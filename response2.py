import requests

# Example data
mcq_id = "b7c87965-ccbb-4f37-9181-ccacb159a264"
user_answer = "Option D"  # User's selected option

response = requests.post('http://localhost:8000/submit-answer/', json={"mcq_id": mcq_id, "user_answer": user_answer})
result = response.json()

print(result)
