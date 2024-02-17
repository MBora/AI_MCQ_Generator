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
from crud import fetch_quiz_details_by_id
from crud import fetch_quiz_history_for_user

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
        for file_name in os.listdir("./processed_data"):
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
        with open(f"./processed_data/{pkls[chapter_index]}", "rb") as f:
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
    processed_data_folder = "./processed_data"  # Adjust the path as necessary
    try:
        # List all .pkl files in the folder
        pkl_files = [file_name for file_name in os.listdir(processed_data_folder) if file_name.endswith(".pkl")]
        # print("pkl_files", pkl_files)
        return {"chapters": pkl_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing chapters: {str(e)}")


class UserRegister(BaseModel):
    email: str
    localId: str 
    
import logging

@app.post("/register-user")
async def register_user(user: UserRegister):
    existing_user = get_user_by_email(user.email)
    if existing_user:
        return {"uid": existing_user["uid"]}
    else:
        # Directly use the localId from Firebase
        user_id = insert_user({"uid": user.localId, "email": user.email})
        return {"uid": user.localId}

@app.post("/save-quiz-results/")
async def save_quiz_results(request: Request):
    body = await request.json()
    user_email = body.get('email')
    quiz_name = body.get('quiz_name')
    mcq_ids = body.get('mcq_ids')  # A list of MCQ IDs
    score = body.get('score')

    # Fetch user information using the email
    user_info = get_user_by_email_safe(user_email)
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")

    # Save quiz results to the database, including MCQ IDs
    quiz_id = save_quiz_result_to_db(user_info['uid'], quiz_name, json.dumps(mcq_ids), score)
    if quiz_id is not None:
        # If the quiz_id is not None, the insertion was successful
        return {"message": "Quiz saved successfully.", "quiz_id": quiz_id}
    else:
        # If the function returned None, an error occurred
        # This assumes that every failure is due to a duplicate quiz name, which might not always be the case
        # It's a more generic error response, not specifically tied to the IntegrityError
        raise HTTPException(status_code=400, detail="An error occurred while saving the quiz")

@app.get("/quiz-history/{user_uid}")
async def get_quiz_history(user_uid: str):
    # Fetch quiz history from the database for the given user UID
    # Make sure this function or query is correctly implemented
    quiz_history = fetch_quiz_history_for_user(user_uid)
    if quiz_history:
        return quiz_history
    else:
        raise HTTPException(status_code=404, detail="No quiz history found for the user")
    
@app.get("/quiz-details/{quiz_id}")
async def get_quiz_details(quiz_id: int):
    try:
        print("BEFORE", quiz_id)
        quiz_details = fetch_quiz_details_by_id(quiz_id)
        print("AFTER", quiz_details)
        if quiz_details:
            print("QUIZ DETAILS", quiz_details)
            # Directly iterate over quiz_data assuming it's already a list
            mcq_ids = quiz_details['quiz_data']
            print("MCQ IDs:", mcq_ids)
            
            mcq_details_list = []
            for mcq_id in mcq_ids:
                print("MCQ ID:", mcq_id)  # Print each MCQ ID
                mcq_details = get_mcq_details(mcq_id)
                if mcq_details:
                    mcq_details_list.append(mcq_details)
                else:
                    print(f"Details for MCQ ID {mcq_id} not found.")

            print("MCQ DETAILS", mcq_details_list)
            quiz_details['mcq_details'] = mcq_details_list
            return quiz_details
        else:
            return HTTPException(status_code=404, detail="Quiz details not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

