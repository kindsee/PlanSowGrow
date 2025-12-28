"""
HTTP routes for PlanSowGrow application.
Routes should contain NO business logic - delegate to services immediately.
"""
from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash
import services


# Create blueprints for logical route grouping
beds_bp = Blueprint('beds', __name__, url_prefix='/beds')
plants_bp = Blueprint('plants', __name__, url_prefix='/plants')
cultures_bp = Blueprint('cultures', __name__, url_prefix='/cultures')
pests_bp = Blueprint('pests', __name__, url_prefix='/pests')
treatments_bp = Blueprint('treatments', __name__, url_prefix='/treatments')
care_bp = Blueprint('care', __name__, url_prefix='/care')
calendar_bp = Blueprint('calendar', __name__, url_prefix='/calendar')


# ========== Main Routes ==========

@beds_bp.route('/')
def index():
    """Homepage - redirect to beds list."""
    return redirect(url_for('beds.list_beds'))


# ========== Raised Bed Routes ==========

@beds_bp.route('/list')
def list_beds():
    """List all raised beds."""
    beds = services.get_all_beds()
    return render_template('beds/list.html', beds=beds)


@beds_bp.route('/create', methods=['GET', 'POST'])
def create_bed():
    """Create a new raised bed."""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        location = request.form.get('location')
        
        bed = services.create_bed(name, description, location)
        flash(f'Bed "{bed.name}" created successfully!', 'success')
        return redirect(url_for('beds.list_beds'))
    
    return render_template('beds/create.html')


@beds_bp.route('/<int:bed_id>')
def view_bed(bed_id):
    """View a single raised bed with its cultures."""
    bed = services.get_bed_by_id(bed_id)
    if not bed:
        flash('Bed not found', 'error')
        return redirect(url_for('beds.list_beds'))
    
    cultures = services.get_cultures_by_bed(bed_id, include_inactive=True)
    return render_template('beds/view.html', bed=bed, cultures=cultures)


# ========== Plant Routes ==========

@plants_bp.route('/list')
def list_plants():
    """List all plants in catalog."""
    plants = services.get_all_plants()
    return render_template('plants/list.html', plants=plants)


@plants_bp.route('/create', methods=['GET', 'POST'])
def create_plant():
    """Create a new plant in catalog."""
    if request.method == 'POST':
        name = request.form.get('name')
        scientific_name = request.form.get('scientific_name')
        description = request.form.get('description')
        growth_days = request.form.get('growth_days', type=int)
        harvest_period_days = request.form.get('harvest_period_days', type=int)
        notes = request.form.get('notes')
        
        plant = services.create_plant(
            name, scientific_name, description,
            growth_days, harvest_period_days, notes
        )
        flash(f'Plant "{plant.name}" created successfully!', 'success')
        return redirect(url_for('plants.list_plants'))
    
    return render_template('plants/create.html')


@plants_bp.route('/<int:plant_id>')
def view_plant(plant_id):
    """View a single plant with details."""
    plant = services.get_plant_by_id(plant_id)
    if not plant:
        flash('Plant not found', 'error')
        return redirect(url_for('plants.list_plants'))
    
    pests = services.get_pests_for_plant(plant_id)
    return render_template('plants/view.html', plant=plant, pests=pests)


# ========== Culture Routes ==========

@cultures_bp.route('/list')
def list_cultures():
    """List all active cultures."""
    cultures = services.get_active_cultures()
    return render_template('cultures/list.html', cultures=cultures)


@cultures_bp.route('/create', methods=['GET', 'POST'])
def create_culture():
    """Create a new culture (planting)."""
    if request.method == 'POST':
        bed_id = request.form.get('bed_id', type=int)
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        start_type = request.form.get('start_type')
        plant_ids = request.form.getlist('plant_ids', type=int)
        notes = request.form.get('notes')
        
        culture = services.create_culture(bed_id, start_date, start_type, plant_ids, notes=notes)
        
        # Generate calendar events for this culture
        services.generate_calendar_events_for_culture(culture.id)
        
        flash(f'Culture created successfully in {culture.bed.name}!', 'success')
        return redirect(url_for('cultures.list_cultures'))
    
    beds = services.get_all_beds()
    plants = services.get_all_plants()
    return render_template('cultures/create.html', beds=beds, plants=plants)


@cultures_bp.route('/<int:culture_id>')
def view_culture(culture_id):
    """View a single culture with details."""
    culture = services.get_culture_by_id(culture_id)
    if not culture:
        flash('Culture not found', 'error')
        return redirect(url_for('cultures.list_cultures'))
    
    return render_template('cultures/view.html', culture=culture)


@cultures_bp.route('/<int:culture_id>/close', methods=['POST'])
def close_culture(culture_id):
    """Close a culture."""
    end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date() if request.form.get('end_date') else None
    culture = services.close_culture(culture_id, end_date)
    
    if culture:
        flash(f'Culture closed successfully!', 'success')
    else:
        flash('Culture not found', 'error')
    
    return redirect(url_for('cultures.list_cultures'))


# ========== Calendar Routes ==========

@calendar_bp.route('/')
def view_calendar():
    """View garden calendar with upcoming events."""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    events = services.get_calendar_events(start_date, end_date)
    return render_template('calendar/view.html', events=events)


@calendar_bp.route('/event/<int:event_id>/complete', methods=['POST'])
def complete_event(event_id):
    """Mark a calendar event as completed."""
    event = services.mark_event_completed(event_id)
    
    if event:
        flash('Event marked as completed!', 'success')
    else:
        flash('Event not found', 'error')
    
    return redirect(url_for('calendar.view_calendar'))


# ========== Pest Routes ==========

@pests_bp.route('/list')
def list_pests():
    """List all pests."""
    pests = services.get_all_pests()
    return render_template('pests/list.html', pests=pests)


@pests_bp.route('/create', methods=['GET', 'POST'])
def create_pest():
    """Create a new pest in catalog."""
    if request.method == 'POST':
        name = request.form.get('name')
        scientific_name = request.form.get('scientific_name')
        description = request.form.get('description')
        symptoms = request.form.get('symptoms')
        
        pest = services.create_pest(name, scientific_name, description, symptoms)
        flash(f'Pest "{pest.name}" created successfully!', 'success')
        return redirect(url_for('pests.list_pests'))
    
    return render_template('pests/create.html')


# ========== Treatment Routes ==========

@treatments_bp.route('/list')
def list_treatments():
    """List all treatments."""
    treatments = services.get_all_treatments()
    return render_template('treatments/list.html', treatments=treatments)


@treatments_bp.route('/create', methods=['GET', 'POST'])
def create_treatment():
    """Create a new treatment."""
    if request.method == 'POST':
        pest_id = request.form.get('pest_id', type=int)
        name = request.form.get('name')
        description = request.form.get('description')
        application_method = request.form.get('application_method')
        frequency_days = request.form.get('frequency_days', type=int)
        
        treatment = services.create_treatment(
            pest_id, name, description, application_method, frequency_days
        )
        flash(f'Treatment "{treatment.name}" created successfully!', 'success')
        return redirect(url_for('treatments.list_treatments'))
    
    pests = services.get_all_pests()
    return render_template('treatments/create.html', pests=pests)


# ========== Care Action Routes ==========

@care_bp.route('/list')
def list_care_actions():
    """List all care actions."""
    care_actions = services.get_all_care_actions()
    return render_template('care/list.html', care_actions=care_actions)


@care_bp.route('/create', methods=['GET', 'POST'])
def create_care_action():
    """Create a new care action."""
    if request.method == 'POST':
        name = request.form.get('name')
        action_type = request.form.get('action_type')
        description = request.form.get('description')
        
        care_action = services.create_care_action(name, action_type, description)
        flash(f'Care action "{care_action.name}" created successfully!', 'success')
        return redirect(url_for('care.list_care_actions'))
    
    return render_template('care/create.html')


def register_blueprints(app):
    """Register all blueprints with the Flask app."""
    app.register_blueprint(beds_bp)
    app.register_blueprint(plants_bp)
    app.register_blueprint(cultures_bp)
    app.register_blueprint(pests_bp)
    app.register_blueprint(treatments_bp)
    app.register_blueprint(care_bp)
    app.register_blueprint(calendar_bp)
    
    # Register root route
    @app.route('/')
    def index():
        return redirect(url_for('beds.list_beds'))
