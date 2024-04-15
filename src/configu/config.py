import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SESSION_COOKIE_SECURE = False




class DevelopmentConfig(Config):
    DEBUG = True
    # encriptar esta madre
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
