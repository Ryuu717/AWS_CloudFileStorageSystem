from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Config:
    AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    S3_BUCKET = os.getenv('S3_BUCKET')
    REGION = os.getenv('REGION')
