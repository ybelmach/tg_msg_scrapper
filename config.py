import os

from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
MSG_NUM = os.getenv("MSG_NUM")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MAX_WORDS_NUM = int(os.getenv("MAX_WORDS_NUM"))
