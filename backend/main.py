#main.py
import os
import openai
from openai import OpenAI
import llama_index.llms
import random
from fastapi import FastAPI, HTTPException, Query, Request
import pickle
from fastapi import Body
import json
import uuid
from pydantic import BaseModel
# Database stuff
from crud import insert_mcq, get_mcq_details, insert_user, get_user_by_email, save_quiz_result_to_db, get_user_by_email_safe
from database import engine, mcqs
import logging

# load OPENAI_API_KEY from .env file
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

from openai import OpenAI
client = OpenAI()
app = FastAPI()

from llama_index.schema import MetadataMode

@app.post("/generate-mcq/{chapter_index}")
async def generate_mcq(chapter_index: int = 0):
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
async def submit_answer(mcq_id: int = Body(...), user_answer: str = Body(...)):
    mcq_info = get_mcq_details(mcq_id)

    if mcq_info is None:
        raise HTTPException(status_code=404, detail="MCQ not found")

    print(f"User Answer: '{user_answer}'")
    print(f"Correct Answer: '{mcq_info['correct_answer']}'")

    if user_answer.strip() == mcq_info["correct_answer"].strip():
        return {"result": "Correct", "explanation": mcq_info["explanation"]}
    else:
        return {"result": "Incorrect", "correct_answer": mcq_info["correct_answer"], "explanation": mcq_info["explanation"]}

@app.get("/get-mcq/{mcq_id}")
async def get_mcq(mcq_id: int):
    mcq_info = get_mcq_details(mcq_id)
    if mcq_info:
        return mcq_info
    raise HTTPException(status_code=404, detail="MCQ not found")

@app.get("/list-chapters")
async def list_chapters():
    # Path to the processed_data folder
    processed_data_folder = "../processed_data"  # Adjust the path as necessary
    try:
        # List all .pkl files in the folder
        pkl_files = [file_name for file_name in os.listdir(processed_data_folder) if file_name.endswith(".pkl")]
        # print("pkl_files", pkl_files)
        return {"chapters": pkl_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing chapters: {str(e)}")


class UserRegister(BaseModel):
    email: str
import logging

@app.post("/register-user")
async def register_user(user: UserRegister):
    
    logger = logging.getLogger("uvicorn.info")
    logger.info(f"Registering user: {user.email}")
    print(f"Received registration request for email: {user.email}")
    # Assuming get_user_by_email and insert_user are properly defined in your backend
    print("USER EMAIL", user.email)
    existing_user = get_user_by_email(user.email)
    if existing_user:
        # User exists, return their existing UID
        return {"uid": existing_user["uid"]}
    else:
        # User does not exist, so generate a new UID (or use Firebase UID if available)
        user_uid = str(uuid.uuid4())
        # Insert the new user with this UID and email into the database
        user_id, user_uid = insert_user({"uid": user_uid, "email": user.email})
        if user_id:
            return {"uid": user_uid}
        else:
            raise HTTPException(status_code=500, detail="Error registering user")

@app.post("/save-quiz-results/")
async def save_quiz_results(request: Request):
    body = await request.json()
    print(f"Request body: {body}")
    
    # Adjusted to match the structure sent from Streamlit
    quiz_details = body.get('quiz_results')
    if not quiz_details:
        raise HTTPException(status_code=400, detail="Missing quiz results data")

    user_email = body.get('email')
    quiz_data = quiz_details.get('quiz_data')
    score = quiz_details.get('score')

    user_info = get_user_by_email_safe(user_email)
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")

    save_quiz_result_to_db(user_info['uid'], quiz_data, score)
    return {"message": "Quiz results saved successfully"}

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

