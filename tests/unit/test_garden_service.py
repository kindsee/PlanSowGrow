"""
Unit tests for Garden service.

These tests verify that business logic in GardenService works correctly.
"""
import pytest
from app.models.garden import Garden
from app.services import GardenService


class TestGardenService:
    """Test cases for GardenService."""
    
    def test_create_garden_success(self, db):
        """Test successful garden creation."""
        garden = GardenService.create_garden(
            name="Test Garden",
            description="A test garden",
            location="Test Location",
            size_sqm=100.0
        )
        
        assert garden is not None
        assert garden.id is not None
        assert garden.name == "Test Garden"
        assert garden.description == "A test garden"
        assert garden.location == "Test Location"
        assert garden.size_sqm == 100.0
    
    def test_create_garden_with_whitespace(self, db):
        """Test that garden name is stripped of whitespace."""
        garden = GardenService.create_garden(name="  Test Garden  ")
        
        assert garden.name == "Test Garden"
    
    def test_create_garden_empty_name_fails(self, db):
        """Test that creating garden with empty name fails."""
        with pytest.raises(ValueError, match="Garden name is required"):
            GardenService.create_garden(name="")
    
    def test_create_garden_whitespace_only_name_fails(self, db):
        """Test that creating garden with whitespace-only name fails."""
        with pytest.raises(ValueError, match="Garden name is required"):
            GardenService.create_garden(name="   ")
    
    def test_create_garden_name_too_long_fails(self, db):
        """Test that creating garden with too long name fails."""
        long_name = "A" * 101
        with pytest.raises(ValueError, match="Garden name must be 100 characters or less"):
            GardenService.create_garden(name=long_name)
    
    def test_create_garden_negative_size_fails(self, db):
        """Test that creating garden with negative size fails."""
        with pytest.raises(ValueError, match="Garden size must be positive"):
            GardenService.create_garden(name="Test Garden", size_sqm=-10)
    
    def test_get_active_gardens(self, db):
        """Test getting active gardens."""
        garden1 = GardenService.create_garden(name="Garden 1")
        garden2 = GardenService.create_garden(name="Garden 2")
        garden3 = GardenService.create_garden(name="Garden 3")
        
        # Archive one garden
        garden2.soft_delete()
        
        active_gardens = GardenService.get_active_gardens()
        
        assert len(active_gardens) == 2
        assert garden1 in active_gardens
        assert garden2 not in active_gardens
        assert garden3 in active_gardens
    
    def test_update_garden(self, db):
        """Test updating a garden."""
        garden = GardenService.create_garden(name="Original Name")
        
        updated = GardenService.update_garden(
            garden.id,
            name="Updated Name",
            description="New description"
        )
        
        assert updated.name == "Updated Name"
        assert updated.description == "New description"
    
    def test_update_garden_invalid_name(self, db):
        """Test updating garden with invalid name fails."""
        garden = GardenService.create_garden(name="Test Garden")
        
        with pytest.raises(ValueError, match="Garden name is required"):
            GardenService.update_garden(garden.id, name="")
    
    def test_archive_garden(self, db):
        """Test archiving a garden."""
        garden = GardenService.create_garden(name="Test Garden")
        
        result = GardenService.archive_garden(garden.id)
        
        assert result is True
        
        # Verify garden is soft-deleted
        db.session.refresh(garden)
        assert garden.is_deleted
        assert garden.deleted_at is not None
    
    def test_get_garden_with_beds(self, db):
        """Test getting garden with its beds."""
        from app.models.bed import Bed
        
        garden = GardenService.create_garden(name="Test Garden")
        
        # Create beds
        bed1 = Bed(name="Bed 1", garden_id=garden.id)
        bed1.save()
        bed2 = Bed(name="Bed 2", garden_id=garden.id)
        bed2.save()
        
        garden_result, beds = GardenService.get_garden_with_beds(garden.id)
        
        assert garden_result == garden
        assert len(beds) == 2
