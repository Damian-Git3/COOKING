import os
from sqlalchemy import create_engine


class Config:
    SECRET_KEY = "CLAVE SECRETA"
    SESSION_COOKIE_SECURE = False


class DevelopmentConfig(Config):
    DEBUG = True
    # encriptar esta madre
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://admin:admin@localhost:3306/cooking"
