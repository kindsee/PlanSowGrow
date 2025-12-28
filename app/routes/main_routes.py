"""
Main application routes.

This module contains the main routes for the application including
the home page and general navigation.
"""
from flask import Blueprint, render_template
from app.services import GardenService, SeasonService

# Create main blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """
    Home page showing overview of the application.
    
    Returns:
        Rendered home page template
    """
    # Get summary data for dashboard
    gardens = GardenService.get_active_gardens()
    current_season = SeasonService.get_current_season()
    
    return render_template(
        'index.html',
        garden_count=len(gardens),
        current_season=current_season
    )


@main_bp.route('/about')
def about():
    """
    About page with information about the application.
    
    Returns:
        Rendered about page template
    """
    return render_template('about.html')
