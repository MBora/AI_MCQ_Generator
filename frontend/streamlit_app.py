#streamlit_app.py
import streamlit as st
import requests
from auth_functions import sign_in, create_account, sign_out, reset_password
import auth_functions
import json

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
    # Assume `localId` is available in `st.session_state.user_info` after successful authentication
    localId = st.session_state.user_info['localId']
    response = requests.post(f"{BACKEND_URL}/register-user", json={"email": email, "localId": localId})
    if response.status_code in [200, 201]:  # Considering both 'OK' and 'Created' responses
        user_data = response.json()
        return user_data  # This includes UID and potentially other user data
    else:
        print(f"Failed to register/check user in the database: {response.text}")
        return None

def load_quiz_details(quiz_id):
    # Request quiz details from backend
    response = requests.get(f"{BACKEND_URL}/quiz-details/{quiz_id}")
    if response.status_code == 200:
        quiz_details = response.json()
        st.write(f"Quiz Name: {quiz_details['quiz_name']}")
        st.write(f"Score: {quiz_details['score']}")
        st.write(f"Timestamp: {quiz_details['timestamp']}")

        # Example: Display each question and its details
        for mcq in quiz_details['mcq_details']:
            st.subheader(f"Question: {mcq['question']}")
            st.write(f"A: {mcq['option_a']}")
            st.write(f"B: {mcq['option_b']}")
            st.write(f"C: {mcq['option_c']}")
            st.write(f"D: {mcq['option_d']}")
            st.write(f"E: {mcq['option_e']}")
            st.write(f"Correct Answer: {mcq['correct_answer']}")
            st.write(f"Explanation: {mcq['explanation']}")
            st.write("---")  # Just to add a separator for readability
    else:
        st.error("Failed to load quiz details")

def fetch_quiz_history(user_uid):
    response = requests.get(f"{BACKEND_URL}/quiz-history/{user_uid}")
    if response.status_code == 200:
        return response.json()  # Returns a list of quizzes
    else:
        st.error("Failed to fetch quiz history")
        return []

def display_quiz_history():
    # Fetch quiz history for the current user
    user_uid = st.session_state.user_info['localId']  # Assume localId is stored in session_state after login
    quiz_history = fetch_quiz_history(user_uid)

    if quiz_history:
        # Create a select box to choose a quiz from history
        quiz_names = [quiz['quiz_name'] for quiz in quiz_history]
        selected_quiz_name = st.selectbox("Select a quiz to review:", [""] + quiz_names)

        if selected_quiz_name:
            # Find the selected quiz details
            selected_quiz = next((quiz for quiz in quiz_history if quiz['quiz_name'] == selected_quiz_name), None)
            if selected_quiz:
                # Load the quiz details using its ID
                load_quiz_details(selected_quiz['id'])
    else:
        st.write("No quiz history found.")

def quiz_generation_page():
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

            submitted = st.form_submit_button("Submit Answers")

        if submitted:
            score = 0
            for i, mcq in enumerate(st.session_state['mcq_details']):
                correct_option = mcq[f"option_{mcq['correct_answer'].lower()}"]
                if user_answers[i] == correct_option:
                    score += 1
                    st.success(f"Q{i+1}: Correct! Explanation: {mcq['explanation']}")
                else:
                    st.error(f"Q{i+1}: Incorrect! Correct Answer: {correct_option}. Explanation: {mcq['explanation']}")

            # Store the calculated score in the session state
            st.session_state['calculated_score'] = score
            st.write(f"Your score: {score}/{len(st.session_state['mcq_details'])}")

        quiz_name = st.text_input("Name your quiz:", key="quiz_name")  # Ensure this is placed correctly in the code
        if st.button("Save Quiz", key="save_quiz"):
            mcq_ids = [mcq['id'] for mcq in st.session_state['mcq_details']]
            # Ensure score is taken from the session state where it was stored
            calculated_score = st.session_state.get('calculated_score', 0)  # Default to 0 if not found
            
            quiz_results = {
                "email": st.session_state['user_info']['email'],
                "quiz_name": quiz_name,
                "mcq_ids": mcq_ids,
                "score": calculated_score  # Use the calculated score from session state
            }
            # Send the request to save the quiz results
            response = requests.post(f"{BACKEND_URL}/save-quiz-results/", json=quiz_results)
            if response.status_code == 200:
                st.success("Quiz saved successfully.")
            else:
                st.error(f"Failed to save the quiz. Please ensure that the Quiz name is unique.")

def main():
    if 'user_info' not in st.session_state:
        st.title("Welcome to the MCQ Generator!")

        do_you_have_an_account = st.selectbox('Do you have an account?', ['Yes', 'No', 'I forgot my password'])
        email = st.text_input('Email')
        password = st.text_input('Password', type='password') if do_you_have_an_account != 'I forgot my password' else None

        if do_you_have_an_account == 'Yes' and st.button('Sign In'):
            response = sign_in(email, password)
            if 'auth_warning' in st.session_state and st.session_state['auth_warning']:
                st.error(st.session_state['auth_warning'])

        elif do_you_have_an_account == 'No' and st.button('Create Account'):
            response = create_account(email, password)
            if response['success']:
                # Check if verification email was sent successfully
                if response['verification_email_sent']:
                    st.success(f"Account created successfully. A verification email has been sent to {email}.")
                else:
                    st.warning(f"Account created for {email}, but there was an issue sending the verification email.")
            else:
                st.error(response['error'])  # Display the error message directly from the response

        elif do_you_have_an_account == 'I forgot my password' and st.button('Send Password Reset Email'):
            reset_password_response = reset_password(email)
            if reset_password_response and reset_password_response.get('success'):
                st.success("Password reset email sent.")
            else:
                st.error("Failed to send password reset email.")
    else:
        email = st.session_state['user_info']['email']
        register_user(email)
        # Sidebar navigation buttons
        if st.sidebar.button('MCQ/Quiz Generator'):
            st.session_state['current_page'] = 'mcq_quiz_generation'
        if st.sidebar.button('Quiz History'):
            st.session_state['current_page'] = 'quiz_history'

        # Display the appropriate page based on current_page in session_state
        if 'current_page' not in st.session_state or st.session_state['current_page'] == 'mcq_quiz_generation':
            quiz_generation_page()
        elif st.session_state['current_page'] == 'quiz_history':
            display_quiz_history()

        # Sign out button
        if st.sidebar.button('Sign Out'):
            sign_out()
            st.session_state.pop('user_info', None)  # Remove user info from session_state
            st.rerun()
    

if __name__ == "__main__":
    main()
