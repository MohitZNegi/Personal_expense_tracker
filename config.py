import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration — shared across all environments."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///expenses_dev.db"

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # in-memory, wiped after each test

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

config = {
    "development": DevelopmentConfig,
    "testing":     TestingConfig,
    "production":  ProductionConfig,
    "default":     DevelopmentConfig,
}