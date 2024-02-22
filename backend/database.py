#database.py
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, ForeignKey, JSON, UniqueConstraint
from sqlalchemy import DateTime
import datetime
from sqlalchemy.sql import func
import os

DATABASE_URL = os.getenv("DATABASE_URL")
# DATABASE_URL = "mysql+pymysql://root:my-secret-pw@mysql-db/mydatabase"
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
    Column('quiz_name', String(255), nullable=False),
    Column('quiz_data', JSON),
    Column('score', Integer),
    Column('timestamp', DateTime, default=func.now()),
    UniqueConstraint('user_uid', 'quiz_name', name='uix_user_uid_quiz_name') 
)

metadata.create_all(engine)
