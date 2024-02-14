#database.py
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy import DateTime
import datetime

DATABASE_URL = "mysql+pymysql://root:my-secret-pw@localhost/mcq_database"
engine = create_engine(DATABASE_URL)
metadata = MetaData()

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

users = Table('users', metadata,
    Column('uid', String(255), primary_key=True),
    Column('email', String(255), nullable=False, unique=True),
    # Add other fields here as needed
)

quiz_results = Table('quiz_results', metadata,
    Column('id', Integer, primary_key=True),
    Column('user_uid', String(255), ForeignKey('users.uid')),
    Column('quiz_data', JSON),  # This will store quiz questions, options, and user answers
    Column('score', Integer),
    Column('timestamp', DateTime, default=datetime.datetime.utcnow)
)

metadata.create_all(engine)
