import os
from decouple import config
import re
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
url = config('DATABASE_URL')
if url.startswith('postgres://'):
    url = url.replace('postgres://', 'postgresql://', 1)

class Config:
    SECRET_KEY = config('SECRET_KEY', 'secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_SECRET_KEY = config('JWT_SECRET_KEY', 'topsecret')

class DevConfig(Config):
    DEBUG = config('DEBUG', cast=bool)
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
    
class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI =  'sqlite://'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI =  url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = config('DEBUG', False, cast=bool)

    

config_dict = {
    'dev': DevConfig,
    'prod': ProductionConfig,
    'test': TestConfig
}
