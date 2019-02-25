import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    Testing = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = 'postgresql://'+os.environ['RDS_USERNAME']+":"+os.environ['RDS_PASSWORD']\
                              +"@"+os.environ['RDS_HOSTNAME']+":"+os.environ['RDS_PORT']+"/"+os.environ['RDS_DB_NAME']

class ProductionConfig(Config):
    DEBUG = False

class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class TestingConfig(Config):
    TESTING = True