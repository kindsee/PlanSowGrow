"""
Garden service containing business logic for garden operations.

This service handles all business logic related to gardens, following
the principle that business logic must live in services, not routes.
"""
from flask import current_app
from app.models.garden import Garden
from app.services.base import BaseService


class GardenService(BaseService):
    """
    Service class for Garden entity business logic.
    
    This service manages all garden-related operations including:
    - CRUD operations
    - Validation
    - Business rules
    """
    
    model = Garden
    
    @classmethod
    def get_active_gardens(cls):
        """
        Retrieve all active (non-deleted) gardens.
        
        Returns:
            list: List of active Garden instances
        """
        return cls.model.get_active().all()
    
    @classmethod
    def create_garden(cls, name, description=None, location=None, size_sqm=None, notes=None):
        """
        Create a new garden with validation.
        
        Args:
            name (str): Name of the garden (required)
            description (str): Detailed description (optional)
            location (str): Physical location (optional)
            size_sqm (float): Size in square meters (optional)
            notes (str): Additional notes (optional)
            
        Returns:
            Garden: The created garden instance
            
        Raises:
            ValueError: If validation fails
        """
        # Business validation
        if not name or not name.strip():
            raise ValueError("Garden name is required")
        
        if len(name) > 100:
            raise ValueError("Garden name must be 100 characters or less")
        
        if size_sqm is not None and size_sqm <= 0:
            raise ValueError("Garden size must be positive")
        
        return cls.create(
            name=name.strip(),
            description=description,
            location=location,
            size_sqm=size_sqm,
            notes=notes
        )
    
    @classmethod
    def update_garden(cls, garden_id, **kwargs):
        """
        Update an existing garden with validation.
        
        Args:
            garden_id (int): ID of the garden to update
            **kwargs: Fields to update
            
        Returns:
            Garden: The updated garden instance or None if not found
            
        Raises:
            ValueError: If validation fails
        """
        # Business validation
        if 'name' in kwargs:
            if not kwargs['name'] or not kwargs['name'].strip():
                raise ValueError("Garden name is required")
            if len(kwargs['name']) > 100:
                raise ValueError("Garden name must be 100 characters or less")
            kwargs['name'] = kwargs['name'].strip()
        
        if 'size_sqm' in kwargs and kwargs['size_sqm'] is not None:
            if kwargs['size_sqm'] <= 0:
                raise ValueError("Garden size must be positive")
        
        return cls.update(garden_id, **kwargs)
    
    @classmethod
    def get_garden_with_beds(cls, garden_id):
        """
        Get a garden with its associated beds.
        
        Args:
            garden_id (int): ID of the garden
            
        Returns:
            tuple: (Garden instance, list of active Bed instances) or (None, None)
        """
        garden = cls.get_by_id(garden_id)
        if not garden:
            return None, None
        
        beds = garden.beds.filter_by(deleted_at=None).all()
        return garden, beds
    
    @classmethod
    def archive_garden(cls, garden_id):
        """
        Archive a garden (soft delete) to preserve historical data.
        
        Args:
            garden_id (int): ID of the garden to archive
            
        Returns:
            bool: True if successful, False if garden not found
        """
        result = cls.delete(garden_id, soft=True)
        if result:
            current_app.logger.info(f"Archived garden {garden_id}")
        return result
