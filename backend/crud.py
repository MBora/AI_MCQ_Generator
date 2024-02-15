#crud.py
from sqlalchemy import insert, select
from database import engine, mcqs, users, quiz_results
import uuid
import json

def insert_mcq(mcq_data):
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            ins_query = mcqs.insert().values(
                question=mcq_data["Question"],
                option_a=mcq_data["A"],
                option_b=mcq_data["B"],
                option_c=mcq_data["C"],
                option_d=mcq_data["D"],
                option_e=mcq_data["E"],
                correct_answer=mcq_data["Correct Answer"],
                explanation=mcq_data["Explanation"]
            )
            result = connection.execute(ins_query)
            mcq_id = result.inserted_primary_key[0]
            transaction.commit()
            return mcq_id
        except Exception as e:
            transaction.rollback()  # Rollback in case of error
            print("Error during insertion:", e)
            return None
        
def get_mcq_details(mcq_id: int):
    with engine.connect() as connection:
        select_query = mcqs.select().where(mcqs.c.id == mcq_id)
        result = connection.execute(select_query).fetchone()
        if result:
            mcq_details = {
                "id": result[0],
                "question": result[1],
                "option_a": result[2],
                "option_b": result[3],
                "option_c": result[4],
                "option_d": result[5],
                "option_e": result[6],
                "correct_answer": result[7],
                "explanation": result[8]
            }
            return mcq_details
        else:
            return None

def insert_user(user_data):
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            # Use the localId from Firebase instead of generating a new UUID
            ins_query = users.insert().values(
                uid=user_data["uid"],  # Use the Firebase localId
                email=user_data["email"],
                # Add other fields as needed
            )
            result = connection.execute(ins_query)
            user_id = result.inserted_primary_key[0]
            transaction.commit()
            # Since we're directly using the provided UID, no need to return it again, just return the internal DB ID if needed
            return user_id
        except Exception as e:
            transaction.rollback()
            print("Error during user insertion:", e)
            return None

def get_user_by_uid(uid: str):
    with engine.connect() as connection:
        select_query = select(users).where(users.c.uid == uid)
        result = connection.execute(select_query).fetchone()
        if result:
            user_info = {column: value for column, value in zip(result.keys(), result)}
            return user_info
        else:
            return None

def get_user_by_email(email: str):
    with engine.connect() as connection:
        query = select(users).where(users.c.email == email)
        result = connection.execute(query).fetchone()
        print(f"Result: {result}")

        if result:
            # Use the _mapping attribute of RowProxy for a dictionary-like access
            user_info = dict(result._mapping)
            print(f"User Info: {user_info}")
            return user_info
        else:
            return None


def get_user_by_email_safe(email: str):
    with engine.connect() as connection:
        # Here's the corrected usage without the list
        query = select(users.c.uid, users.c.email).where(users.c.email == email)
        result = connection.execute(query).fetchone()
        print("RESULT", result)
        
        if result:
            # Safely construct a dictionary from the RowProxy
            user_info_safe = {
                "uid": result[0],  # UID
                "email": result[1]  # Email
            }
            print(f"Safely fetched user info: {user_info_safe}")
            return user_info_safe
        else:
            print(f"No user found with email: {email}")
            return None

def save_quiz_result_to_db(user_uid, quiz_name, mcq_ids_json, score):
    print(f"User UID: {user_uid}, Quiz Name: {quiz_name}, MCQ IDs JSON: {mcq_ids_json}, Score: {score}")
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            ins_query = quiz_results.insert().values(
                user_uid=user_uid,
                quiz_name=quiz_name,  # Include the quiz name in the insert values
                quiz_data=mcq_ids_json,
                score=score
            )
            result = connection.execute(ins_query)
            transaction.commit()
            print("Quiz result saved successfully.")
            return result.inserted_primary_key[0]  # Returning the primary key (id) of the inserted record
        except Exception as e:
            transaction.rollback()
            print(f"Error saving quiz result: {e}")
            return None

def fetch_quiz_history_for_user(user_uid: str):
    with engine.connect() as connection:
        # Correctly pass column objects as arguments to select()
        query = select(
            quiz_results.c.id, 
            quiz_results.c.quiz_name, 
            quiz_results.c.score, 
            quiz_results.c.timestamp
        ).where(quiz_results.c.user_uid == user_uid)

        result = connection.execute(query).fetchall()

        quiz_history = [
            {
                "id": row.id, 
                "quiz_name": row.quiz_name, 
                "score": row.score, 
                "timestamp": row.timestamp.isoformat() if row.timestamp else None
            } for row in result
        ]

        return quiz_history
    
def fetch_quiz_details_by_id(quiz_id: int):
    print("Fetching quiz details for ID:", quiz_id)
    with engine.connect() as connection:
        # Use the select function to build a query
        query = select(quiz_results).where(quiz_results.c.id == quiz_id)
        result = connection.execute(query).fetchone()
        
        if result:
            # Convert the result into a dictionary
            quiz_details = {
                "id": result.id,
                "user_uid": result.user_uid,
                "quiz_name": result.quiz_name,
                "quiz_data": result.quiz_data,
                "score": result.score,
                "timestamp": result.timestamp.isoformat() if result.timestamp else None
            }

            # Deserialize 'quiz_data' if necessary
            if quiz_details.get('quiz_data'):
                quiz_details['quiz_data'] = json.loads(quiz_details['quiz_data'])

            return quiz_details
        else:
            return None

