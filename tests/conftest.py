"""
Pytest configuration for PlanSowGrow tests.

This module provides fixtures and configuration for testing.
"""
import pytest
from app import create_app
from app.models.base import db as _db


@pytest.fixture(scope='session')
def app():
    """
    Create application instance for testing.
    
    Returns:
        Flask: Application instance configured for testing
    """
    app = create_app('testing')
    return app


@pytest.fixture(scope='function')
def client(app):
    """
    Create test client for making requests.
    
    Args:
        app: Application fixture
        
    Returns:
        FlaskClient: Test client instance
    """
    return app.test_client()


@pytest.fixture(scope='function')
def db(app):
    """
    Create database for testing.
    
    Sets up a clean database for each test and tears it down afterwards.
    
    Args:
        app: Application fixture
        
    Yields:
        SQLAlchemy: Database instance
    """
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture(scope='function')
def session(db):
    """
    Create database session for testing.
    
    Args:
        db: Database fixture
        
    Returns:
        Session: Database session
    """
    return db.session
