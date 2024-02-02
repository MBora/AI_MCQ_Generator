from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text

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

# New Users table
users = Table('users', metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String(50), unique=True, nullable=False),
    Column('email', String(255), unique=True, nullable=False),
    Column('hashed_password', String(255), nullable=False)
)

metadata.create_all(engine)
