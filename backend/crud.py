#crud.py
from sqlalchemy import insert, select
from database import engine, mcqs, users, quiz_results
import uuid

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
            # Generate a unique UUID
            user_uuid = str(uuid.uuid4())
            ins_query = users.insert().values(
                uid=user_uuid,  # Use the generated UUID
                email=user_data["email"],
                # Add other fields as needed
            )
            result = connection.execute(ins_query)
            user_id = result.inserted_primary_key[0]
            transaction.commit()
            # Return both the internal user ID and the UUID
            return user_id, user_uuid
        except Exception as e:
            transaction.rollback()
            print("Error during user insertion:", e)
            return None, None

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
        # Prepare a SELECT statement
        query = select(users).where(users.c.email == email)
        result = connection.execute(query).fetchone()
        print(f"Result: {result}")
        print("Email", email)
        if result:
            # Convert the result into a dictionary for easier access
            user_info = {column: value for column, value in zip(result.keys(), result)}
            print(f"User Info: {user_info}")
            return user_info
        else:
            return None
        
from sqlalchemy import select

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



def save_quiz_result_to_db(user_uid, quiz_data, score):
    print(f"Preparing to save quiz result: UID: {user_uid}, Score: {score}, Quiz Data: {quiz_data}")
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            # Assuming 'quiz_history' is imported or accessible within this context
            ins_query = quiz_results.insert().values(
                user_uid=user_uid,
                quiz_data=quiz_data,
                score=score
            )
            result = connection.execute(ins_query)
            transaction.commit()
            return result.inserted_primary_key[0]  # Returning the primary key (id) of the inserted record
        except Exception as e:
            transaction.rollback()
            print(f"Error saving quiz result: {e}")
            return None
