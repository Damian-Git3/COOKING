import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SESSION_COOKIE_SECURE = False

class DevelopmentConfig(Config):
    DEBUG = True
    # encriptar esta madre
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
