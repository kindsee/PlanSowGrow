"""
SQLAlchemy models for PlanSowGrow application.
Defines the database schema for garden management.
"""
from datetime import datetime
from extensions import db


class RaisedBed(db.Model):
    """
    Represents a fixed raised bed (bancal) in the garden.
    Fixed dimensions: 4m x 1m.
    """
    __tablename__ = 'raised_beds'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    location = db.Column(db.String(200))  # Physical location description
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    cultures = db.relationship('Culture', back_populates='bed', lazy='dynamic')
    
    def __repr__(self):
        return f'<RaisedBed {self.name}>'


class Plant(db.Model):
    """
    Catalog of plant species with growth and harvest information.
    """
    __tablename__ = 'plants'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    scientific_name = db.Column(db.String(200))
    description = db.Column(db.Text)
    icon = db.Column(db.String(10), default='🌱')  # Emoji icon for visual representation
    growth_days = db.Column(db.Integer)  # Days from planting to harvest
    harvest_period_days = db.Column(db.Integer)  # Duration of harvest period
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    cultures = db.relationship('CulturePlant', back_populates='plant', lazy='dynamic')
    plant_pests = db.relationship('PlantPest', back_populates='plant', lazy='dynamic')
    plant_cares = db.relationship('PlantCare', back_populates='plant', lazy='dynamic')
    
    def __repr__(self):
        return f'<Plant {self.name}>'


class Culture(db.Model):
    """
    Represents an active or historical planting in a raised bed.
    Multiple plants can be grown simultaneously in one bed.
    """
    __tablename__ = 'cultures'
    
    id = db.Column(db.Integer, primary_key=True)
    bed_id = db.Column(db.Integer, db.ForeignKey('raised_beds.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    start_type = db.Column(
        db.Enum('seed', 'seedling', 'transplant', name='start_type_enum'),
        nullable=False
    )
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    bed = db.relationship('RaisedBed', back_populates='cultures')
    plants = db.relationship('CulturePlant', back_populates='culture', lazy='dynamic')
    treatments = db.relationship('CultureTreatment', back_populates='culture', lazy='dynamic')
    cares = db.relationship('CultureCare', back_populates='culture', lazy='dynamic')
    calendar_events = db.relationship('CalendarEvent', back_populates='culture', lazy='dynamic')
    
    def __repr__(self):
        return f'<Culture {self.id} in {self.bed.name if self.bed else "unknown"}>'


class CulturePlant(db.Model):
    """
    Association table between cultures and plants.
    Allows multiple plants per culture (polyculture).
    """
    __tablename__ = 'culture_plants'
    
    id = db.Column(db.Integer, primary_key=True)
    culture_id = db.Column(db.Integer, db.ForeignKey('cultures.id'), nullable=False)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.id'), nullable=False)
    quantity_planted = db.Column(db.Integer, default=1)  # Seeds/seedlings used initially
    quantity_grown = db.Column(db.Integer, default=1)  # Plants that successfully grew
    
    # Visual plantation layout fields
    row_position = db.Column(
        db.Enum('superior', 'central', 'inferior', name='row_position_enum'),
        default='central'
    )  # Row in the bed
    spacing_cm = db.Column(
        db.Integer,
        default=30
    )  # Spacing between plants: 15, 20, 30, 40, 50, 100
    alignment = db.Column(
        db.Enum('left', 'center', 'right', name='alignment_enum'),
        default='center'
    )  # Horizontal alignment within the row
    
    notes = db.Column(db.Text)
    
    # Relationships
    culture = db.relationship('Culture', back_populates='plants')
    plant = db.relationship('Plant', back_populates='cultures')
    
    # Unique constraint to prevent duplicate plant-culture pairs
    __table_args__ = (
        db.UniqueConstraint('culture_id', 'plant_id', name='uq_culture_plant'),
    )
    
    def __repr__(self):
        return f'<CulturePlant culture={self.culture_id} plant={self.plant_id}>'


class Pest(db.Model):
    """
    Catalog of pests that can affect plants.
    """
    __tablename__ = 'pests'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    scientific_name = db.Column(db.String(200))
    description = db.Column(db.Text)
    symptoms = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    plant_pests = db.relationship('PlantPest', back_populates='pest', lazy='dynamic')
    pest_treatments = db.relationship('PestTreatment', back_populates='pest', lazy='dynamic')
    treatments = db.relationship('Treatment', secondary='pest_treatments', viewonly=True, overlaps="pest_treatments")
    
    def __repr__(self):
        return f'<Pest {self.name}>'


class PlantPest(db.Model):
    """
    Association table linking plants to their common pests.
    """
    __tablename__ = 'plant_pests'
    
    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.id'), nullable=False)
    pest_id = db.Column(db.Integer, db.ForeignKey('pests.id'), nullable=False)
    severity = db.Column(db.Enum('low', 'medium', 'high', name='severity_enum'))
    notes = db.Column(db.Text)
    
    # Relationships
    plant = db.relationship('Plant', back_populates='plant_pests')
    pest = db.relationship('Pest', back_populates='plant_pests')
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('plant_id', 'pest_id', name='uq_plant_pest'),
    )
    
    def __repr__(self):
        return f'<PlantPest plant={self.plant_id} pest={self.pest_id}>'


class PestTreatment(db.Model):
    """
    Association table linking pests to treatments.
    A treatment can be effective against multiple pests.
    A pest can have multiple effective treatments.
    """
    __tablename__ = 'pest_treatments'
    
    id = db.Column(db.Integer, primary_key=True)
    pest_id = db.Column(db.Integer, db.ForeignKey('pests.id'), nullable=False)
    treatment_id = db.Column(db.Integer, db.ForeignKey('treatments.id'), nullable=False)
    effectiveness = db.Column(db.Enum('high', 'medium', 'low', name='effectiveness_enum'))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    pest = db.relationship('Pest', back_populates='pest_treatments')
    treatment = db.relationship('Treatment', back_populates='pest_treatments')
    
    __table_args__ = (
        db.Index('idx_pest_id', 'pest_id'),
        db.Index('idx_treatment_id', 'treatment_id'),
        db.UniqueConstraint('pest_id', 'treatment_id', name='uq_pest_treatment'),
    )
    
    def __repr__(self):
        return f'<PestTreatment pest={self.pest_id} treatment={self.treatment_id}>'


class Treatment(db.Model):
    """
    Ecological treatments that can be applied to combat pests.
    A treatment can be effective against multiple pests (many-to-many).
    """
    __tablename__ = 'treatments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    application_method = db.Column(db.Text)
    frequency_days = db.Column(db.Integer)  # Suggested frequency (in days)
    is_ecological = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    pest_treatments = db.relationship('PestTreatment', back_populates='treatment', lazy='dynamic')
    pests = db.relationship('Pest', secondary='pest_treatments', viewonly=True, overlaps="pest_treatments")
    culture_treatments = db.relationship('CultureTreatment', back_populates='treatment', lazy='dynamic')
    calendar_events = db.relationship('CalendarEvent', back_populates='treatment', lazy='dynamic')
    
    def __repr__(self):
        return f'<Treatment {self.name}>'


class CareAction(db.Model):
    """
    Additional care actions for plants (pruning, pinching, tutoring, etc.).
    """
    __tablename__ = 'care_actions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    action_type = db.Column(
        db.Enum('pruning', 'pinching', 'tutoring', 'fertilizing', 'watering', 'other', 
                name='action_type_enum'),
        nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    plant_cares = db.relationship('PlantCare', back_populates='care_action', lazy='dynamic')
    culture_cares = db.relationship('CultureCare', back_populates='care_action', lazy='dynamic')
    calendar_events = db.relationship('CalendarEvent', back_populates='care_action', lazy='dynamic')
    
    def __repr__(self):
        return f'<CareAction {self.name}>'


class PlantCare(db.Model):
    """
    Association table linking plants to recommended care actions.
    Includes timing information relative to planting date.
    """
    __tablename__ = 'plant_cares'
    
    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.id'), nullable=False)
    care_action_id = db.Column(db.Integer, db.ForeignKey('care_actions.id'), nullable=False)
    days_after_planting = db.Column(db.Integer)  # When to perform (days after planting)
    frequency_days = db.Column(db.Integer)  # How often to repeat (in days)
    notes = db.Column(db.Text)
    
    # Relationships
    plant = db.relationship('Plant', back_populates='plant_cares')
    care_action = db.relationship('CareAction', back_populates='plant_cares')
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('plant_id', 'care_action_id', 'days_after_planting', 
                          name='uq_plant_care'),
    )
    
    def __repr__(self):
        return f'<PlantCare plant={self.plant_id} care={self.care_action_id}>'


class CultureTreatment(db.Model):
    """
    Association table linking treatments to specific cultures.
    Allows custom timing for treatment application.
    """
    __tablename__ = 'culture_treatments'
    
    id = db.Column(db.Integer, primary_key=True)
    culture_id = db.Column(db.Integer, db.ForeignKey('cultures.id'), nullable=False)
    treatment_id = db.Column(db.Integer, db.ForeignKey('treatments.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)  # When to start applying
    frequency_days = db.Column(db.Integer)  # Override treatment's default frequency
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    culture = db.relationship('Culture', back_populates='treatments')
    treatment = db.relationship('Treatment', back_populates='culture_treatments')
    
    def __repr__(self):
        return f'<CultureTreatment culture={self.culture_id} treatment={self.treatment_id}>'


class CultureCare(db.Model):
    """
    Association table linking care actions to specific cultures.
    Allows scheduling care actions for a specific date.
    """
    __tablename__ = 'culture_cares'
    
    id = db.Column(db.Integer, primary_key=True)
    culture_id = db.Column(db.Integer, db.ForeignKey('cultures.id'), nullable=False)
    care_action_id = db.Column(db.Integer, db.ForeignKey('care_actions.id'), nullable=False)
    scheduled_date = db.Column(db.Date, nullable=False)  # When to perform this care
    frequency_days = db.Column(db.Integer)  # How often to repeat (optional)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    culture = db.relationship('Culture', back_populates='cares')
    care_action = db.relationship('CareAction', back_populates='culture_cares')
    
    def __repr__(self):
        return f'<CultureCare culture={self.culture_id} care={self.care_action_id}>'


class CalendarEvent(db.Model):
    """
    Auto-generated calendar events for garden activities.
    Events reference either a treatment or a care action.
    """
    __tablename__ = 'calendar_events'
    
    id = db.Column(db.Integer, primary_key=True)
    culture_id = db.Column(db.Integer, db.ForeignKey('cultures.id'), nullable=False)
    treatment_id = db.Column(db.Integer, db.ForeignKey('treatments.id'))
    care_action_id = db.Column(db.Integer, db.ForeignKey('care_actions.id'))
    scheduled_date = db.Column(db.Date, nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    completed_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    culture = db.relationship('Culture', back_populates='calendar_events')
    treatment = db.relationship('Treatment', back_populates='calendar_events')
    care_action = db.relationship('CareAction', back_populates='calendar_events')
    
    # Check constraint: must have either treatment_id or care_action_id, but not both
    __table_args__ = (
        db.CheckConstraint(
            '(treatment_id IS NOT NULL AND care_action_id IS NULL) OR '
            '(treatment_id IS NULL AND care_action_id IS NOT NULL)',
            name='chk_event_type'
        ),
    )
    
    def __repr__(self):
        return f'<CalendarEvent {self.id} on {self.scheduled_date}>'
