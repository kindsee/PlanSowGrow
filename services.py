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
    Treatment, CareAction, PlantCare, CalendarEvent
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
        'pest': pp.pest,
        'severity': pp.severity,
        'notes': pp.notes
    } for pp in plant_pests]


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


def create_treatment(pest_id: int, name: str, description: str = None,
                     application_method: str = None, frequency_days: int = None) -> Treatment:
    """Create a new treatment."""
    treatment = Treatment(
        pest_id=pest_id,
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
