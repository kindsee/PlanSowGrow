"""
Season model representing a growing season.

Seasons are time periods for planning and tracking garden activities.
This demonstrates the PeriodMixin for date-based entities.
"""
from app.models.base import db, BaseModel, PeriodMixin


class Season(BaseModel, PeriodMixin):
    """
    Represents a growing season.
    
    A season is a defined time period used for planning and organizing
    garden activities. Seasons have start and end dates, and may remain
    open (no end date) until explicitly closed.
    
    Attributes:
        name (str): Name of the season (e.g., "Spring 2024")
        description (str): Description of the season
        notes (str): Additional notes
    """
    
    __tablename__ = 'seasons'
    
    name = db.Column(
        db.String(100),
        nullable=False,
        unique=True,
        doc="Name of the season"
    )
    description = db.Column(
        db.Text,
        nullable=True,
        doc="Description of the season"
    )
    notes = db.Column(
        db.Text,
        nullable=True,
        doc="Additional notes about the season"
    )
    
    def __repr__(self):
        """String representation of the season."""
        status = "Active" if self.is_active else "Closed"
        return f"<Season {self.name} ({status})>"
    
    def to_dict(self):
        """
        Convert season to dictionary representation.
        
        Returns:
            dict: Dictionary with season data
        """
        data = super().to_dict()
        data['is_active'] = self.is_active
        data['is_closed'] = self.is_closed
        data['duration_days'] = self.duration_days
        return data
