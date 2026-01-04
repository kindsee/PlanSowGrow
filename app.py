"""
Flask application initialization for PlanSowGrow.
"""
import os
from flask import Flask
from markupsafe import Markup
from extensions import db
import bleach


def create_app(config_name=None):
    """
    Application factory pattern.
    
    Args:
        config_name: Configuration name ('development', 'production', or None for default)
    
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    from config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Register Jinja2 filters
    @app.template_filter('safe_html')
    def safe_html_filter(text):
        """Sanitize HTML for safe rendering."""
        if not text:
            return ''
        
        # Allow common formatting tags and preserve line breaks
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 's', 'h1', 'h2', 'h3', 
                       'ul', 'ol', 'li', 'a', 'blockquote', 'code', 'pre']
        allowed_attrs = {'a': ['href', 'title'], '*': ['class']}
        
        cleaned = bleach.clean(
            text,
            tags=allowed_tags,
            attributes=allowed_attrs,
            strip=True
        )
        
        # Return as Markup object so Jinja2 doesn't escape it
        return Markup(cleaned)
    
    # Create tables within app context
    with app.app_context():
        # Import models to ensure they're registered
        import models
    
    # Register blueprints
    from routes import register_blueprints
    register_blueprints(app)
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5001, debug=True)
