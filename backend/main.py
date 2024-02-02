#main.py
import os
import openai
from openai import OpenAI
import llama_index.llms
import random
from fastapi import FastAPI, HTTPException, Query
import pickle
from fastapi import Body
import json

# Database stuff
from crud import insert_mcq, get_mcq_details
from database import engine, mcqs

# load OPENAI_API_KEY from .env file
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

from openai import OpenAI
client = OpenAI()
app = FastAPI()

from llama_index.schema import MetadataMode

# Additional imports in main.py
from crud import create_user, get_user_by_username
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, status
from pydantic import BaseModel
from schemas import UserCreate, Token, User
from dependencies import create_access_token, verify_password, get_password_hash, get_current_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/generate-mcq/{chapter_index}")
async def generate_mcq(chapter_index: int = 0, current_user: User = Depends(get_current_user)):
    # get the list of pkls from the processed_data folder
    pkls = []
    try:
        for file_name in os.listdir("../processed_data"):
            if file_name.endswith(".pkl"):
                pkls.append(file_name)
    except:
        raise HTTPException(status_code=404, detail="Error opening processed_data folder")
    
    if not pkls:
        raise HTTPException(status_code=404, detail="No PKL files found")

    if chapter_index >= len(pkls):
        raise HTTPException(status_code=404, detail="Chapter index out of range")
       
    # open pkl from pkl 
    try:
        with open(f"../processed_data/{pkls[chapter_index]}", "rb") as f:
            nodes = pickle.load(f)
    except:
        raise HTTPException(status_code=404, detail="Error opening PKL file")
    
    node_text = random.choice(nodes).get_content(metadata_mode=MetadataMode.LLM)

    prompt_template = "Generate one comprehensive and difficult multiple choice question ,containing 5 options (A, B, C, D, E), that evaluates the understanding of key concepts or details presented. Format your response in JSON with the following structure: {\"Question\": \"Your Question here\", \"A\": \"First option here\", \"B\": \"Second option here\", \"C\": \"Third option here\", \"D\": \"Fourth option here\", \"E\": \"Fifth option here\", \"Correct Answer\": \"Correct option here(A, B, C, D, or E)\", \"Explanation\": \"Brief explanation for why the correct answer is the best choice\"}. Ensure the question is relevant and the options are plausible, with one correct answer and a brief explanation of why it's correct."
    context = node_text + prompt_template

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        # model = "gpt-4-0125-preview",
    response_format={ "type": "json_object" },
    messages=[
        {
    "role": "system",
    "content": " You are an advanced AI assistant specialized in creating challenging multiple-choice questions (MCQs) based on provided text. Your task is to analyze the content, identify key concepts or facts, and formulate MCQs that effectively test understanding of these elements. Each question should be accompanied by five options: one correct answer and four plausible but incorrect distractors. Strictly ensure your output is in a structured JSON format, with each MCQ including the question, options, and the correct answer clearly indicated."
        },
        {"role": "user", "content": context}
    ]
    )
    try:
        mcq_response = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error decoding the response from OpenAI")
    print("Json decoded successfully")

    try:
        mcq_id = insert_mcq(mcq_response)
    except:
        raise HTTPException(status_code=500, detail="Error inserting MCQ into database")
    # mcq_response["id"] = mcq_id  # Send this ID back to the user
    print("MCQ inserted successfully")
    print(mcq_id)
    return mcq_id
    # mcq_id = insert_mcq(mcq_response)
    # mcq_response["id"] = mcq_id  # Send this ID back to the user
    # # del mcq_response["Correct Answer"], mcq_response["Explanation"]  # Remove the correct answer and explanation from the response
    # return mcq_response

@app.post("/submit-answer/")
async def submit_answer(mcq_id: int = Body(...), user_answer: str = Body(...), current_user: User = Depends(get_current_user)):
    mcq_info = get_mcq_details(mcq_id)

    if mcq_info is None:
        raise HTTPException(status_code=404, detail="MCQ not found")

    if user_answer == mcq_info["correct_answer"]:
        return {"result": "Correct", "explanation": mcq_info["explanation"]}
    else:
        return {"result": "Incorrect", "correct_answer": mcq_info["correct_answer"], "explanation": mcq_info["explanation"]}

@app.get("/get-mcq/{mcq_id}")
async def get_mcq(mcq_id: int, current_user: User = Depends(get_current_user)):
    mcq_info = get_mcq_details(mcq_id)
    if mcq_info:
        return mcq_info
    raise HTTPException(status_code=404, detail="MCQ not found")

@app.post("/signup/", response_model=UserCreate)
async def signup(user_data: UserCreate):
    hashed_password = get_password_hash(user_data.password)
    user = create_user(user_data.username, user_data.email, hashed_password)
    if user is None:
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists. Please choose a different one."
        )
    return user_data

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
