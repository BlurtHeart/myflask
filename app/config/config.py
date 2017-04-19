import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Can You Guess Out?'
    MAIL_SERVER = 'smtp.126.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[myflask]'
    FLASKY_MAIL_SENDER = 'myflask admin <%s>' %MAIL_USERNAME
    FLASKY_ADMIN = "administrator@test.com"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    FLASKY_ADMIN = "administrator@test.com"

config = {
    'development': DevelopmentConfig,
    'default':DevelopmentConfig,
    'testing':TestingConfig
}