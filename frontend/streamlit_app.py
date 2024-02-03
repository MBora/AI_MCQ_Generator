import streamlit as st
import requests

# FastAPI backend URL
BACKEND_URL = "http://localhost:8000"

def generate_mcq(chapter_index):
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    response = requests.post(f"{BACKEND_URL}/generate-mcq/{chapter_index}", headers=headers)
    if response.status_code == 200:
        return response.json()  # Assuming this is just the mcq_id
    else:
        st.error("Error generating MCQ")
        return None

def get_mcq(mcq_id):
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    response = requests.get(f"{BACKEND_URL}/get-mcq/{mcq_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error retrieving MCQ")
        return None

def submit_answer(mcq_id, user_answer):
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    response = requests.post(f"{BACKEND_URL}/submit-answer/", json={"mcq_id": mcq_id, "user_answer": user_answer}, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error submitting answer")
        return None

def login(username, password):
    response = requests.post(f"{BACKEND_URL}/token", data={"username": username, "password": password})
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Login failed"}

def signup(username, email, password):
    response = requests.post(f"{BACKEND_URL}/signup/", json={"username": username, "email": email, "password": password})
    if response.status_code == 200 or "detail" in response.json():
        return response.json()
    else:
        return {"error": "Signup failed"}

def show_login_form():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username", key="login_username")
    password = st.sidebar.text_input("Password", type="password", key="login_password")

    if st.sidebar.button("Login", key="login_button"):
        login_response = login(username, password)
        if "access_token" in login_response:
            st.sidebar.success("Logged in successfully.")
            st.session_state["token"] = login_response["access_token"]
            st.session_state["page"] = "mcq_generator"
            st.rerun()
        else:
            st.sidebar.error("Login failed.")

def show_signup_form():
    st.sidebar.title("Signup")
    username = st.sidebar.text_input("Username", key="signup_username")
    email = st.sidebar.text_input("Email", key="signup_email")
    password = st.sidebar.text_input("Password", type="password", key="signup_password")

    if st.sidebar.button("Signup", key="signup_button"):
        signup_response = signup(username, email, password)
        if "detail" in signup_response:
            st.sidebar.error(signup_response["detail"])
        else:
            st.sidebar.success("Signed up successfully. Please log in.")
            st.session_state["page"] = "login"
            st.rerun()
# Define a function to show the home page
def show_home():
    st.write("Welcome to the MCQ Generator App.")
    if st.button("Login"):
        st.session_state["page"] = "login"
        st.rerun()
    if st.button("Signup"):
        st.session_state["page"] = "signup"
        st.rerun()


def show_mcq_generator():
    st.write("MCQ Generator Page")
    chapter_index = st.number_input("Enter Chapter Index", value=1, step=1)
    generate_button = st.button("Generate MCQ")

    if generate_button:
        mcq_id = generate_mcq(chapter_index)
        if mcq_id:
            mcq_details = get_mcq(mcq_id)
            if mcq_details:
                st.session_state['mcq_details'] = mcq_details
                st.session_state['mcq_id'] = mcq_id

    if 'mcq_details' in st.session_state and st.session_state['mcq_details']:
        st.write("Question:", st.session_state['mcq_details']["question"])
        options = [st.session_state['mcq_details'][f"option_{opt}"] for opt in ['a', 'b', 'c', 'd', 'e']]
        answer = st.radio("Select your answer:", [None] + options)
        
        if st.button("Submit Answer") and answer is not None:
            result = submit_answer(st.session_state['mcq_id'], answer)
            if result:
                st.write("Your answer is:", result["result"])
                st.write("Correct answer is:", result["correct_answer"])
                st.write("Explanation:", result["explanation"])

def main():
    st.title("MCQ Generator")

    # Initialize session state variables for page navigation and token
    if "page" not in st.session_state:
        st.session_state["page"] = "home"
        st.rerun()
    if "token" not in st.session_state:
        st.session_state["token"] = None

    # Show the appropriate page based on the user's login status and page selection
    if st.session_state["token"] and st.session_state["page"] == "mcq_generator":
        # User is logged in and has chosen to view the MCQ generator page
        show_mcq_generator()
    elif st.session_state["page"] == "login":
        # Show login form
        show_login_form()
    elif st.session_state["page"] == "signup":
        # Show signup form
        show_signup_form()
    else:
        # User is not logged in and hasn't selected a page
        show_home()

if __name__ == "__main__":
    main()

