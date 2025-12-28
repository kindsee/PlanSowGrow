"""
Season routes for handling HTTP requests.

This module defines routes for season-related operations.
All business logic is delegated to SeasonService.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.services import SeasonService

# Create blueprint
season_bp = Blueprint('seasons', __name__, url_prefix='/seasons')


@season_bp.route('/')
def list_seasons():
    """
    Display list of all seasons.
    
    Returns:
        Rendered template with list of seasons
    """
    seasons = SeasonService.get_all()
    active_seasons = SeasonService.get_active_seasons()
    return render_template('seasons/list.html', seasons=seasons, active_seasons=active_seasons)


@season_bp.route('/<int:season_id>')
def view_season(season_id):
    """
    Display details of a specific season.
    
    Args:
        season_id (int): ID of the season to view
        
    Returns:
        Rendered template with season details
    """
    season = SeasonService.get_by_id(season_id)
    
    if not season:
        flash('Season not found', 'error')
        return redirect(url_for('seasons.list_seasons'))
    
    return render_template('seasons/view.html', season=season)


@season_bp.route('/new', methods=['GET', 'POST'])
def create_season():
    """
    Create a new season.
    
    GET: Display the creation form
    POST: Process the form and create the season
    
    Returns:
        Rendered form template or redirect to season list
    """
    if request.method == 'POST':
        try:
            # Extract form data
            name = request.form.get('name')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date') or None
            description = request.form.get('description')
            notes = request.form.get('notes')
            
            # Delegate to service for business logic
            season = SeasonService.create_season(
                name=name,
                start_date=start_date,
                end_date=end_date,
                description=description,
                notes=notes
            )
            
            flash(f'Season "{season.name}" created successfully', 'success')
            return redirect(url_for('seasons.view_season', season_id=season.id))
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash('An error occurred while creating the season', 'error')
    
    return render_template('seasons/form.html', season=None)


@season_bp.route('/<int:season_id>/edit', methods=['GET', 'POST'])
def edit_season(season_id):
    """
    Edit an existing season.
    
    Args:
        season_id (int): ID of the season to edit
    
    Returns:
        Rendered form template or redirect to season view
    """
    season = SeasonService.get_by_id(season_id)
    
    if not season:
        flash('Season not found', 'error')
        return redirect(url_for('seasons.list_seasons'))
    
    if request.method == 'POST':
        try:
            # Extract form data
            data = {
                'name': request.form.get('name'),
                'description': request.form.get('description'),
                'notes': request.form.get('notes')
            }
            
            # Delegate to service for business logic
            updated_season = SeasonService.update(season_id, **data)
            
            flash(f'Season "{updated_season.name}" updated successfully', 'success')
            return redirect(url_for('seasons.view_season', season_id=season_id))
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash('An error occurred while updating the season', 'error')
    
    return render_template('seasons/form.html', season=season)


@season_bp.route('/<int:season_id>/close', methods=['POST'])
def close_season(season_id):
    """
    Close a season by setting its end date.
    
    Args:
        season_id (int): ID of the season to close
        
    Returns:
        Redirect to season view
    """
    try:
        end_date = request.form.get('end_date') or None
        season = SeasonService.close_season(season_id, end_date)
        
        if season:
            flash(f'Season "{season.name}" closed successfully', 'success')
        else:
            flash('Season not found', 'error')
            
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash('An error occurred while closing the season', 'error')
    
    return redirect(url_for('seasons.view_season', season_id=season_id))


@season_bp.route('/<int:season_id>/reopen', methods=['POST'])
def reopen_season(season_id):
    """
    Reopen a closed season.
    
    Args:
        season_id (int): ID of the season to reopen
        
    Returns:
        Redirect to season view
    """
    try:
        season = SeasonService.reopen_season(season_id)
        
        if season:
            flash(f'Season "{season.name}" reopened successfully', 'success')
        else:
            flash('Season not found', 'error')
            
    except Exception as e:
        flash('An error occurred while reopening the season', 'error')
    
    return redirect(url_for('seasons.view_season', season_id=season_id))


# API endpoints
@season_bp.route('/api/seasons')
def api_list_seasons():
    """
    API endpoint to get all seasons as JSON.
    
    Returns:
        JSON response with list of seasons
    """
    seasons = SeasonService.get_all()
    return jsonify([season.to_dict() for season in seasons])


@season_bp.route('/api/seasons/active')
def api_active_seasons():
    """
    API endpoint to get active seasons as JSON.
    
    Returns:
        JSON response with list of active seasons
    """
    seasons = SeasonService.get_active_seasons()
    return jsonify([season.to_dict() for season in seasons])
