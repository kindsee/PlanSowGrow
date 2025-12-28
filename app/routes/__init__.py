"""
Routes package for PlanSowGrow application.

This package contains all HTTP route definitions (controllers).
Routes are kept thin - they handle HTTP concerns only and delegate
all business logic to services.

Route responsibilities:
- Receive HTTP requests
- Extract and validate request data
- Call appropriate service methods
- Return HTTP responses (render templates, JSON, redirects)
- Handle HTTP-specific concerns (flash messages, status codes)
"""
from .main_routes import main_bp
from .garden_routes import garden_bp
from .season_routes import season_bp

__all__ = ['main_bp', 'garden_bp', 'season_bp']
