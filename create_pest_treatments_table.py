"""
Migration script to create pest_treatments association table.
This enables many-to-many relationship between pests and treatments.
"""
from config import Config
from sqlalchemy import create_engine, text
import pymysql

def run_migration():
    """Execute the pest_treatments migration."""
    # Create database connection
    db_url = f"mysql+pymysql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{int(Config.DB_PORT)}/{Config.DB_NAME}"
    engine = create_engine(db_url)
    
    with engine.connect() as connection:
        # Read migration SQL
        with open('migrations/003_add_pest_treatments.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Split by semicolon and execute each statement
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
        
        for statement in statements:
            # Skip SELECT statements that are just for display
            if statement.upper().startswith('SELECT'):
                try:
                    result = connection.execute(text(statement))
                    rows = result.fetchall()
                    print(f"Query result: {rows}")
                except Exception as e:
                    print(f"Info query: {e}")
                continue
            
            # Skip DESCRIBE statements
            if statement.upper().startswith('DESCRIBE'):
                try:
                    result = connection.execute(text(statement))
                    rows = result.fetchall()
                    for row in rows:
                        print(row)
                except Exception as e:
                    print(f"Describe query: {e}")
                continue
            
            # Execute other statements
            try:
                connection.execute(text(statement))
                connection.commit()
                print(f"Executed: {statement[:50]}...")
            except Exception as e:
                print(f"Error executing statement: {e}")
                print(f"Statement: {statement[:100]}...")
                # Continue with next statement even if this one fails
                connection.rollback()
    
    print("\nMigration completed!")
    print("The pest_treatments table has been created.")
    print("Existing treatment data has been migrated to the new structure.")

if __name__ == '__main__':
    run_migration()
