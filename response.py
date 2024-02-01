import requests

response = requests.post('http://localhost:8000/generate-mcq/1')
mcq_data = response.json()
print(mcq_data)

# # Accessing individual fields
# question = mcq_data.get("Question", "No question provided")
# option_a = mcq_data.get("Option A", "No option A provided")
# option_b = mcq_data.get("Option B", "No option B provided")
# option_c = mcq_data.get("Option C", "No option C provided")
# option_d = mcq_data.get("Option D", "No option D provided")
# correct_answer = mcq_data.get("CorrectAnswer", "No correct answer provided")
# explanation = mcq_data.get("Explanation", "No explanation provided")

# # Print the fields
# print("Question:", question)
# print("Option A:", option_a)
# print("Option B:", option_b)
# print("Option C:", option_c)
# print("Option D:", option_d)
# print("Correct Answer:", correct_answer)
# print("Explanation:", explanation)
