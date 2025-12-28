"""
Garden model representing a garden or growing space.

A garden is a physical space where plants are grown. This is a core entity
in the PlanSowGrow system.
"""
from app.models.base import db, BaseModel, SoftDeleteMixin


class Garden(BaseModel, SoftDeleteMixin):
    """
    Represents a garden or growing space.
    
    Gardens can be soft-deleted to preserve historical data while removing
    them from active use.
    
    Attributes:
        name (str): Name of the garden
        description (str): Detailed description of the garden
        location (str): Physical location or address
        size_sqm (float): Size in square meters
        notes (str): Additional notes about the garden
    """
    
    __tablename__ = 'gardens'
    
    name = db.Column(
        db.String(100),
        nullable=False,
        doc="Name of the garden"
    )
    description = db.Column(
        db.Text,
        nullable=True,
        doc="Detailed description of the garden"
    )
    location = db.Column(
        db.String(200),
        nullable=True,
        doc="Physical location or address of the garden"
    )
    size_sqm = db.Column(
        db.Float,
        nullable=True,
        doc="Size of the garden in square meters"
    )
    notes = db.Column(
        db.Text,
        nullable=True,
        doc="Additional notes about the garden"
    )
    
    # Relationships
    beds = db.relationship(
        'Bed',
        backref='garden',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    
    def __repr__(self):
        """String representation of the garden."""
        return f"<Garden {self.name}>"
    
    def to_dict(self):
        """
        Convert garden to dictionary representation.
        
        Returns:
            dict: Dictionary with garden data
        """
        data = super().to_dict()
        data['is_active'] = self.is_active
        data['bed_count'] = self.beds.filter_by(deleted_at=None).count()
        return data
