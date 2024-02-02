import streamlit as st
import requests

# FastAPI backend URL
BACKEND_URL = "http://localhost:8000"

def generate_mcq(chapter_index):
    response = requests.post(f"{BACKEND_URL}/generate-mcq/{chapter_index}")
    if response.status_code == 200:
        return response.json()  # Assuming this is just the mcq_id
    else:
        st.error("Error generating MCQ")
        return None

def get_mcq(mcq_id):
    response = requests.get(f"{BACKEND_URL}/get-mcq/{mcq_id}")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error retrieving MCQ")
        return None

def submit_answer(mcq_id, user_answer):
    response = requests.post(f"{BACKEND_URL}/submit-answer/", json={"mcq_id": mcq_id, "user_answer": user_answer})
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error submitting answer")
        return None


def main():
    st.title("MCQ Generator")

    if 'mcq_details' not in st.session_state:
        st.session_state['mcq_details'] = None
        st.session_state['mcq_id'] = None

    chapter_index = st.number_input("Enter Chapter Index", value=1, step=1)
    generate_button = st.button("Generate MCQ")

    if generate_button:
        mcq_id = generate_mcq(chapter_index)
        if mcq_id:
            mcq_details = get_mcq(mcq_id)
            if mcq_details:
                st.session_state['mcq_details'] = mcq_details
                st.session_state['mcq_id'] = mcq_id

    if st.session_state['mcq_details']:
        st.write("Question:", st.session_state['mcq_details']["question"])
        options = [st.session_state['mcq_details'][f"option_{opt}"] for opt in ['a', 'b', 'c', 'd', 'e']]
        answer = st.radio("Select your answer:", [None] + options)
        
        # When the user submits an answer
        if st.button("Submit Answer") and answer is not None:
            result = submit_answer(st.session_state['mcq_id'], answer)
            if result:
                # Display the result and explanation
                st.write("Your answer is:", result["result"])
                st.write("Correct answer is:", result["correct_answer"])
                st.write("Explanation:", result["explanation"])

if __name__ == "__main__":
    main()
