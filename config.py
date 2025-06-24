from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv()

class Config:
    LOGGING_LEVEL = os.environ.get('LOGGING_LEVEL')
    DB_URL = os.environ.get("DATABASE_URL")
    VALIDATE_URL = os.environ.get("VALIDATE_URL")
