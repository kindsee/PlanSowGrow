"""
Base model classes for PlanSowGrow application.

This module provides base classes with common functionality for all models,
including timestamp tracking, soft delete support, and period management.
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()


class BaseModel(db.Model):
    """
    Abstract base model with common fields and functionality.
    
    All models should inherit from this class to get:
    - Primary key (id)
    - Creation timestamp (created_at)
    - Update timestamp (updated_at)
    - Common query methods
    
    This class follows the principle that historical data must never be deleted.
    """
    
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        doc="Timestamp when the record was created"
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        doc="Timestamp when the record was last updated"
    )
    
    def save(self):
        """
        Save the current instance to the database.
        
        Returns:
            self: The saved instance
        """
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """
        Delete the current instance from the database.
        
        Note: This performs a hard delete. For models requiring soft delete,
        use SoftDeleteMixin instead.
        
        Returns:
            bool: True if deletion was successful
        """
        db.session.delete(self)
        db.session.commit()
        return True
    
    def update(self, **kwargs):
        """
        Update the current instance with provided keyword arguments.
        
        Args:
            **kwargs: Field names and their new values
            
        Returns:
            self: The updated instance
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self
    
    def to_dict(self):
        """
        Convert model instance to dictionary.
        
        Returns:
            dict: Dictionary representation of the model
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def __repr__(self):
        """String representation of the model."""
        return f"<{self.__class__.__name__} {self.id}>"


class SoftDeleteMixin:
    """
    Mixin to add soft delete functionality to models.
    
    Instead of permanently deleting records, marks them as deleted
    with a timestamp. This preserves historical data as required.
    
    Usage:
        class MyModel(BaseModel, SoftDeleteMixin):
            pass
    """
    
    deleted_at = db.Column(
        db.DateTime,
        nullable=True,
        default=None,
        doc="Timestamp when the record was soft-deleted (None if active)"
    )
    
    @property
    def is_deleted(self):
        """Check if the record is soft-deleted."""
        return self.deleted_at is not None
    
    @property
    def is_active(self):
        """Check if the record is active (not deleted)."""
        return self.deleted_at is None
    
    def soft_delete(self):
        """
        Mark the record as deleted without removing it from database.
        
        Returns:
            self: The soft-deleted instance
        """
        self.deleted_at = datetime.utcnow()
        db.session.commit()
        return self
    
    def restore(self):
        """
        Restore a soft-deleted record.
        
        Returns:
            self: The restored instance
        """
        self.deleted_at = None
        db.session.commit()
        return self
    
    @classmethod
    def get_active(cls):
        """
        Query to get only active (non-deleted) records.
        
        Returns:
            Query: SQLAlchemy query filtered for active records
        """
        return cls.query.filter_by(deleted_at=None)


class PeriodMixin:
    """
    Mixin for models that have start and end periods.
    
    Many entities in PlanSowGrow have time periods (seasons, plantings, etc.).
    This mixin provides common fields and functionality for period management.
    
    Usage:
        class Season(BaseModel, PeriodMixin):
            pass
    """
    
    start_date = db.Column(
        db.Date,
        nullable=False,
        doc="Start date of the period"
    )
    end_date = db.Column(
        db.Date,
        nullable=True,
        doc="End date of the period (None if ongoing)"
    )
    
    @property
    def is_active(self):
        """Check if the period is currently active."""
        today = datetime.utcnow().date()
        if self.end_date is None:
            return self.start_date <= today
        return self.start_date <= today <= self.end_date
    
    @property
    def is_closed(self):
        """Check if the period is closed (has an end date in the past or today)."""
        if self.end_date is None:
            return False
        return self.end_date <= datetime.utcnow().date()
    
    @property
    def duration_days(self):
        """
        Calculate the duration of the period in days.
        
        Returns:
            int: Number of days in the period, or None if period is ongoing
        """
        if self.end_date is None:
            return None
        return (self.end_date - self.start_date).days
    
    def close(self, end_date=None):
        """
        Close the period by setting an end date.
        
        Args:
            end_date: The end date (defaults to today)
            
        Returns:
            self: The updated instance
        """
        self.end_date = end_date or datetime.utcnow().date()
        db.session.commit()
        return self
    
    @classmethod
    def get_active_periods(cls):
        """
        Query to get currently active periods.
        
        Returns:
            Query: SQLAlchemy query filtered for active periods
        """
        today = datetime.utcnow().date()
        return cls.query.filter(
            cls.start_date <= today,
            db.or_(cls.end_date.is_(None), cls.end_date >= today)
        )
