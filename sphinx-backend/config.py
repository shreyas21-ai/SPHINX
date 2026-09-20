import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    """Base Configuration Class"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-dev-secret-key-must-change')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'default-jwt-secret-key-must-change')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # Cryptographic settings
    SPHINX_AES_SECRET_KEY = os.environ.get('SPHINX_AES_SECRET_KEY')
    SPHINX_HMAC_SECRET_KEY = os.environ.get('SPHINX_HMAC_SECRET_KEY')

    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Bootstrap settings
    BOOTSTRAP_ADMIN_EMAIL = os.environ.get('BOOTSTRAP_ADMIN_EMAIL', 'admin@sphinxhealth.com')
    BOOTSTRAP_ADMIN_PASSWORD = os.environ.get('BOOTSTRAP_ADMIN_PASSWORD', 'AdminSecurePass123!')


class DevelopmentConfig(Config):
    """Development Configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:root@localhost:3306/sphinx')


class TestingConfig(Config):
    """Testing Configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL', 'mysql+pymysql://root:root@localhost:3306/sphinx_test')
    # Use deterministic 32-byte test keys for tests if env is not set
    SPHINX_AES_SECRET_KEY = os.environ.get('SPHINX_AES_SECRET_KEY', 'MTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTI=')
    SPHINX_HMAC_SECRET_KEY = os.environ.get('SPHINX_HMAC_SECRET_KEY', 'MTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTI=')


class ProductionConfig(Config):
    """Production Configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
