"""
Bed service containing business logic for bed operations.

This service handles all business logic related to planting beds.
"""
from flask import current_app
from app.models.bed import Bed
from app.services.base import BaseService


class BedService(BaseService):
    """
    Service class for Bed entity business logic.
    
    This service manages all bed-related operations including:
    - CRUD operations
    - Validation
    - Business rules
    - Relationship with gardens
    """
    
    model = Bed
    
    @classmethod
    def get_beds_by_garden(cls, garden_id, include_deleted=False):
        """
        Retrieve all beds for a specific garden.
        
        Args:
            garden_id (int): ID of the garden
            include_deleted (bool): Whether to include soft-deleted beds
            
        Returns:
            list: List of Bed instances
        """
        query = cls.model.query.filter_by(garden_id=garden_id)
        if not include_deleted:
            query = query.filter_by(deleted_at=None)
        return query.all()
    
    @classmethod
    def create_bed(cls, name, garden_id, length_m=None, width_m=None, notes=None):
        """
        Create a new bed with validation.
        
        Args:
            name (str): Name of the bed (required)
            garden_id (int): ID of the parent garden (required)
            length_m (float): Length in meters (optional)
            width_m (float): Width in meters (optional)
            notes (str): Additional notes (optional)
            
        Returns:
            Bed: The created bed instance
            
        Raises:
            ValueError: If validation fails
        """
        # Business validation
        if not name or not name.strip():
            raise ValueError("Bed name is required")
        
        if len(name) > 100:
            raise ValueError("Bed name must be 100 characters or less")
        
        if not garden_id:
            raise ValueError("Garden ID is required")
        
        if length_m is not None and length_m <= 0:
            raise ValueError("Bed length must be positive")
        
        if width_m is not None and width_m <= 0:
            raise ValueError("Bed width must be positive")
        
        return cls.create(
            name=name.strip(),
            garden_id=garden_id,
            length_m=length_m,
            width_m=width_m,
            notes=notes
        )
    
    @classmethod
    def update_bed(cls, bed_id, **kwargs):
        """
        Update an existing bed with validation.
        
        Args:
            bed_id (int): ID of the bed to update
            **kwargs: Fields to update
            
        Returns:
            Bed: The updated bed instance or None if not found
            
        Raises:
            ValueError: If validation fails
        """
        # Business validation
        if 'name' in kwargs:
            if not kwargs['name'] or not kwargs['name'].strip():
                raise ValueError("Bed name is required")
            if len(kwargs['name']) > 100:
                raise ValueError("Bed name must be 100 characters or less")
            kwargs['name'] = kwargs['name'].strip()
        
        if 'length_m' in kwargs and kwargs['length_m'] is not None:
            if kwargs['length_m'] <= 0:
                raise ValueError("Bed length must be positive")
        
        if 'width_m' in kwargs and kwargs['width_m'] is not None:
            if kwargs['width_m'] <= 0:
                raise ValueError("Bed width must be positive")
        
        return cls.update(bed_id, **kwargs)
