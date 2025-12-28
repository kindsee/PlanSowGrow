"""
Garden routes for handling HTTP requests.

This module defines routes for garden-related operations.
All business logic is delegated to GardenService, keeping routes thin.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.services import GardenService

# Create blueprint
garden_bp = Blueprint('gardens', __name__, url_prefix='/gardens')


@garden_bp.route('/')
def list_gardens():
    """
    Display list of all active gardens.
    
    Returns:
        Rendered template with list of gardens
    """
    gardens = GardenService.get_active_gardens()
    return render_template('gardens/list.html', gardens=gardens)


@garden_bp.route('/<int:garden_id>')
def view_garden(garden_id):
    """
    Display details of a specific garden.
    
    Args:
        garden_id (int): ID of the garden to view
        
    Returns:
        Rendered template with garden details
    """
    garden, beds = GardenService.get_garden_with_beds(garden_id)
    
    if not garden:
        flash('Garden not found', 'error')
        return redirect(url_for('gardens.list_gardens'))
    
    return render_template('gardens/view.html', garden=garden, beds=beds)


@garden_bp.route('/new', methods=['GET', 'POST'])
def create_garden():
    """
    Create a new garden.
    
    GET: Display the creation form
    POST: Process the form and create the garden
    
    Returns:
        Rendered form template or redirect to garden list
    """
    if request.method == 'POST':
        try:
            # Extract form data
            name = request.form.get('name')
            description = request.form.get('description')
            location = request.form.get('location')
            size_sqm = request.form.get('size_sqm')
            notes = request.form.get('notes')
            
            # Convert size to float if provided
            if size_sqm:
                size_sqm = float(size_sqm)
            else:
                size_sqm = None
            
            # Delegate to service for business logic
            garden = GardenService.create_garden(
                name=name,
                description=description,
                location=location,
                size_sqm=size_sqm,
                notes=notes
            )
            
            flash(f'Garden "{garden.name}" created successfully', 'success')
            return redirect(url_for('gardens.view_garden', garden_id=garden.id))
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash('An error occurred while creating the garden', 'error')
    
    return render_template('gardens/form.html', garden=None)


@garden_bp.route('/<int:garden_id>/edit', methods=['GET', 'POST'])
def edit_garden(garden_id):
    """
    Edit an existing garden.
    
    Args:
        garden_id (int): ID of the garden to edit
    
    Returns:
        Rendered form template or redirect to garden view
    """
    garden = GardenService.get_by_id(garden_id)
    
    if not garden:
        flash('Garden not found', 'error')
        return redirect(url_for('gardens.list_gardens'))
    
    if request.method == 'POST':
        try:
            # Extract form data
            data = {
                'name': request.form.get('name'),
                'description': request.form.get('description'),
                'location': request.form.get('location'),
                'notes': request.form.get('notes')
            }
            
            # Convert size to float if provided
            size_sqm = request.form.get('size_sqm')
            if size_sqm:
                data['size_sqm'] = float(size_sqm)
            
            # Delegate to service for business logic
            updated_garden = GardenService.update_garden(garden_id, **data)
            
            flash(f'Garden "{updated_garden.name}" updated successfully', 'success')
            return redirect(url_for('gardens.view_garden', garden_id=garden_id))
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash('An error occurred while updating the garden', 'error')
    
    return render_template('gardens/form.html', garden=garden)


@garden_bp.route('/<int:garden_id>/archive', methods=['POST'])
def archive_garden(garden_id):
    """
    Archive a garden (soft delete).
    
    Args:
        garden_id (int): ID of the garden to archive
        
    Returns:
        Redirect to garden list
    """
    try:
        result = GardenService.archive_garden(garden_id)
        
        if result:
            flash('Garden archived successfully', 'success')
        else:
            flash('Garden not found', 'error')
            
    except Exception as e:
        flash('An error occurred while archiving the garden', 'error')
    
    return redirect(url_for('gardens.list_gardens'))


# API endpoints for AJAX requests
@garden_bp.route('/api/gardens')
def api_list_gardens():
    """
    API endpoint to get all active gardens as JSON.
    
    Returns:
        JSON response with list of gardens
    """
    gardens = GardenService.get_active_gardens()
    return jsonify([garden.to_dict() for garden in gardens])


@garden_bp.route('/api/gardens/<int:garden_id>')
def api_get_garden(garden_id):
    """
    API endpoint to get a specific garden as JSON.
    
    Args:
        garden_id (int): ID of the garden
        
    Returns:
        JSON response with garden data
    """
    garden = GardenService.get_by_id(garden_id)
    
    if not garden:
        return jsonify({'error': 'Garden not found'}), 404
    
    return jsonify(garden.to_dict())
