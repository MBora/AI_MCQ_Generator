from sqlalchemy import create_engine, Table, MetaData, Column, Integer, String, Text

# Database configuration
DATABASE_URL = "mysql+pymysql://root:my-secret-pw@localhost:3306/newdatabase"
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Define your table structure
mcqs = Table('mcqs', metadata,
    Column('id', Integer, primary_key=True),
    Column('question', Text, nullable=False),
    Column('option_a', String(255), nullable=True),
    Column('option_b', String(255), nullable=True),
    Column('option_c', String(255), nullable=True),
    Column('option_d', String(255), nullable=True),
    Column('option_e', String(255), nullable=True),
    Column('correct_answer', String(255), nullable=False),
    Column('explanation', Text, nullable=False)
)
metadata.create_all(engine)


dummy_data = {
    "question": "What is 2 + 2?",
    "option_a": "3",
    "option_b": "4",
    "option_c": "5",
    "option_d": "6",
    "option_e": "7",
    "correct_answer": "B",
    "explanation": "2 + 2 equals 4."
}

def insert_dummy_mcq():
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(mcqs.insert(), dummy_data)
            transaction.commit()
            print("Dummy MCQ inserted and committed.")
        except Exception as e:
            print(f"Error during insertion: {e}")
            transaction.rollback()

if __name__ == "__main__":
    insert_dummy_mcq()
