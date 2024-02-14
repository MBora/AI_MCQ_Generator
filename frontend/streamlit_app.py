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
        password = st.text_input('Password', type='password') if do_you_have_an_account in ['Yes', 'No'] else None

        if do_you_have_an_account == 'Yes' and st.button('Sign In'):
            response = sign_in(email, password)
            if response and response.get('success'):
                register_user(email)  # Additional database registration step
            else:
                st.error("Login failed. Please try again.")
        
        elif do_you_have_an_account == 'No' and st.button('Create Account'):
            response = create_account(email, password)
            if response and response.get('success'):
                register_user(email)  # Registers the user in your database
                if response.get('verification_email_sent'):
                    st.success("Account created successfully. Verification email has been sent.")
                else:
                    st.warning("Account created but there was an issue sending the verification email.")
            else:
                st.error("Account creation failed. Please try again.")
        
        elif do_you_have_an_account == 'I forgot my password' and st.button('Send Password Reset Email'):
            reset_password_response = reset_password(email)
            if reset_password_response.get('success'):
                st.success("Password reset email sent.")
            else:
                st.error("Failed to send password reset email.")

    else:
        # Place for the sign-out button
        if st.sidebar.button('Sign Out'):
            auth_functions.sign_out()
            st.rerun()

        st.title("MCQ Generator")

        if 'mcq_details' not in st.session_state:
            st.session_state['mcq_details'] = None
            st.session_state['mcq_id'] = None

        # Fetch chapter names from the backend
        chapter_names = fetch_chapter_names()

        # Add None or a default selection prompt as the first option
        chapter_names.insert(0, "Select a chapter")
        selected_chapter_name = st.selectbox("Choose a Chapter", chapter_names)

        # Only enable MCQ generation if a chapter is selected
        if selected_chapter_name != "Select a chapter":
            generate_button = st.button("Generate MCQ")

            if generate_button:
                # Find the index of the selected chapter name
                chapter_index = chapter_names.index(selected_chapter_name) - 1  # Adjust for the added default selection
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
