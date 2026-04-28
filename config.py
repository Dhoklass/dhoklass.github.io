import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'glitchfix_super_secret_2024')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '851688')   
    MYSQL_DB = os.environ.get('MYSQL_DB', 'glitchfix_db')
    MYSQL_CURSORCLASS = 'DictCursor'
