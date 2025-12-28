"""
Flask extensions initialization.
This module avoids circular imports by keeping extensions separate.
"""
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()
