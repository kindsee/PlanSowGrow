"""
Integration tests for garden routes.

These tests verify that HTTP endpoints work correctly with the full stack.
"""
import pytest


class TestGardenRoutes:
    """Test cases for garden routes."""
    
    def test_list_gardens_empty(self, client, db):
        """Test listing gardens when none exist."""
        response = client.get('/gardens/')
        
        assert response.status_code == 200
        assert b'No gardens yet' in response.data
    
    def test_create_garden_form_get(self, client, db):
        """Test GET request to create garden form."""
        response = client.get('/gardens/new')
        
        assert response.status_code == 200
        assert b'New Garden' in response.data
    
    def test_create_garden_form_post_success(self, client, db):
        """Test POST request to create garden."""
        data = {
            'name': 'Test Garden',
            'description': 'A test garden',
            'location': 'Test Location',
            'size_sqm': '100.5'
        }
        
        response = client.post('/gardens/new', data=data, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Garden "Test Garden" created successfully' in response.data
    
    def test_create_garden_validation_error(self, client, db):
        """Test creating garden with validation error."""
        data = {
            'name': '',  # Empty name should fail
            'description': 'Test'
        }
        
        response = client.post('/gardens/new', data=data, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Garden name is required' in response.data
    
    def test_view_garden(self, client, db):
        """Test viewing a specific garden."""
        from app.services import GardenService
        
        garden = GardenService.create_garden(name="Test Garden")
        
        response = client.get(f'/gardens/{garden.id}')
        
        assert response.status_code == 200
        assert b'Test Garden' in response.data
    
    def test_view_garden_not_found(self, client, db):
        """Test viewing non-existent garden."""
        response = client.get('/gardens/999', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Garden not found' in response.data
