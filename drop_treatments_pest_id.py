"""
Script to drop pest_id column from treatments table after data migration.
"""
from config import Config
from sqlalchemy import create_engine, text

def drop_pest_id_column():
    """Drop the pest_id column from treatments table."""
    db_url = f"mysql+pymysql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{int(Config.DB_PORT)}/{Config.DB_NAME}"
    engine = create_engine(db_url)
    
    with engine.connect() as connection:
        try:
            # First, drop the foreign key constraint
            print("Dropping foreign key constraint...")
            connection.execute(text("ALTER TABLE treatments DROP FOREIGN KEY treatments_ibfk_1"))
            connection.commit()
            print("Foreign key dropped successfully!")
        except Exception as e:
            print(f"Note: {e}")
            connection.rollback()
        
        try:
            # Then drop the column
            print("Dropping pest_id column...")
            connection.execute(text("ALTER TABLE treatments DROP COLUMN pest_id"))
            connection.commit()
            print("Column dropped successfully!")
        except Exception as e:
            print(f"Error dropping column: {e}")
            connection.rollback()
        
        # Verify the structure
        print("\nCurrent treatments table structure:")
        result = connection.execute(text("DESCRIBE treatments"))
        for row in result:
            print(row)

if __name__ == '__main__':
    drop_pest_id_column()
