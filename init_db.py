"""
Database initialization script for PlanSowGrow.
Creates all tables and optionally loads sample data.
"""
import sys
from app import create_app
from extensions import db
from models import (
    RaisedBed, Plant, Culture, CulturePlant, Pest, PlantPest,
    Treatment, CareAction, PlantCare, CalendarEvent
)


def init_database(drop_existing=False):
    """
    Initialize the database schema.
    
    Args:
        drop_existing: If True, drops all existing tables before creating new ones
    """
    app = create_app()
    
    with app.app_context():
        if drop_existing:
            print("Dropping existing tables...")
            db.drop_all()
        
        print("Creating database tables...")
        db.create_all()
        print("Database initialized successfully!")


def load_sample_data():
    """
    Load sample data for testing and development.
    """
    app = create_app()
    
    with app.app_context():
        print("Loading sample data...")
        
        # Sample Raised Beds
        beds = [
            RaisedBed(name="Bancal 1", description="Sunny location", location="North side"),
            RaisedBed(name="Bancal 2", description="Partial shade", location="South side"),
            RaisedBed(name="Bancal 3", description="Full sun", location="East side"),
        ]
        db.session.add_all(beds)
        
        # Sample Plants
        plants = [
            Plant(
                name="Tomato",
                scientific_name="Solanum lycopersicum",
                description="Red fruit vegetable",
                growth_days=80,
                harvest_period_days=60,
                notes="Needs tutoring and regular pruning"
            ),
            Plant(
                name="Lettuce",
                scientific_name="Lactuca sativa",
                description="Leafy green vegetable",
                growth_days=45,
                harvest_period_days=30,
                notes="Prefers cool weather"
            ),
            Plant(
                name="Carrot",
                scientific_name="Daucus carota",
                description="Root vegetable",
                growth_days=70,
                harvest_period_days=20,
                notes="Direct seeding recommended"
            ),
        ]
        db.session.add_all(plants)
        
        # Sample Pests
        pests = [
            Pest(
                name="Aphids",
                scientific_name="Aphidoidea",
                description="Small sap-sucking insects",
                symptoms="Curled leaves, sticky residue, stunted growth"
            ),
            Pest(
                name="Whiteflies",
                scientific_name="Aleyrodidae",
                description="Small white flying insects",
                symptoms="Yellow leaves, honeydew secretion"
            ),
        ]
        db.session.add_all(pests)
        
        # Sample Care Actions
        care_actions = [
            CareAction(
                name="Pruning suckers",
                description="Remove lateral shoots from tomatoes",
                action_type="pruning"
            ),
            CareAction(
                name="Install stakes",
                description="Add support structures for climbing plants",
                action_type="tutoring"
            ),
            CareAction(
                name="Deep watering",
                description="Water thoroughly at base of plants",
                action_type="watering"
            ),
        ]
        db.session.add_all(care_actions)
        
        db.session.commit()
        print("Sample data loaded successfully!")
        
        # Link plants to pests
        tomato = Plant.query.filter_by(name="Tomato").first()
        lettuce = Plant.query.filter_by(name="Lettuce").first()
        aphids = Pest.query.filter_by(name="Aphids").first()
        whiteflies = Pest.query.filter_by(name="Whiteflies").first()
        
        if tomato and aphids:
            plant_pest = PlantPest(plant_id=tomato.id, pest_id=aphids.id, severity="medium")
            db.session.add(plant_pest)
        
        if tomato and whiteflies:
            plant_pest = PlantPest(plant_id=tomato.id, pest_id=whiteflies.id, severity="high")
            db.session.add(plant_pest)
        
        if lettuce and aphids:
            plant_pest = PlantPest(plant_id=lettuce.id, pest_id=aphids.id, severity="low")
            db.session.add(plant_pest)
        
        # Add treatments
        if aphids:
            treatment = Treatment(
                pest_id=aphids.id,
                name="Neem oil spray",
                description="Organic neem oil solution",
                application_method="Spray on affected areas in early morning",
                frequency_days=7
            )
            db.session.add(treatment)
        
        # Link plants to care actions
        pruning = CareAction.query.filter_by(name="Pruning suckers").first()
        staking = CareAction.query.filter_by(name="Install stakes").first()
        
        if tomato and pruning:
            plant_care = PlantCare(
                plant_id=tomato.id,
                care_action_id=pruning.id,
                days_after_planting=21,
                frequency_days=7,
                notes="Prune weekly once plant is established"
            )
            db.session.add(plant_care)
        
        if tomato and staking:
            plant_care = PlantCare(
                plant_id=tomato.id,
                care_action_id=staking.id,
                days_after_planting=14,
                notes="Install stakes before plant grows too large"
            )
            db.session.add(plant_care)
        
        db.session.commit()
        print("Sample relationships created successfully!")


if __name__ == '__main__':
    # Parse command line arguments
    drop = '--drop' in sys.argv
    sample = '--sample' in sys.argv
    
    # Initialize database
    init_database(drop_existing=drop)
    
    # Load sample data if requested
    if sample:
        load_sample_data()
    
    print("\nUsage:")
    print("  python init_db.py           # Create tables only")
    print("  python init_db.py --drop    # Drop and recreate all tables")
    print("  python init_db.py --sample  # Create tables and load sample data")
    print("  python init_db.py --drop --sample  # Reset and load sample data")
