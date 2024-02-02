import requests

# Base URL of your FastAPI application
base_url = "http://localhost:8000"

# Test MCQ Generation
def test_generate_mcq(chapter_index):
    response = requests.post(f"{base_url}/generate-mcq/{chapter_index}")
    if response.status_code == 200:
        mcq_id = response.json()
        print("MCQ Generated:")
        return mcq_id
    else:
        print("Error generating MCQ:", response.text)

# Test Submitting an Answer
def test_submit_answer(mcq_id, user_answer):
    response = requests.post(f"{base_url}/submit-answer/", json={"mcq_id": mcq_id, "user_answer": user_answer})
    if response.status_code == 200:
        result = response.json()
        print("Answer Submission Result:", result)
    else:
        print("Error submitting answer:", response.text)

# Test Getting an MCQ
def test_get_mcq(mcq_id):
    response = requests.get(f"{base_url}/get-mcq/{mcq_id}")
    if response.status_code == 200:
        mcq_data = response.json()
        print("Retrieved MCQ:", mcq_data)
    else:
        print("Error retrieving MCQ:", response.text)

# Running the tests
chapter_index = 1  # Replace with a valid chapter index
mcq_id = test_generate_mcq(chapter_index)
# print(mcq_id)
mcq_id = 1  # Replace with a valid MCQ ID
test_submit_answer(mcq_id, "A")  # Replace "A" with a chosen answer option
test_get_mcq(mcq_id) # gets the mcq details
