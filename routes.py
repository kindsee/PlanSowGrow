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
    active_cultures = [c for c in cultures if c.is_active]
    
    # Get events for all cultures in this bed
    bed_events = services.get_bed_events_with_status(bed_id)
    
    return render_template('beds/view.html', 
                         bed=bed, 
                         cultures=cultures, 
                         active_cultures=active_cultures,
                         events=bed_events)


@beds_bp.route('/<int:bed_id>/edit', methods=['GET', 'POST'])
def edit_bed(bed_id):
    """Edit an existing raised bed."""
    bed = services.get_bed_by_id(bed_id)
    if not bed:
        flash('Bancal no encontrado', 'error')
        return redirect(url_for('beds.list_beds'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        location = request.form.get('location')
        
        services.update_bed(bed_id, name=name, description=description, location=location)
        flash(f'Bancal "{name}" actualizado correctamente!', 'success')
        return redirect(url_for('beds.view_bed', bed_id=bed_id))
    
    return render_template('beds/edit.html', bed=bed)


@beds_bp.route('/<int:bed_id>/deactivate', methods=['POST'])
def deactivate_bed_route(bed_id):
    """Deactivate a raised bed (preserve history, don't delete)."""
    bed = services.deactivate_bed(bed_id)
    if bed:
        flash(f'Bancal "{bed.name}" desactivado correctamente', 'success')
    else:
        flash('Bancal no encontrado', 'error')
    
    return redirect(url_for('beds.list_beds'))


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
        icon = request.form.get('icon', '🌱')
        scientific_name = request.form.get('scientific_name')
        description = request.form.get('description')
        growth_days = request.form.get('growth_days', type=int)
        harvest_period_days = request.form.get('harvest_period_days', type=int)
        notes = request.form.get('notes')
        
        plant = services.create_plant(
            name, icon, scientific_name, description,
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
    cares = services.get_cares_for_plant(plant_id)
    return render_template('plants/view.html', plant=plant, pests=pests, cares=cares)


@plants_bp.route('/<int:plant_id>/edit', methods=['GET', 'POST'])
def edit_plant(plant_id):
    """Edit an existing plant."""
    plant = services.get_plant_by_id(plant_id)
    if not plant:
        flash('Planta no encontrada', 'error')
        return redirect(url_for('plants.list_plants'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        icon = request.form.get('icon', '🌱')
        scientific_name = request.form.get('scientific_name')
        description = request.form.get('description')
        growth_days = request.form.get('growth_days', type=int)
        harvest_period_days = request.form.get('harvest_period_days', type=int)
        notes = request.form.get('notes')
        
        services.update_plant(
            plant_id, name=name, icon=icon, scientific_name=scientific_name,
            description=description, growth_days=growth_days,
            harvest_period_days=harvest_period_days, notes=notes
        )
        flash(f'Planta "{name}" actualizada correctamente!', 'success')
        return redirect(url_for('plants.view_plant', plant_id=plant_id))
    
    # Load associated pests and all available pests
    plant_pests = services.get_pests_for_plant(plant_id)
    all_pests = services.get_all_pests()
    
    # Load associated cares and all available care actions
    plant_cares = services.get_cares_for_plant(plant_id)
    all_cares = services.get_all_care_actions()
    
    return render_template('plants/edit.html', plant=plant, 
                         plant_pests=plant_pests, all_pests=all_pests,
                         plant_cares=plant_cares, all_cares=all_cares)


@plants_bp.route('/<int:plant_id>/add_pest', methods=['POST'])
def add_pest(plant_id):
    """Add a pest association to a plant."""
    plant = services.get_plant_by_id(plant_id)
    if not plant:
        flash('Planta no encontrada', 'error')
        return redirect(url_for('plants.list_plants'))
    
    pest_id = request.form.get('pest_id', type=int)
    severity = request.form.get('severity', 'medium')
    notes = request.form.get('notes', '')
    
    if not pest_id:
        flash('Debes seleccionar una plaga', 'error')
        return redirect(url_for('plants.edit_plant', plant_id=plant_id))
    
    try:
        services.add_pest_to_plant(plant_id, pest_id, severity, notes)
        pest = services.get_pest_by_id(pest_id)
        flash(f'Plaga "{pest.name}" asociada correctamente', 'success')
    except Exception as e:
        flash(f'Error al asociar la plaga: {str(e)}', 'error')
    
    return redirect(url_for('plants.edit_plant', plant_id=plant_id))


@plants_bp.route('/<int:plant_id>/remove_pest', methods=['POST'])
def remove_pest(plant_id):
    """Remove a pest association from a plant."""
    plant = services.get_plant_by_id(plant_id)
    if not plant:
        flash('Planta no encontrada', 'error')
        return redirect(url_for('plants.list_plants'))
    
    pest_id = request.form.get('pest_id', type=int)
    
    if not pest_id:
        flash('Plaga no especificada', 'error')
        return redirect(url_for('plants.edit_plant', plant_id=plant_id))


@plants_bp.route('/<int:plant_id>/add_care', methods=['POST'])
def add_care(plant_id):
    """Add a care action association to a plant."""
    plant = services.get_plant_by_id(plant_id)
    if not plant:
        flash('Planta no encontrada', 'error')
        return redirect(url_for('plants.list_plants'))
    
    care_action_id = request.form.get('care_action_id', type=int)
    days_after_planting = request.form.get('days_after_planting', type=int)
    frequency_days = request.form.get('frequency_days', type=int)
    notes = request.form.get('notes', '')
    
    if not care_action_id:
        flash('Debes seleccionar un cuidado', 'error')
        return redirect(url_for('plants.edit_plant', plant_id=plant_id))
    
    try:
        services.add_care_to_plant(plant_id, care_action_id, days_after_planting, frequency_days, notes)
        care = services.get_care_action_by_id(care_action_id)
        flash(f'Cuidado "{care.name}" asociado correctamente', 'success')
    except Exception as e:
        flash(f'Error al asociar el cuidado: {str(e)}', 'error')
    
    return redirect(url_for('plants.edit_plant', plant_id=plant_id))


@plants_bp.route('/<int:plant_id>/remove_care', methods=['POST'])
def remove_care(plant_id):
    """Remove a care action association from a plant."""
    plant = services.get_plant_by_id(plant_id)
    if not plant:
        flash('Planta no encontrada', 'error')
        return redirect(url_for('plants.list_plants'))
    
    care_action_id = request.form.get('care_action_id', type=int)
    
    if not care_action_id:
        flash('Cuidado no especificado', 'error')
        return redirect(url_for('plants.edit_plant', plant_id=plant_id))
    
    try:
        if services.remove_pest_from_plant(plant_id, pest_id):
            pest = services.get_pest_by_id(pest_id)
            flash(f'Plaga "{pest.name}" desasociada correctamente', 'success')
        else:
            flash('La asociación no existe', 'warning')
    except Exception as e:
        flash(f'Error al eliminar la asociación: {str(e)}', 'error')
    
    return redirect(url_for('plants.edit_plant', plant_id=plant_id))


# ========== Culture Routes ==========

@cultures_bp.route('/list')
def list_cultures():
    """List all active cultures."""
    active_cultures = services.get_active_cultures()
    
    # Add progress info to each culture
    cultures_with_progress = []
    for culture in active_cultures:
        progress = services.get_culture_progress(culture)
        cultures_with_progress.append({
            'culture': culture,
            'progress': progress
        })
    
    return render_template('cultures/list.html', 
                         cultures=cultures_with_progress,
                         today=date.today().isoformat())


@cultures_bp.route('/create', methods=['GET', 'POST'])
def create_culture():
    """Create a new culture (planting)."""
    if request.method == 'POST':
        bed_id = request.form.get('bed_id', type=int)
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        start_type = request.form.get('start_type')
        plant_ids = request.form.getlist('plant_ids', type=int)
        
        # Get quantities and visual layout for each plant
        quantities_planted = []
        quantities_grown = []
        row_positions = []
        spacing_cms = []
        alignments = []
        
        for plant_id in plant_ids:
            qty_planted = request.form.get(f'qty_planted_{plant_id}', type=int) or 1
            qty_grown = request.form.get(f'qty_grown_{plant_id}', type=int) or 1
            row_pos = request.form.get(f'row_position_{plant_id}') or 'central'
            spacing = request.form.get(f'spacing_cm_{plant_id}', type=int) or 30
            alignment = request.form.get(f'alignment_{plant_id}') or 'center'
            
            quantities_planted.append(qty_planted)
            quantities_grown.append(qty_grown)
            row_positions.append(row_pos)
            spacing_cms.append(spacing)
            alignments.append(alignment)
        
        notes = request.form.get('notes')
        
        culture = services.create_culture(
            bed_id, start_date, start_type, plant_ids,
            quantities_planted, quantities_grown, 
            row_positions, spacing_cms, alignments,
            notes=notes
        )
        
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
    
    # Get progress information
    progress = services.get_culture_progress(culture)
    
    # Get assigned treatments and cares
    culture_treatments = services.get_culture_treatments(culture_id)
    culture_cares = services.get_culture_cares(culture_id)
    
    # Get events with status (pending/completed)
    events = services.get_culture_events_with_status(culture_id)
    
    # Get potential pests and relevant treatments
    potential_pests = services.get_culture_potential_pests(culture_id)
    relevant_treatments = services.get_relevant_treatments_for_culture(culture_id)
    
    return render_template('cultures/view.html', culture=culture, 
                          progress=progress, 
                          treatments=culture_treatments,
                          cares=culture_cares,
                          events=events,
                          potential_pests=potential_pests,
                          relevant_treatments=relevant_treatments,
                          today=date.today().isoformat())


@cultures_bp.route('/<int:culture_id>/edit', methods=['GET', 'POST'])
def edit_culture(culture_id):
    """Edit culture information and plant distribution."""
    culture = services.get_culture_by_id(culture_id)
    if not culture:
        flash('Cultivo no encontrado', 'error')
        return redirect(url_for('cultures.list_cultures'))
    
    if request.method == 'POST':
        # Update basic culture information
        bed_id = request.form.get('bed_id', type=int)
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        start_type = request.form.get('start_type')
        notes = request.form.get('notes')
        
        if bed_id:
            culture.bed_id = bed_id
        if start_date_str:
            culture.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        if end_date_str:
            culture.end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            culture.is_active = False
        else:
            culture.end_date = None
            culture.is_active = True
        if start_type:
            culture.start_type = start_type
        if notes is not None:
            culture.notes = notes
        
        # Update each culture_plant distribution
        for cp in culture.plants:
            qty_planted = request.form.get(f'qty_planted_{cp.id}', type=int)
            qty_grown = request.form.get(f'qty_grown_{cp.id}', type=int)
            row_pos = request.form.get(f'row_position_{cp.id}')
            spacing = request.form.get(f'spacing_cm_{cp.id}', type=int)
            alignment = request.form.get(f'alignment_{cp.id}')
            
            if qty_planted:
                cp.quantity_planted = qty_planted
            if qty_grown is not None:
                cp.quantity_grown = qty_grown
            if row_pos:
                cp.row_position = row_pos
            if spacing:
                cp.spacing_cm = spacing
            if alignment:
                cp.alignment = alignment
        
        from extensions import db
        db.session.commit()
        
        flash('Cultivo actualizado correctamente!', 'success')
        return redirect(url_for('cultures.view_culture', culture_id=culture_id))
    
    # GET request - show form
    beds = services.get_all_beds()
    return render_template('cultures/edit.html', culture=culture, beds=beds)


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


@cultures_bp.route('/<int:culture_id>/delete', methods=['POST'])
def delete_culture(culture_id):
    """Delete a culture permanently."""
    culture = services.get_culture_by_id(culture_id)
    if not culture:
        flash('Cultivo no encontrado', 'error')
        return redirect(url_for('cultures.list_cultures'))
    
    bed_name = culture.bed.name
    
    # Delete the culture (cascade will handle related records)
    from extensions import db
    db.session.delete(culture)
    db.session.commit()
    
    flash(f'Cultivo eliminado del bancal {bed_name}', 'success')
    return redirect(url_for('cultures.list_cultures'))


@cultures_bp.route('/<int:culture_id>/add-treatment', methods=['GET', 'POST'])
def add_treatment_to_culture(culture_id):
    """Add a treatment to a culture."""
    culture = services.get_culture_by_id(culture_id)
    
    if not culture:
        flash('Culture not found', 'error')
        return redirect(url_for('cultures.list_cultures'))
    
    if request.method == 'POST':
        treatment_id = int(request.form.get('treatment_id'))
        start_date_str = request.form.get('start_date')
        frequency_days = request.form.get('frequency_days')
        notes = request.form.get('notes')
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        frequency = int(frequency_days) if frequency_days else None
        
        culture_treatment = services.add_treatment_to_culture(
            culture_id=culture_id,
            treatment_id=treatment_id,
            start_date=start_date,
            frequency_days=frequency,
            notes=notes
        )
        
        if culture_treatment:
            flash('Treatment added successfully!', 'success')
            return redirect(url_for('cultures.view_culture', culture_id=culture_id))
        else:
            flash('Error adding treatment. Check that start date is not before culture start date.', 'error')
    
    # GET request - show form
    treatments = services.get_all_treatments()
    relevant_treatments = services.get_relevant_treatments_for_culture(culture_id)
    return render_template('cultures/add_treatment.html', 
                         culture=culture,
                         treatments=treatments,
                         relevant_treatments=relevant_treatments)


@cultures_bp.route('/<int:culture_id>/add-care', methods=['GET', 'POST'])
def add_care_to_culture(culture_id):
    """Add a care action to a culture."""
    culture = services.get_culture_by_id(culture_id)
    
    if not culture:
        flash('Culture not found', 'error')
        return redirect(url_for('cultures.list_cultures'))
    
    if request.method == 'POST':
        care_action_id = int(request.form.get('care_action_id'))
        scheduled_date_str = request.form.get('scheduled_date')
        frequency_days = request.form.get('frequency_days')
        notes = request.form.get('notes')
        
        scheduled_date = datetime.strptime(scheduled_date_str, '%Y-%m-%d').date()
        frequency = int(frequency_days) if frequency_days else None
        
        culture_care = services.add_care_to_culture(
            culture_id=culture_id,
            care_action_id=care_action_id,
            scheduled_date=scheduled_date,
            frequency_days=frequency,
            notes=notes
        )
        
        if culture_care:
            flash('Care action added successfully!', 'success')
            return redirect(url_for('cultures.view_culture', culture_id=culture_id))
        else:
            flash('Error adding care action. Check that scheduled date is not before culture start date.', 'error')
    
    # GET request - show form
    care_actions = services.get_all_care_actions()
    return render_template('cultures/add_care.html', 
                         culture=culture,
                         care_actions=care_actions)


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


@pests_bp.route('/<int:pest_id>/edit', methods=['GET', 'POST'])
def edit_pest(pest_id):
    """Edit an existing pest."""
    pest = services.get_pest_by_id(pest_id)
    if not pest:
        flash('Plaga no encontrada', 'error')
        return redirect(url_for('pests.list_pests'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        scientific_name = request.form.get('scientific_name')
        description = request.form.get('description')
        symptoms = request.form.get('symptoms')
        
        services.update_pest(pest_id, name=name, scientific_name=scientific_name,
                           description=description, symptoms=symptoms)
        flash(f'Plaga "{name}" actualizada correctamente!', 'success')
        return redirect(url_for('pests.edit_pest', pest_id=pest_id))
    
    # Get treatments for this pest
    pest_treatments = services.get_treatments_for_pest(pest_id)
    return render_template('pests/edit.html', pest=pest, pest_treatments=pest_treatments)
    pest_treatments = services.get_treatments_for_pest(pest_id)
    return render_template('pests/edit.html', pest=pest, pest_treatments=pest_treatments)


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
        name = request.form.get('name')
        description = request.form.get('description')
        application_method = request.form.get('application_method')
        frequency_days = request.form.get('frequency_days', type=int)
        
        treatment = services.create_treatment(
            name, description, application_method, frequency_days
        )
        flash(f'Tratamiento "{treatment.name}" creado correctamente! Ahora puedes asociarle plagas.', 'success')
        return redirect(url_for('treatments.edit_treatment', treatment_id=treatment.id))
    
    pests = services.get_all_pests()
    return render_template('treatments/create.html', pests=pests)


@treatments_bp.route('/<int:treatment_id>/edit', methods=['GET', 'POST'])
def edit_treatment(treatment_id):
    """Edit an existing treatment."""
    treatment = services.get_treatment_by_id(treatment_id)
    if not treatment:
        flash('Tratamiento no encontrado', 'error')
        return redirect(url_for('treatments.list_treatments'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        application_method = request.form.get('application_method')
        frequency_days = request.form.get('frequency_days', type=int)
        
        services.update_treatment(treatment_id, name=name,
                                description=description, application_method=application_method,
                                frequency_days=frequency_days)
        flash(f'Tratamiento "{name}" actualizado correctamente!', 'success')
        return redirect(url_for('treatments.edit_treatment', treatment_id=treatment_id))
    
    all_pests = services.get_all_pests()
    treatment_pests = services.get_pests_for_treatment(treatment_id)
    return render_template('treatments/edit.html', treatment=treatment, 
                          all_pests=all_pests, treatment_pests=treatment_pests)


@treatments_bp.route('/<int:treatment_id>/add_pest', methods=['POST'])
def add_pest(treatment_id):
    """Add a pest to a treatment."""
    treatment = services.get_treatment_by_id(treatment_id)
    if not treatment:
        flash('Tratamiento no encontrado', 'error')
        return redirect(url_for('treatments.list_treatments'))
    
    pest_id = request.form.get('pest_id', type=int)
    effectiveness = request.form.get('effectiveness', 'high')
    notes = request.form.get('notes')
    
    services.add_pest_to_treatment(treatment_id, pest_id, effectiveness, notes)
    flash('Plaga añadida al tratamiento correctamente!', 'success')
    return redirect(url_for('treatments.edit_treatment', treatment_id=treatment_id))


@treatments_bp.route('/<int:treatment_id>/remove_pest/<int:pest_id>', methods=['POST'])
def remove_pest(treatment_id, pest_id):
    """Remove a pest from a treatment."""
    services.remove_pest_from_treatment(treatment_id, pest_id)
    flash('Plaga eliminada del tratamiento', 'success')
    return redirect(url_for('treatments.edit_treatment', treatment_id=treatment_id))


@care_bp.route('/<int:care_id>/edit', methods=['GET', 'POST'])
def edit_care_action(care_id):
    """Edit an existing care action."""
    care_action = services.get_care_action_by_id(care_id)
    if not care_action:
        flash('Acción de cuidado no encontrada', 'error')
        return redirect(url_for('care.list_care_actions'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        action_type = request.form.get('action_type')
        description = request.form.get('description')
        
        services.update_care_action(care_id, name=name, action_type=action_type,
                                   description=description)
        flash(f'Acción "{name}" actualizada correctamente!', 'success')
        return redirect(url_for('care.list_care_actions'))
    
    return render_template('care/edit.html', care_action=care_action)
    return render_template('treatments/edit.html', treatment=treatment, pests=pests)


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
