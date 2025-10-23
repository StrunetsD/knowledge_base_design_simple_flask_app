import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()

class Config:
    DEBUG = bool(os.environ.get('DEBUG'))
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DB_HOST = os.environ.get('DB_HOST') 
    DB_PORT = os.environ.get('DB_PORT') 
    DB_NAME = os.environ.get('DB_NAME') 
    DB_USER = os.environ.get('DB_USER') 
    DB_PASSWORD = os.environ.get('DB_PASSWORD') 
    DB_URL=os.environ.get('DB_URL')



settings = Config()
