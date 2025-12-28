"""
Base service class for PlanSowGrow application.

This module provides a base service class that encapsulates common
database operations, following the principle that business logic
must live in services, never in routes.
"""
from flask import current_app
from app.models.base import db


class BaseService:
    """
    Base service class providing common CRUD operations.
    
    All service classes should inherit from this class to ensure
    consistent patterns for database operations and business logic.
    
    The service layer is responsible for:
    - Business logic and validation
    - Orchestrating operations across multiple models
    - Transaction management
    - Error handling and logging
    """
    
    model = None  # Should be overridden by child classes
    
    @classmethod
    def get_by_id(cls, entity_id):
        """
        Retrieve an entity by its ID.
        
        Args:
            entity_id (int): The ID of the entity
            
        Returns:
            Model instance or None if not found
        """
        return cls.model.query.get(entity_id)
    
    @classmethod
    def get_all(cls, include_deleted=False):
        """
        Retrieve all entities.
        
        Args:
            include_deleted (bool): Whether to include soft-deleted records
            
        Returns:
            list: List of model instances
        """
        if hasattr(cls.model, 'deleted_at') and not include_deleted:
            return cls.model.get_active().all()
        return cls.model.query.all()
    
    @classmethod
    def create(cls, **kwargs):
        """
        Create a new entity.
        
        Args:
            **kwargs: Field values for the new entity
            
        Returns:
            Model instance: The created entity
            
        Raises:
            ValueError: If validation fails
        """
        try:
            entity = cls.model(**kwargs)
            entity.save()
            current_app.logger.info(f"Created {cls.model.__name__} with id {entity.id}")
            return entity
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating {cls.model.__name__}: {str(e)}")
            raise
    
    @classmethod
    def update(cls, entity_id, **kwargs):
        """
        Update an existing entity.
        
        Args:
            entity_id (int): The ID of the entity to update
            **kwargs: Field values to update
            
        Returns:
            Model instance: The updated entity or None if not found
            
        Raises:
            ValueError: If validation fails
        """
        entity = cls.get_by_id(entity_id)
        if not entity:
            return None
        
        try:
            entity.update(**kwargs)
            current_app.logger.info(f"Updated {cls.model.__name__} with id {entity_id}")
            return entity
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating {cls.model.__name__}: {str(e)}")
            raise
    
    @classmethod
    def delete(cls, entity_id, soft=True):
        """
        Delete an entity.
        
        Args:
            entity_id (int): The ID of the entity to delete
            soft (bool): Whether to soft-delete (if supported) or hard-delete
            
        Returns:
            bool: True if deletion was successful, False if not found
        """
        entity = cls.get_by_id(entity_id)
        if not entity:
            return False
        
        try:
            if soft and hasattr(entity, 'soft_delete'):
                entity.soft_delete()
                current_app.logger.info(f"Soft-deleted {cls.model.__name__} with id {entity_id}")
            else:
                entity.delete()
                current_app.logger.info(f"Hard-deleted {cls.model.__name__} with id {entity_id}")
            return True
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error deleting {cls.model.__name__}: {str(e)}")
            raise
    
    @classmethod
    def restore(cls, entity_id):
        """
        Restore a soft-deleted entity.
        
        Args:
            entity_id (int): The ID of the entity to restore
            
        Returns:
            Model instance: The restored entity or None if not found
        """
        entity = cls.get_by_id(entity_id)
        if not entity or not hasattr(entity, 'restore'):
            return None
        
        try:
            entity.restore()
            current_app.logger.info(f"Restored {cls.model.__name__} with id {entity_id}")
            return entity
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error restoring {cls.model.__name__}: {str(e)}")
            raise
