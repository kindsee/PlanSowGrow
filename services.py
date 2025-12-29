"""
Business logic services for PlanSowGrow.
All business logic must live here, never in routes.
"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import and_, or_
from extensions import db
from models import (
    RaisedBed, Plant, Culture, CulturePlant, Pest, PlantPest,
    Treatment, CareAction, PlantCare, CalendarEvent, CultureTreatment, CultureCare, PestTreatment
)


# ========== Raised Bed Services ==========

def get_all_beds(include_inactive: bool = False) -> List[RaisedBed]:
    """
    Get all raised beds.
    
    Args:
        include_inactive: If True, includes inactive beds
    
    Returns:
        List of RaisedBed objects
    """
    query = db.session.query(RaisedBed)
    if not include_inactive:
        query = query.filter_by(is_active=True)
    return query.order_by(RaisedBed.name).all()


def get_bed_by_id(bed_id: int) -> Optional[RaisedBed]:
    """Get a single raised bed by ID."""
    return db.session.get(RaisedBed, bed_id)


def create_bed(name: str, description: str = None, location: str = None) -> RaisedBed:
    """
    Create a new raised bed.
    
    Args:
        name: Unique name for the bed
        description: Optional description
        location: Optional physical location
    
    Returns:
        Created RaisedBed object
    """
    bed = RaisedBed(name=name, description=description, location=location)
    db.session.add(bed)
    db.session.commit()
    return bed


def update_bed(bed_id: int, **kwargs) -> Optional[RaisedBed]:
    """
    Update a raised bed.
    
    Args:
        bed_id: ID of bed to update
        **kwargs: Fields to update
    
    Returns:
        Updated RaisedBed object or None if not found
    """
    bed = db.session.get(RaisedBed, bed_id)
    if not bed:
        return None
    
    for key, value in kwargs.items():
        if hasattr(bed, key):
            setattr(bed, key, value)
    
    db.session.commit()
    return bed


def deactivate_bed(bed_id: int) -> Optional[RaisedBed]:
    """
    Deactivate a raised bed (never delete, preserve history).
    
    Args:
        bed_id: ID of bed to deactivate
    
    Returns:
        Deactivated RaisedBed object or None if not found
    """
    return update_bed(bed_id, is_active=False)


# ========== Plant Services ==========

def get_all_plants() -> List[Plant]:
    """Get all plants from catalog."""
    return db.session.query(Plant).order_by(Plant.name).all()


def get_plant_by_id(plant_id: int) -> Optional[Plant]:
    """Get a single plant by ID."""
    return db.session.get(Plant, plant_id)


def create_plant(name: str, scientific_name: str = None, description: str = None,
                 growth_days: int = None, harvest_period_days: int = None,
                 notes: str = None) -> Plant:
    """
    Create a new plant in the catalog.
    
    Args:
        name: Common name of the plant
        scientific_name: Scientific name
        description: Plant description
        growth_days: Days from planting to harvest
        harvest_period_days: Duration of harvest period
        notes: Additional notes
    
    Returns:
        Created Plant object
    """
    plant = Plant(
        name=name,
        scientific_name=scientific_name,
        description=description,
        growth_days=growth_days,
        harvest_period_days=harvest_period_days,
        notes=notes
    )
    db.session.add(plant)
    db.session.commit()
    return plant


def update_plant(plant_id: int, **kwargs) -> Optional[Plant]:
    """Update a plant in the catalog."""
    plant = db.session.get(Plant, plant_id)
    if not plant:
        return None
    
    for key, value in kwargs.items():
        if hasattr(plant, key):
            setattr(plant, key, value)
    
    db.session.commit()
    return plant


def update_pest(pest_id: int, **kwargs) -> Optional[Pest]:
    """Update a pest in the catalog."""
    pest = db.session.get(Pest, pest_id)
    if not pest:
        return None
    
    for key, value in kwargs.items():
        if hasattr(pest, key):
            setattr(pest, key, value)
    
    db.session.commit()
    return pest


# ========== Culture Services ==========

def get_active_cultures() -> List[Culture]:
    """Get all active cultures."""
    return db.session.query(Culture).filter_by(is_active=True).order_by(Culture.start_date.desc()).all()


def get_culture_by_id(culture_id: int) -> Optional[Culture]:
    """Get a single culture by ID."""
    return db.session.get(Culture, culture_id)


def get_cultures_by_bed(bed_id: int, include_inactive: bool = False) -> List[Culture]:
    """
    Get all cultures for a specific bed.
    
    Args:
        bed_id: ID of the raised bed
        include_inactive: If True, includes closed cultures
    
    Returns:
        List of Culture objects
    """
    query = db.session.query(Culture).filter_by(bed_id=bed_id)
    if not include_inactive:
        query = query.filter_by(is_active=True)
    return query.order_by(Culture.start_date.desc()).all()


def create_culture(bed_id: int, start_date: date, start_type: str,
                   plant_ids: List[int], quantities_planted: List[int] = None,
                   quantities_grown: List[int] = None, end_date: date = None,
                   notes: str = None) -> Culture:
    """
    Create a new culture (planting).
    
    Args:
        bed_id: ID of the raised bed
        start_date: Planting start date
        start_type: One of 'seed', 'seedling', 'transplant'
        plant_ids: List of plant IDs to include in this culture
        quantities_planted: List of quantities planted for each plant (defaults to 1)
        quantities_grown: List of quantities that grew for each plant (defaults to 1)
        end_date: Optional end date
        notes: Optional notes
    
    Returns:
        Created Culture object
    """
    culture = Culture(
        bed_id=bed_id,
        start_date=start_date,
        end_date=end_date,
        start_type=start_type,
        notes=notes
    )
    db.session.add(culture)
    db.session.flush()  # Get culture.id before adding plants
    
    # Add plants to culture
    for i, plant_id in enumerate(plant_ids):
        qty_planted = quantities_planted[i] if quantities_planted and i < len(quantities_planted) else 1
        qty_grown = quantities_grown[i] if quantities_grown and i < len(quantities_grown) else 1
        
        culture_plant = CulturePlant(
            culture_id=culture.id,
            plant_id=plant_id,
            quantity_planted=qty_planted,
            quantity_grown=qty_grown
        )
        db.session.add(culture_plant)
    
    db.session.commit()
    return culture


def close_culture(culture_id: int, end_date: date = None) -> Optional[Culture]:
    """
    Close a culture (mark as inactive, preserve history).
    
    Args:
        culture_id: ID of culture to close
        end_date: Optional end date (defaults to today)
    
    Returns:
        Closed Culture object or None if not found
    """
    culture = db.session.get(Culture, culture_id)
    if not culture:
        return None
    
    culture.is_active = False
    culture.end_date = end_date or date.today()
    db.session.commit()
    return culture


def get_bed_history(bed_id: int) -> List[Culture]:
    """
    Get complete historical record of all cultures in a bed.
    
    Args:
        bed_id: ID of the raised bed
    
    Returns:
        List of all Culture objects (active and inactive) for the bed
    """
    return db.session.query(Culture).filter_by(bed_id=bed_id).order_by(Culture.start_date.desc()).all()


# ========== Pest Services ==========

def get_all_pests() -> List[Pest]:
    """Get all pests from catalog."""
    return db.session.query(Pest).order_by(Pest.name).all()


def get_pest_by_id(pest_id: int) -> Optional[Pest]:
    """Get a single pest by ID."""
    return db.session.get(Pest, pest_id)


def create_pest(name: str, scientific_name: str = None,
                description: str = None, symptoms: str = None) -> Pest:
    """Create a new pest in the catalog."""
    pest = Pest(
        name=name,
        scientific_name=scientific_name,
        description=description,
        symptoms=symptoms
    )
    db.session.add(pest)
    db.session.commit()
    return pest


def link_plant_to_pest(plant_id: int, pest_id: int, severity: str = None) -> PlantPest:
    """
    Link a plant to a pest it's susceptible to.
    
    Args:
        plant_id: ID of the plant
        pest_id: ID of the pest
        severity: One of 'low', 'medium', 'high'
    
    Returns:
        Created PlantPest association
    """
    plant_pest = PlantPest(plant_id=plant_id, pest_id=pest_id, severity=severity)
    db.session.add(plant_pest)
    db.session.commit()
    return plant_pest


def get_pests_for_plant(plant_id: int) -> List[Dict[str, Any]]:
    """
    Get all pests that affect a specific plant.
    
    Args:
        plant_id: ID of the plant
    
    Returns:
        List of dictionaries with pest and severity information
    """
    plant_pests = db.session.query(PlantPest).filter_by(plant_id=plant_id).all()
    return [{
        'plant_pest_id': pp.id,
        'pest': pp.pest,
        'severity': pp.severity,
        'notes': pp.notes
    } for pp in plant_pests]


def add_pest_to_plant(plant_id: int, pest_id: int, severity: str = 'medium', notes: str = '') -> PlantPest:
    """
    Add a pest to a plant or update the relationship if it exists.
    
    Args:
        plant_id: ID of the plant
        pest_id: ID of the pest
        severity: Severity level ('low', 'medium', 'high')
        notes: Optional notes about this pest-plant relationship
    
    Returns:
        The created or updated PlantPest association
    """
    # Check if the association already exists
    plant_pest = db.session.query(PlantPest).filter_by(
        plant_id=plant_id,
        pest_id=pest_id
    ).first()
    
    if plant_pest:
        # Update existing association
        plant_pest.severity = severity
        plant_pest.notes = notes
    else:
        # Create new association
        plant_pest = PlantPest(
            plant_id=plant_id,
            pest_id=pest_id,
            severity=severity,
            notes=notes
        )
        db.session.add(plant_pest)
    
    db.session.commit()
    return plant_pest


def remove_pest_from_plant(plant_id: int, pest_id: int) -> bool:
    """
    Remove a pest association from a plant.
    
    Args:
        plant_id: ID of the plant
        pest_id: ID of the pest
    
    Returns:
        True if the association was removed, False if it didn't exist
    """
    plant_pest = db.session.query(PlantPest).filter_by(
        plant_id=plant_id,
        pest_id=pest_id
    ).first()
    
    if plant_pest:
        db.session.delete(plant_pest)
        db.session.commit()
        return True
    
    return False


# ========== Treatment Services ==========

def get_all_treatments() -> List[Treatment]:
    """Get all treatments."""
    return db.session.query(Treatment).order_by(Treatment.name).all()


def get_treatment_by_id(treatment_id: int) -> Optional[Treatment]:
    """Get a single treatment by ID."""
    return db.session.get(Treatment, treatment_id)


def get_treatments_for_pest(pest_id: int) -> List[Treatment]:
    """Get all treatments for a specific pest."""
    return db.session.query(Treatment).filter_by(pest_id=pest_id).all()


def create_treatment(name: str, description: str = None,
                     application_method: str = None, frequency_days: int = None) -> Treatment:
    """Create a new treatment."""
    treatment = Treatment(
        name=name,
        description=description,
        application_method=application_method,
        frequency_days=frequency_days
    )
    db.session.add(treatment)
    db.session.commit()
    return treatment


def update_treatment(treatment_id: int, **kwargs) -> Optional[Treatment]:
    """Update a treatment."""
    treatment = db.session.get(Treatment, treatment_id)
    if not treatment:
        return None
    
    for key, value in kwargs.items():
        if hasattr(treatment, key):
            setattr(treatment, key, value)
    
    db.session.commit()
    return treatment


# ========== Care Action Services ==========

def get_all_care_actions() -> List[CareAction]:
    """Get all care actions."""
    return db.session.query(CareAction).order_by(CareAction.name).all()


def get_care_action_by_id(care_id: int) -> Optional[CareAction]:
    """Get a single care action by ID."""
    return db.session.get(CareAction, care_id)


def create_care_action(name: str, action_type: str, description: str = None) -> CareAction:
    """
    Create a new care action.
    
    Args:
        name: Name of the care action
        action_type: One of 'pruning', 'pinching', 'tutoring', 'fertilizing', 'watering', 'other'
        description: Optional description
    
    Returns:
        Created CareAction object
    """
    care_action = CareAction(name=name, action_type=action_type, description=description)
    db.session.add(care_action)
    db.session.commit()
    return care_action


def update_care_action(care_id: int, **kwargs) -> Optional[CareAction]:
    """Update a care action."""
    care_action = db.session.get(CareAction, care_id)
    if not care_action:
        return None
    
    for key, value in kwargs.items():
        if hasattr(care_action, key):
            setattr(care_action, key, value)
    
    db.session.commit()
    return care_action


def link_plant_to_care(plant_id: int, care_action_id: int,
                       days_after_planting: int = None,
                       frequency_days: int = None, notes: str = None) -> PlantCare:
    """
    Link a plant to a care action with timing information.
    
    Args:
        plant_id: ID of the plant
        care_action_id: ID of the care action
        days_after_planting: When to perform (days after planting)
        frequency_days: How often to repeat (in days)
        notes: Optional notes
    
    Returns:
        Created PlantCare association
    """
    plant_care = PlantCare(
        plant_id=plant_id,
        care_action_id=care_action_id,
        days_after_planting=days_after_planting,
        frequency_days=frequency_days,
        notes=notes
    )
    db.session.add(plant_care)
    db.session.commit()
    return plant_care


# ========== Calendar Services ==========

def generate_calendar_events_for_culture(culture_id: int) -> List[CalendarEvent]:
    """
    Generate calendar events for a culture based on its plants' care needs.
    
    Args:
        culture_id: ID of the culture
    
    Returns:
        List of generated CalendarEvent objects
    """
    culture = db.session.get(Culture, culture_id)
    if not culture:
        return []
    
    events = []
    
    # Get all plants in this culture
    culture_plants = db.session.query(CulturePlant).filter_by(culture_id=culture_id).all()
    
    for cp in culture_plants:
        plant = cp.plant
        
        # Generate events for each care action linked to this plant
        plant_cares = db.session.query(PlantCare).filter_by(plant_id=plant.id).all()
        
        for pc in plant_cares:
            if pc.days_after_planting is not None:
                # Calculate event date
                event_date = culture.start_date + timedelta(days=pc.days_after_planting)
                
                # Only create events for future dates or recent past
                if event_date >= date.today() - timedelta(days=7):
                    event = CalendarEvent(
                        culture_id=culture_id,
                        care_action_id=pc.care_action_id,
                        scheduled_date=event_date,
                        notes=pc.notes
                    )
                    db.session.add(event)
                    events.append(event)
    
    db.session.commit()
    return events


def get_calendar_events(start_date: date = None, end_date: date = None,
                        include_completed: bool = False) -> List[CalendarEvent]:
    """
    Get calendar events within a date range.
    
    Args:
        start_date: Start of date range (defaults to today)
        end_date: End of date range (defaults to 30 days from start)
        include_completed: If True, includes completed events
    
    Returns:
        List of CalendarEvent objects
    """
    if start_date is None:
        start_date = date.today()
    if end_date is None:
        end_date = start_date + timedelta(days=30)
    
    query = db.session.query(CalendarEvent).filter(
        and_(
            CalendarEvent.scheduled_date >= start_date,
            CalendarEvent.scheduled_date <= end_date
        )
    )
    
    if not include_completed:
        query = query.filter_by(completed=False)
    
    return query.order_by(CalendarEvent.scheduled_date).all()


def mark_event_completed(event_id: int, completed_date: date = None) -> Optional[CalendarEvent]:
    """
    Mark a calendar event as completed.
    
    Args:
        event_id: ID of the event
        completed_date: Date completed (defaults to today)
    
    Returns:
        Updated CalendarEvent or None if not found
    """
    event = db.session.get(CalendarEvent, event_id)
    if not event:
        return None
    
    event.completed = True
    event.completed_date = completed_date or date.today()
    db.session.commit()
    return event


# ========== Culture Progress Services ==========

def get_culture_progress(culture: Culture) -> Dict[str, Any]:
    """
    Calculate growth and harvest progress for a culture.
    
    Args:
        culture: Culture object
    
    Returns:
        Dictionary with:
        - phase: 'growing' | 'harvesting' | 'ended'
        - growth_progress: percentage (0-100)
        - harvest_progress: percentage (0-100) or None
        - days_since_start: integer
        - days_to_harvest: integer or None
        - days_to_harvest_end: integer or None
    """
    # Get all plants in the culture
    culture_plants = culture.plants.all()
    if not culture_plants:
        return {
            'phase': 'ended',
            'growth_progress': 0,
            'harvest_progress': None,
            'days_since_start': 0,
            'days_to_harvest': None,
            'days_to_harvest_end': None
        }
    
    # Get maximum growth and harvest periods from plants
    max_growth_days = max((cp.plant.growth_days for cp in culture_plants if cp.plant.growth_days), default=None)
    max_harvest_days = max((cp.plant.harvest_period_days for cp in culture_plants if cp.plant.harvest_period_days), default=None)
    
    # Calculate days since start
    today = date.today()
    days_since_start = (today - culture.start_date).days
    
    # Determine phase and calculate progress
    if max_growth_days is None:
        # No growth info, can't calculate progress
        return {
            'phase': 'growing',
            'growth_progress': 0,
            'harvest_progress': None,
            'days_since_start': days_since_start,
            'days_to_harvest': None,
            'days_to_harvest_end': None
        }
    
    if days_since_start < max_growth_days:
        # Growing phase
        growth_progress = min(100, int((days_since_start / max_growth_days) * 100))
        days_to_harvest = max_growth_days - days_since_start
        
        return {
            'phase': 'growing',
            'growth_progress': growth_progress,
            'harvest_progress': None,
            'days_since_start': days_since_start,
            'days_to_harvest': days_to_harvest,
            'days_to_harvest_end': days_to_harvest + (max_harvest_days or 0)
        }
    
    elif max_harvest_days and days_since_start < (max_growth_days + max_harvest_days):
        # Harvesting phase
        days_in_harvest = days_since_start - max_growth_days
        harvest_progress = min(100, int((days_in_harvest / max_harvest_days) * 100))
        days_to_harvest_end = max_growth_days + max_harvest_days - days_since_start
        
        return {
            'phase': 'harvesting',
            'growth_progress': 100,
            'harvest_progress': harvest_progress,
            'days_since_start': days_since_start,
            'days_to_harvest': 0,
            'days_to_harvest_end': days_to_harvest_end
        }
    
    else:
        # Culture should be ended
        return {
            'phase': 'ended',
            'growth_progress': 100,
            'harvest_progress': 100 if max_harvest_days else None,
            'days_since_start': days_since_start,
            'days_to_harvest': 0,
            'days_to_harvest_end': 0
        }


# ========== Culture Treatment Services ==========

def add_treatment_to_culture(
    culture_id: int,
    treatment_id: int,
    start_date: date,
    frequency_days: Optional[int] = None,
    notes: Optional[str] = None
) -> Optional[CultureTreatment]:
    """
    Add a treatment to a culture with custom timing.
    
    Args:
        culture_id: ID of the culture
        treatment_id: ID of the treatment
        start_date: When to start applying (must be >= culture.start_date)
        frequency_days: Override treatment's default frequency
        notes: Additional notes
    
    Returns:
        Created CultureTreatment or None if validation fails
    """
    culture = db.session.get(Culture, culture_id)
    treatment = db.session.get(Treatment, treatment_id)
    
    if not culture or not treatment:
        return None
    
    # Validate start_date is not before culture start
    if start_date < culture.start_date:
        return None
    
    # Create the association
    culture_treatment = CultureTreatment(
        culture_id=culture_id,
        treatment_id=treatment_id,
        start_date=start_date,
        frequency_days=frequency_days if frequency_days else treatment.frequency_days,
        notes=notes
    )
    
    db.session.add(culture_treatment)
    db.session.commit()
    
    # Generate calendar events for this treatment
    generate_treatment_events_for_culture(
        culture_id, 
        treatment_id, 
        start_date, 
        culture_treatment.frequency_days
    )
    
    return culture_treatment


def get_culture_treatments(culture_id: int) -> List[CultureTreatment]:
    """
    Get all treatments assigned to a culture.
    
    Args:
        culture_id: ID of the culture
    
    Returns:
        List of CultureTreatment objects
    """
    return db.session.query(CultureTreatment).filter_by(
        culture_id=culture_id
    ).order_by(CultureTreatment.start_date).all()


def generate_treatment_events_for_culture(
    culture_id: int,
    treatment_id: int,
    start_date: date,
    frequency_days: Optional[int]
) -> List[CalendarEvent]:
    """
    Generate calendar events for a treatment in a culture.
    
    Args:
        culture_id: ID of the culture
        treatment_id: ID of the treatment
        start_date: First application date
        frequency_days: How often to repeat (in days)
    
    Returns:
        List of created CalendarEvent objects
    """
    culture = db.session.get(Culture, culture_id)
    if not culture:
        return []
    
    events = []
    
    # Determine end date for event generation
    if culture.end_date:
        end_date = culture.end_date
    else:
        # If culture is still active, generate events for 90 days from start_date
        end_date = start_date + timedelta(days=90)
    
    # Generate first event
    current_date = start_date
    event = CalendarEvent(
        culture_id=culture_id,
        treatment_id=treatment_id,
        scheduled_date=current_date
    )
    db.session.add(event)
    events.append(event)
    
    # Generate recurring events if frequency is specified
    if frequency_days and frequency_days > 0:
        current_date = start_date + timedelta(days=frequency_days)
        
        while current_date <= end_date:
            event = CalendarEvent(
                culture_id=culture_id,
                treatment_id=treatment_id,
                scheduled_date=current_date
            )
            db.session.add(event)
            events.append(event)
            current_date += timedelta(days=frequency_days)
    
    db.session.commit()
    return events


# ========== Culture Care Services ==========

def add_care_to_culture(
    culture_id: int,
    care_action_id: int,
    scheduled_date: date,
    frequency_days: Optional[int] = None,
    notes: Optional[str] = None
) -> Optional[CultureCare]:
    """
    Add a care action to a culture with specific scheduling.
    
    Args:
        culture_id: ID of the culture
        care_action_id: ID of the care action
        scheduled_date: When to perform (must be >= culture.start_date)
        frequency_days: How often to repeat (optional)
        notes: Additional notes
    
    Returns:
        Created CultureCare or None if validation fails
    """
    culture = db.session.get(Culture, culture_id)
    care_action = db.session.get(CareAction, care_action_id)
    
    if not culture or not care_action:
        return None
    
    # Validate scheduled_date is not before culture start
    if scheduled_date < culture.start_date:
        return None
    
    # Create the association
    culture_care = CultureCare(
        culture_id=culture_id,
        care_action_id=care_action_id,
        scheduled_date=scheduled_date,
        frequency_days=frequency_days,
        notes=notes
    )
    
    db.session.add(culture_care)
    db.session.commit()
    
    # Generate calendar events for this care action
    generate_care_events_for_culture(
        culture_id, 
        care_action_id, 
        scheduled_date, 
        frequency_days
    )
    
    return culture_care


def get_culture_cares(culture_id: int) -> List[CultureCare]:
    """
    Get all care actions assigned to a culture.
    
    Args:
        culture_id: ID of the culture
    
    Returns:
        List of CultureCare objects
    """
    return db.session.query(CultureCare).filter_by(
        culture_id=culture_id
    ).order_by(CultureCare.scheduled_date).all()


def generate_care_events_for_culture(
    culture_id: int,
    care_action_id: int,
    scheduled_date: date,
    frequency_days: Optional[int]
) -> List[CalendarEvent]:
    """
    Generate calendar events for a care action in a culture.
    
    Args:
        culture_id: ID of the culture
        care_action_id: ID of the care action
        scheduled_date: First occurrence date
        frequency_days: How often to repeat (in days)
    
    Returns:
        List of created CalendarEvent objects
    """
    culture = db.session.get(Culture, culture_id)
    if not culture:
        return []
    
    events = []
    
    # Determine end date for event generation
    if culture.end_date:
        end_date = culture.end_date
    else:
        # If culture is still active, generate events for 90 days from scheduled_date
        end_date = scheduled_date + timedelta(days=90)
    
    # Generate first event
    current_date = scheduled_date
    event = CalendarEvent(
        culture_id=culture_id,
        care_action_id=care_action_id,
        scheduled_date=current_date
    )
    db.session.add(event)
    events.append(event)
    
    # Generate recurring events if frequency is specified
    if frequency_days and frequency_days > 0:
        current_date = scheduled_date + timedelta(days=frequency_days)
        
        while current_date <= end_date:
            event = CalendarEvent(
                culture_id=culture_id,
                care_action_id=care_action_id,
                scheduled_date=current_date
            )
            db.session.add(event)
            events.append(event)
            current_date += timedelta(days=frequency_days)
    
    db.session.commit()
    return events


def get_culture_events_with_status(culture_id: int) -> Dict[str, List[Dict]]:
    """
    Get all events (treatments and cares) for a culture grouped by status.
    
    Args:
        culture_id: ID of the culture
    
    Returns:
        Dictionary with 'pending' and 'completed' lists
    """
    events = db.session.query(CalendarEvent).filter_by(
        culture_id=culture_id
    ).order_by(CalendarEvent.scheduled_date).all()
    
    pending = []
    completed = []
    
    for event in events:
        event_data = {
            'id': event.id,
            'scheduled_date': event.scheduled_date,
            'completed': event.completed,
            'completed_date': event.completed_date,
            'notes': event.notes
        }
        
        if event.treatment_id:
            event_data['type'] = 'treatment'
            event_data['treatment'] = event.treatment
        elif event.care_action_id:
            event_data['type'] = 'care'
            event_data['care_action'] = event.care_action
        
        if event.completed:
            completed.append(event_data)
        else:
            pending.append(event_data)
    
    return {
        'pending': pending,
        'completed': completed
    }


def get_bed_events_with_status(bed_id: int) -> Dict[str, List[Dict]]:
    """
    Get all events for all cultures in a bed grouped by status.
    
    Args:
        bed_id: ID of the raised bed
    
    Returns:
        Dictionary with 'pending' and 'completed' lists
    """
    # Get all cultures in the bed
    cultures = db.session.query(Culture).filter_by(bed_id=bed_id).all()
    culture_ids = [c.id for c in cultures]
    
    if not culture_ids:
        return {'pending': [], 'completed': []}
    
    # Get all events for these cultures
    events = db.session.query(CalendarEvent).filter(
        CalendarEvent.culture_id.in_(culture_ids)
    ).order_by(CalendarEvent.scheduled_date).all()
    
    pending = []
    completed = []
    
    for event in events:
        event_data = {
            'id': event.id,
            'scheduled_date': event.scheduled_date,
            'completed': event.completed,
            'completed_date': event.completed_date,
            'notes': event.notes,
            'culture': event.culture
        }
        
        if event.treatment_id:
            event_data['type'] = 'treatment'
            event_data['treatment'] = event.treatment
        elif event.care_action_id:
            event_data['type'] = 'care'
            event_data['care_action'] = event.care_action
        
        if event.completed:
            completed.append(event_data)
        else:
            pending.append(event_data)
    
    return {
        'pending': pending,
        'completed': completed
    }


# ========== Pest-Treatment Association Services ==========

def add_pest_to_treatment(treatment_id: int, pest_id: int, effectiveness: str = 'high', notes: str = None) -> PestTreatment:
    """
    Associate a pest with a treatment.
    
    Args:
        treatment_id: ID of the treatment
        pest_id: ID of the pest
        effectiveness: Effectiveness level ('high', 'medium', 'low')
        notes: Optional notes about this association
    
    Returns:
        Created PestTreatment association
    """
    # Check if association already exists
    existing = db.session.query(PestTreatment).filter_by(
        treatment_id=treatment_id,
        pest_id=pest_id
    ).first()
    
    if existing:
        # Update existing
        existing.effectiveness = effectiveness
        if notes:
            existing.notes = notes
        db.session.commit()
        return existing
    
    # Create new association
    pest_treatment = PestTreatment(
        treatment_id=treatment_id,
        pest_id=pest_id,
        effectiveness=effectiveness,
        notes=notes
    )
    db.session.add(pest_treatment)
    db.session.commit()
    return pest_treatment


def remove_pest_from_treatment(treatment_id: int, pest_id: int) -> bool:
    """
    Remove pest-treatment association.
    
    Returns:
        True if removed, False if not found
    """
    pest_treatment = db.session.query(PestTreatment).filter_by(
        treatment_id=treatment_id,
        pest_id=pest_id
    ).first()
    
    if pest_treatment:
        db.session.delete(pest_treatment)
        db.session.commit()
        return True
    return False


def get_pests_for_treatment(treatment_id: int) -> List[Dict[str, Any]]:
    """
    Get all pests associated with a treatment.
    
    Returns:
        List of dicts with pest info and effectiveness
    """
    pest_treatments = db.session.query(PestTreatment).filter_by(
        treatment_id=treatment_id
    ).all()
    
    return [{
        'pest': pt.pest,
        'effectiveness': pt.effectiveness,
        'notes': pt.notes,
        'pest_treatment_id': pt.id
    } for pt in pest_treatments]


def get_treatments_for_pest(pest_id: int) -> List[Dict[str, Any]]:
    """
    Get all treatments effective against a pest.
    
    Returns:
        List of dicts with treatment info and effectiveness
    """
    pest_treatments = db.session.query(PestTreatment).filter_by(
        pest_id=pest_id
    ).all()
    
    return [{
        'treatment': pt.treatment,
        'effectiveness': pt.effectiveness,
        'notes': pt.notes,
        'pest_treatment_id': pt.id
    } for pt in pest_treatments]


def get_culture_potential_pests(culture_id: int) -> List[Pest]:
    """
    Get all pests that could affect a culture based on its plants.
    
    Args:
        culture_id: ID of the culture
    
    Returns:
        List of Pest objects that affect any plant in the culture
    """
    # Get all plants in this culture
    culture_plants = db.session.query(CulturePlant).filter_by(
        culture_id=culture_id
    ).all()
    
    plant_ids = [cp.plant_id for cp in culture_plants]
    
    if not plant_ids:
        return []
    
    # Get all pests associated with these plants
    plant_pests = db.session.query(PlantPest).filter(
        PlantPest.plant_id.in_(plant_ids)
    ).all()
    
    # Extract unique pests
    pest_ids = list(set([pp.pest_id for pp in plant_pests]))
    
    if not pest_ids:
        return []
    
    pests = db.session.query(Pest).filter(Pest.id.in_(pest_ids)).all()
    return pests


def get_relevant_treatments_for_culture(culture_id: int) -> List[Dict[str, Any]]:
    """
    Get treatments relevant for a culture based on pests affecting its plants.
    
    Args:
        culture_id: ID of the culture
    
    Returns:
        List of dicts with treatment and related pest info
    """
    # Get pests for this culture
    pests = get_culture_potential_pests(culture_id)
    
    if not pests:
        return []
    
    pest_ids = [p.id for p in pests]
    
    # Get all treatment associations for these pests
    pest_treatments = db.session.query(PestTreatment).filter(
        PestTreatment.pest_id.in_(pest_ids)
    ).order_by(
        PestTreatment.effectiveness.desc(),
        PestTreatment.treatment_id
    ).all()
    
    # Group by treatment to avoid duplicates
    treatments_dict = {}
    for pt in pest_treatments:
        treatment_id = pt.treatment_id
        if treatment_id not in treatments_dict:
            treatments_dict[treatment_id] = {
                'treatment': pt.treatment,
                'pests': [],
                'max_effectiveness': pt.effectiveness
            }
        treatments_dict[treatment_id]['pests'].append({
            'pest': pt.pest,
            'effectiveness': pt.effectiveness
        })
    
    return list(treatments_dict.values())


# ========== Pest-Treatment Association Services ==========

def add_pest_to_treatment(treatment_id: int, pest_id: int, effectiveness: str = 'high', notes: str = None) -> PestTreatment:
    """
    Associate a pest with a treatment.
    
    Args:
        treatment_id: ID of the treatment
        pest_id: ID of the pest
        effectiveness: Effectiveness level ('high', 'medium', 'low')
        notes: Optional notes about this association
    
    Returns:
        Created PestTreatment association
    """
    # Check if association already exists
    existing = db.session.query(PestTreatment).filter_by(
        treatment_id=treatment_id,
        pest_id=pest_id
    ).first()
    
    if existing:
        # Update existing
        existing.effectiveness = effectiveness
        if notes:
            existing.notes = notes
        db.session.commit()
        return existing
    
    # Create new association
    pest_treatment = PestTreatment(
        treatment_id=treatment_id,
        pest_id=pest_id,
        effectiveness=effectiveness,
        notes=notes
    )
    db.session.add(pest_treatment)
    db.session.commit()
    return pest_treatment


def remove_pest_from_treatment(treatment_id: int, pest_id: int) -> bool:
    """
    Remove pest-treatment association.
    
    Returns:
        True if removed, False if not found
    """
    pest_treatment = db.session.query(PestTreatment).filter_by(
        treatment_id=treatment_id,
        pest_id=pest_id
    ).first()
    
    if pest_treatment:
        db.session.delete(pest_treatment)
        db.session.commit()
        return True
    return False


def get_pests_for_treatment(treatment_id: int) -> List[Dict[str, Any]]:
    """
    Get all pests associated with a treatment.
    
    Returns:
        List of dicts with pest info and effectiveness
    """
    pest_treatments = db.session.query(PestTreatment).filter_by(
        treatment_id=treatment_id
    ).all()
    
    return [{
        'pest': pt.pest,
        'effectiveness': pt.effectiveness,
        'notes': pt.notes,
        'pest_treatment_id': pt.id
    } for pt in pest_treatments]


def get_treatments_for_pest(pest_id: int) -> List[Dict[str, Any]]:
    """
    Get all treatments effective against a pest.
    
    Returns:
        List of dicts with treatment info and effectiveness
    """
    pest_treatments = db.session.query(PestTreatment).filter_by(
        pest_id=pest_id
    ).all()
    
    return [{
        'treatment': pt.treatment,
        'effectiveness': pt.effectiveness,
        'notes': pt.notes,
        'pest_treatment_id': pt.id
    } for pt in pest_treatments]


def get_culture_potential_pests(culture_id: int) -> List[Pest]:
    """
    Get all pests that could affect a culture based on its plants.
    
    Args:
        culture_id: ID of the culture
    
    Returns:
        List of Pest objects that affect any plant in the culture
    """
    # Get all plants in this culture
    culture_plants = db.session.query(CulturePlant).filter_by(
        culture_id=culture_id
    ).all()
    
    plant_ids = [cp.plant_id for cp in culture_plants]
    
    if not plant_ids:
        return []
    
    # Get all pests associated with these plants
    plant_pests = db.session.query(PlantPest).filter(
        PlantPest.plant_id.in_(plant_ids)
    ).all()
    
    # Extract unique pests
    pest_ids = list(set([pp.pest_id for pp in plant_pests]))
    
    if not pest_ids:
        return []
    
    pests = db.session.query(Pest).filter(Pest.id.in_(pest_ids)).all()
    return pests


def get_relevant_treatments_for_culture(culture_id: int) -> List[Dict[str, Any]]:
    """
    Get treatments relevant for a culture based on pests affecting its plants.
    
    Args:
        culture_id: ID of the culture
    
    Returns:
        List of dicts with treatment and related pest info
    """
    # Get pests for this culture
    pests = get_culture_potential_pests(culture_id)
    
    if not pests:
        return []
    
    pest_ids = [p.id for p in pests]
    
    # Get all treatment associations for these pests
    pest_treatments = db.session.query(PestTreatment).filter(
        PestTreatment.pest_id.in_(pest_ids)
    ).order_by(
        PestTreatment.effectiveness.desc(),
        PestTreatment.treatment_id
    ).all()
    
    # Group by treatment to avoid duplicates
    treatments_dict = {}
    for pt in pest_treatments:
        treatment_id = pt.treatment_id
        if treatment_id not in treatments_dict:
            treatments_dict[treatment_id] = {
                'treatment': pt.treatment,
                'pests': [],
                'max_effectiveness': pt.effectiveness
            }
        treatments_dict[treatment_id]['pests'].append({
            'pest': pt.pest,
            'effectiveness': pt.effectiveness
        })
    
    return list(treatments_dict.values())
