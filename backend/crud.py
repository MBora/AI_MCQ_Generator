from sqlalchemy import insert
from database import engine, mcqs
from database import engine, mcqs, users
from sqlalchemy import select

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

def create_user(username: str, email: str, hashed_password: str):
    with engine.connect() as connection:
        # Check if the user already exists
        if get_user_by_username(username) is not None or get_user_by_email(email) is not None:
            return None

        transaction = connection.begin()
        try:
            ins_query = users.insert().values(
                username=username,
                email=email,
                hashed_password=hashed_password
            )
            connection.execute(ins_query)
            transaction.commit()
            return {"username": username, "email": email, "hashed_password": hashed_password}
        except Exception as e:
            transaction.rollback()
            print("Error during user insertion:", e)
            # Here you can add specific handling for unique constraint violations
            return None

def get_user_by_username(username: str):
    with engine.connect() as connection:
        query = select(users).where(users.c.username == username)  # Select the entire user row
        result = connection.execute(query).fetchone()
        return result

def get_user_by_email(email: str):
    with engine.connect() as connection:
        query = select(users.c.id).where(users.c.email == email)  # Select only the id column
        result = connection.execute(query).fetchone()
        return result
