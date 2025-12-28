"""
Season service containing business logic for season operations.

This service handles all business logic related to growing seasons,
including period management and validation.
"""
from datetime import datetime, date
from flask import current_app
from app.models.season import Season
from app.services.base import BaseService


class SeasonService(BaseService):
    """
    Service class for Season entity business logic.
    
    This service manages all season-related operations including:
    - CRUD operations with date validation
    - Period management (opening/closing seasons)
    - Active season queries
    """
    
    model = Season
    
    @classmethod
    def get_active_seasons(cls):
        """
        Retrieve all currently active seasons.
        
        Returns:
            list: List of active Season instances
        """
        return cls.model.get_active_periods().all()
    
    @classmethod
    def get_current_season(cls):
        """
        Get the current active season (if any).
        
        Returns:
            Season: The current season or None if no active season
        """
        active_seasons = cls.get_active_seasons()
        # Return the most recently started active season
        if active_seasons:
            return max(active_seasons, key=lambda s: s.start_date)
        return None
    
    @classmethod
    def create_season(cls, name, start_date, end_date=None, description=None, notes=None):
        """
        Create a new season with validation.
        
        Args:
            name (str): Name of the season (required)
            start_date (date): Start date of the season (required)
            end_date (date): End date of the season (optional)
            description (str): Description (optional)
            notes (str): Additional notes (optional)
            
        Returns:
            Season: The created season instance
            
        Raises:
            ValueError: If validation fails
        """
        # Business validation
        if not name or not name.strip():
            raise ValueError("Season name is required")
        
        if len(name) > 100:
            raise ValueError("Season name must be 100 characters or less")
        
        if not start_date:
            raise ValueError("Start date is required")
        
        # Convert string dates to date objects if needed
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        if end_date and isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Validate date logic
        if end_date and end_date < start_date:
            raise ValueError("End date must be after start date")
        
        # Check for overlapping seasons
        if cls._has_overlap(start_date, end_date):
            current_app.logger.warning(
                f"Creating season '{name}' with potential overlap with existing seasons"
            )
        
        return cls.create(
            name=name.strip(),
            start_date=start_date,
            end_date=end_date,
            description=description,
            notes=notes
        )
    
    @classmethod
    def close_season(cls, season_id, end_date=None):
        """
        Close a season by setting its end date.
        
        This follows the principle that historical data must never be deleted,
        only closed or archived.
        
        Args:
            season_id (int): ID of the season to close
            end_date (date): End date (defaults to today)
            
        Returns:
            Season: The closed season or None if not found
            
        Raises:
            ValueError: If validation fails
        """
        season = cls.get_by_id(season_id)
        if not season:
            return None
        
        if season.is_closed:
            raise ValueError("Season is already closed")
        
        close_date = end_date or datetime.utcnow().date()
        
        # Convert string date if needed
        if isinstance(close_date, str):
            close_date = datetime.strptime(close_date, '%Y-%m-%d').date()
        
        if close_date < season.start_date:
            raise ValueError("End date cannot be before start date")
        
        season.close(close_date)
        current_app.logger.info(f"Closed season {season_id} on {close_date}")
        return season
    
    @classmethod
    def reopen_season(cls, season_id):
        """
        Reopen a closed season by removing its end date.
        
        Args:
            season_id (int): ID of the season to reopen
            
        Returns:
            Season: The reopened season or None if not found
        """
        season = cls.get_by_id(season_id)
        if not season:
            return None
        
        season.end_date = None
        season.save()
        current_app.logger.info(f"Reopened season {season_id}")
        return season
    
    @classmethod
    def _has_overlap(cls, start_date, end_date):
        """
        Check if the given date range overlaps with existing seasons.
        
        Args:
            start_date (date): Start date to check
            end_date (date): End date to check (None for open-ended)
            
        Returns:
            bool: True if there's an overlap
        """
        # This is a simple check; could be enhanced with more sophisticated logic
        active_seasons = cls.get_active_seasons()
        
        for season in active_seasons:
            # Check for overlap
            if end_date is None:
                # New season is open-ended, check if it overlaps with start
                if season.end_date is None or season.end_date >= start_date:
                    return True
            else:
                # Check standard range overlap
                if season.end_date is None:
                    if season.start_date <= end_date:
                        return True
                else:
                    if not (end_date < season.start_date or start_date > season.end_date):
                        return True
        
        return False
