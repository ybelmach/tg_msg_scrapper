from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config import DB_PORT, DB_NAME, DB_PASS, DB_USER, DB_HOST

DSN = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

engine = create_engine(DSN)

session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

# from psycopg2.extras import RealDictCursor
# from config import DB_PORT, DB_NAME, DB_PASS, DB_USER, DB_HOST
# import psycopg2
# import time
#
# while True:
#     try:
#         conn = psycopg2.connect(f"dbname={DB_NAME} user={DB_USER} password={DB_PASS} port={DB_PORT} host={DB_HOST}",
#                                 cursor_factory=RealDictCursor)
#         cursor = conn.cursor()
#         print(f"Database connection established")
#     except Exception as error:
#         print(f"Error while connecting to database: {error}.")
#         time.sleep(5)
