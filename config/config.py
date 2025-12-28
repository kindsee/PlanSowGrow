"""
Configuration management for PlanSowGrow application.

This module defines configuration classes for different environments
following Flask best practices.
"""
import os
from datetime import timedelta


class Config:
    """
    Base configuration class with common settings.
    
    All environment-specific configurations inherit from this class.
    """
    
    # Flask Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # SQLAlchemy Settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_ECHO = False
    
    # Database Connection Pool
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Application Settings
    ITEMS_PER_PAGE = 20
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration-specific settings."""
        pass


class DevelopmentConfig(Config):
    """Configuration for development environment."""
    
    DEBUG = True
    TESTING = False
    
    # Build database URI from environment variables
    DB_USER = os.environ.get('DATABASE_USER', 'root')
    DB_PASSWORD = os.environ.get('DATABASE_PASSWORD', '')
    DB_HOST = os.environ.get('DATABASE_HOST', 'localhost')
    DB_PORT = os.environ.get('DATABASE_PORT', '3306')
    DB_NAME = os.environ.get('DATABASE_NAME', 'plansowgrow_dev')
    
    SQLALCHEMY_DATABASE_URI = (
        f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    )
    
    SQLALCHEMY_ECHO = True  # Log SQL queries in development


class ProductionConfig(Config):
    """Configuration for production environment."""
    
    DEBUG = False
    TESTING = False
    
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        """Build database URI from environment variables."""
        DB_USER = os.environ.get('DATABASE_USER')
        DB_PASSWORD = os.environ.get('DATABASE_PASSWORD')
        DB_HOST = os.environ.get('DATABASE_HOST')
        DB_PORT = os.environ.get('DATABASE_PORT', '3306')
        DB_NAME = os.environ.get('DATABASE_NAME')
        
        if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
            raise ValueError("Database configuration incomplete in production")
        
        return f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    
    # Enhanced security for production
    SESSION_COOKIE_SECURE = True
    
    @staticmethod
    def init_app(app):
        """Initialize production-specific settings."""
        Config.init_app(app)
        
        # Log to syslog in production
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


class TestingConfig(Config):
    """Configuration for testing environment."""
    
    TESTING = True
    DEBUG = True
    
    # Use SQLite for faster testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Faster password hashing for tests
    BCRYPT_LOG_ROUNDS = 4
    
    # Override engine options for SQLite
    SQLALCHEMY_ENGINE_OPTIONS = {}


# Configuration dictionary mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
