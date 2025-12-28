"""
Unit tests for Season service.

These tests verify that business logic in SeasonService works correctly.
"""
import pytest
from datetime import date, timedelta
from app.services import SeasonService


class TestSeasonService:
    """Test cases for SeasonService."""
    
    def test_create_season_success(self, db):
        """Test successful season creation."""
        today = date.today()
        
        season = SeasonService.create_season(
            name="Spring 2024",
            start_date=today,
            description="Spring growing season"
        )
        
        assert season is not None
        assert season.id is not None
        assert season.name == "Spring 2024"
        assert season.start_date == today
        assert season.end_date is None
        assert season.description == "Spring growing season"
    
    def test_create_season_with_end_date(self, db):
        """Test creating season with end date."""
        start = date.today()
        end = start + timedelta(days=90)
        
        season = SeasonService.create_season(
            name="Summer 2024",
            start_date=start,
            end_date=end
        )
        
        assert season.start_date == start
        assert season.end_date == end
        assert season.duration_days == 90
    
    def test_create_season_empty_name_fails(self, db):
        """Test that creating season with empty name fails."""
        with pytest.raises(ValueError, match="Season name is required"):
            SeasonService.create_season(name="", start_date=date.today())
    
    def test_create_season_end_before_start_fails(self, db):
        """Test that end date before start date fails."""
        start = date.today()
        end = start - timedelta(days=1)
        
        with pytest.raises(ValueError, match="End date must be after start date"):
            SeasonService.create_season(
                name="Test Season",
                start_date=start,
                end_date=end
            )
    
    def test_get_active_seasons(self, db):
        """Test getting active seasons."""
        today = date.today()
        past = today - timedelta(days=30)
        future = today + timedelta(days=30)
        
        # Active season (started in past, no end date)
        active1 = SeasonService.create_season(
            name="Active 1",
            start_date=past
        )
        
        # Active season (started in past, ends in future)
        active2 = SeasonService.create_season(
            name="Active 2",
            start_date=past,
            end_date=future
        )
        
        # Closed season (ended in past)
        closed = SeasonService.create_season(
            name="Closed",
            start_date=past - timedelta(days=60),
            end_date=past - timedelta(days=1)
        )
        
        # Future season
        future_season = SeasonService.create_season(
            name="Future",
            start_date=future
        )
        
        active_seasons = SeasonService.get_active_seasons()
        
        assert active1 in active_seasons
        assert active2 in active_seasons
        assert closed not in active_seasons
        assert future_season not in active_seasons
    
    def test_close_season(self, db):
        """Test closing a season."""
        season = SeasonService.create_season(
            name="Test Season",
            start_date=date.today() - timedelta(days=30)
        )
        
        end_date = date.today()
        closed = SeasonService.close_season(season.id, end_date)
        
        assert closed.end_date == end_date
        assert closed.is_closed
    
    def test_close_season_already_closed_fails(self, db):
        """Test that closing already closed season fails."""
        season = SeasonService.create_season(
            name="Test Season",
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )
        
        with pytest.raises(ValueError, match="Season is already closed"):
            SeasonService.close_season(season.id)
    
    def test_close_season_end_before_start_fails(self, db):
        """Test that closing season with end before start fails."""
        start = date.today()
        season = SeasonService.create_season(
            name="Test Season",
            start_date=start
        )
        
        with pytest.raises(ValueError, match="End date cannot be before start date"):
            SeasonService.close_season(season.id, start - timedelta(days=1))
    
    def test_reopen_season(self, db):
        """Test reopening a closed season."""
        season = SeasonService.create_season(
            name="Test Season",
            start_date=date.today() - timedelta(days=30),
            end_date=date.today()
        )
        
        assert season.is_closed
        
        reopened = SeasonService.reopen_season(season.id)
        
        assert reopened.end_date is None
        assert not reopened.is_closed
        assert reopened.is_active
