"""
Bed model representing a planting bed within a garden.

A bed is a subdivision of a garden where specific plants are grown.
"""
from app.models.base import db, BaseModel, SoftDeleteMixin


class Bed(BaseModel, SoftDeleteMixin):
    """
    Represents a planting bed within a garden.
    
    Beds are logical or physical subdivisions of gardens that help organize
    plantings and track what's growing where.
    
    Attributes:
        name (str): Name or identifier of the bed
        garden_id (int): Foreign key to the parent garden
        length_m (float): Length in meters
        width_m (float): Width in meters
        notes (str): Additional notes about the bed
    """
    
    __tablename__ = 'beds'
    
    name = db.Column(
        db.String(100),
        nullable=False,
        doc="Name or identifier of the bed"
    )
    garden_id = db.Column(
        db.Integer,
        db.ForeignKey('gardens.id'),
        nullable=False,
        doc="Foreign key to the parent garden"
    )
    length_m = db.Column(
        db.Float,
        nullable=True,
        doc="Length of the bed in meters"
    )
    width_m = db.Column(
        db.Float,
        nullable=True,
        doc="Width of the bed in meters"
    )
    notes = db.Column(
        db.Text,
        nullable=True,
        doc="Additional notes about the bed"
    )
    
    @property
    def area_sqm(self):
        """
        Calculate the area of the bed in square meters.
        
        Returns:
            float: Area in square meters, or None if dimensions not set
        """
        if self.length_m and self.width_m:
            return self.length_m * self.width_m
        return None
    
    def __repr__(self):
        """String representation of the bed."""
        return f"<Bed {self.name} in Garden {self.garden_id}>"
    
    def to_dict(self):
        """
        Convert bed to dictionary representation.
        
        Returns:
            dict: Dictionary with bed data
        """
        data = super().to_dict()
        data['area_sqm'] = self.area_sqm
        data['is_active'] = self.is_active
        return data
