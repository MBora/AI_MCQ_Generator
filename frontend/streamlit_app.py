#streamlit_app.py
import streamlit as st
import requests
from auth_functions import sign_in, create_account, sign_out, reset_password
import auth_functions

# FastAPI backend URL
BACKEND_URL = "http://localhost:8000"

def generate_mcq(chapter_index):
    response = requests.post(f"{BACKEND_URL}/generate-mcq/{chapter_index}")
    if response.status_code == 200:
        mcq_data = response.json()
        # Assuming the backend returns the full MCQ details directly
        if isinstance(mcq_data, dict):
            return mcq_data
        # If the backend returns an MCQ ID, fetch the details (This part might need adjustment based on your backend)
        elif isinstance(mcq_data, int):
            return get_mcq(mcq_data)
        else:
            st.error(f"Unexpected MCQ data format: {mcq_data}")
            return None
    else:
        st.error("Error generating MCQ")
        return None

def generate_quiz(chapter_index):
    questions = []
    for _ in range(2):  # Aim to generate 2 questions
        mcq_response = generate_mcq(chapter_index)
        if mcq_response and isinstance(mcq_response, dict):
            questions.append(mcq_response)
        else:
            print(f"Error or unexpected format in MCQ response: {mcq_response}")  # Debugging line
    return questions

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

def submit_quiz_answers(answers):
    for mcq_id, user_answer in answers.items():
        print(f"Submitting {mcq_id} with answer {user_answer}")  # Debugging line
        response = submit_answer(mcq_id, user_answer)
        print(response)  # See the backend's response

def fetch_chapter_names():
    response = requests.get(f"{BACKEND_URL}/list-chapters")
    if response.status_code == 200:
        # Remove the '.pkl' extension from each chapter name
        chapters = response.json().get("chapters", [])
        chapter_names = [chapter.rstrip('.pkl') for chapter in chapters]
        return chapter_names
    else:
        st.error("Error fetching chapter names")
        return []

def register_user(email):
    response = requests.post(f"{BACKEND_URL}/register-user", json={"email": email})
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error registering/fetching user: {response.status_code}, {response.text}")
        return None

def main():
    if 'user_info' not in st.session_state:
        st.title("Welcome to the MCQ Generator!")

        do_you_have_an_account = st.selectbox('Do you have an account?', ['Yes', 'No', 'I forgot my password'])
        email = st.text_input('Email')
        password = st.text_input('Password', type='password') if do_you_have_an_account != 'I forgot my password' else None

        if do_you_have_an_account == 'Yes' and st.button('Sign In'):
            response = sign_in(email, password)
            if 'auth_success' in st.session_state:
                st.success(st.session_state['auth_success'])
                register_user(email)  # Additional database registration step
            elif 'auth_warning' in st.session_state:
                st.error(st.session_state['auth_warning'])

        elif do_you_have_an_account == 'No' and st.button('Create Account'):
            response = create_account(email, password)
            if 'auth_success' in st.session_state:
                st.success(st.session_state['auth_success'])
                register_user(email)  # Registers the user in your database
            elif 'auth_warning' in st.session_state:
                st.error(st.session_state['auth_warning'])

        elif do_you_have_an_account == 'I forgot my password' and st.button('Send Password Reset Email'):
            reset_password_response = reset_password(email)
            if reset_password_response and reset_password_response.get('success'):
                st.success("Password reset email sent.")
            else:
                st.error("Failed to send password reset email.")
    else:
        if st.sidebar.button('Sign Out'):
            sign_out()
            st.rerun()

        st.title("MCQ Generator")

        chapter_names = fetch_chapter_names()
        if chapter_names:
            chapter_names.insert(0, "Select a chapter")
            selected_chapter_name = st.selectbox("Choose a Chapter", chapter_names)

            if selected_chapter_name != "Select a chapter":
                chapter_index = chapter_names.index(selected_chapter_name) - 1

                if st.button("Generate MCQ"):
                    mcq = generate_mcq(chapter_index)
                    if mcq:
                        st.session_state['mcq_details'] = [mcq]  # Adjust for single MCQ

                if st.button("Generate Quiz"):
                    quiz = generate_quiz(chapter_index)
                    if quiz:
                        st.session_state['mcq_details'] = quiz  # Adjust for quiz questions

        if 'mcq_details' in st.session_state and st.session_state['mcq_details']:
            with st.form("quiz_form"):
                user_answers = {}
                for i, mcq in enumerate(st.session_state['mcq_details']):
                    question_text = f"Q{i+1}: {mcq['question']}"
                    options = [mcq[f"option_{opt}"] for opt in ['a', 'b', 'c', 'd', 'e']]
                    user_answer = st.radio(question_text, options, key=f"question_{i}")
                    user_answers[i] = user_answer  # Store the actual answer selected by the user

                submitted = st.form_submit_button("Submit Quiz")

            if submitted:
                score = 0
                for i, mcq in enumerate(st.session_state['mcq_details']):
                    # Get the correct option text
                    correct_option = mcq[f"option_{mcq['correct_answer'].lower()}"]
                    print(f"User answer for Q{i+1}: {user_answers[i]}")
                    print(f"Correct answer for Q{i+1}: {correct_option}")
                    
                    # Compare the selected answer with the correct option text
                    if user_answers[i] == correct_option:
                        score += 1
                        st.success(f"Q{i+1}: Correct! Explanation: {mcq['explanation']}")
                    else:
                        st.error(f"Q{i+1}: Incorrect! Correct Answer: {correct_option}. Explanation: {mcq['explanation']}")
                st.write(f"Your score: {score}/{len(st.session_state['mcq_details'])}")

if __name__ == "__main__":
    main()
