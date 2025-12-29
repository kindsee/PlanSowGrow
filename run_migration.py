"""
Migration script to add culture_treatments table.
Run this to update the database schema without losing existing data.
"""
import pymysql
from config import Config

def run_migration():
    """Execute the migration SQL file."""
    # Connect to database
    connection = pymysql.connect(
        host=Config.DB_HOST,
        port=int(Config.DB_PORT),
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        charset='utf8mb4'
    )
    
    try:
        with connection.cursor() as cursor:
            # Read migration file
            with open('migrations/001_add_culture_treatments.sql', 'r', encoding='utf-8') as f:
                sql_statements = f.read()
            
            # Execute SQL statements
            for statement in sql_statements.split(';'):
                statement = statement.strip()
                if statement and not statement.startswith('--'):
                    cursor.execute(statement)
                    result = cursor.fetchone()
                    if result:
                        print(result)
            
            connection.commit()
            print("✅ Migration completed successfully!")
            print("✅ Table 'culture_treatments' created")
            
    except Exception as e:
        connection.rollback()
        print(f"❌ Error during migration: {e}")
        raise
    
    finally:
        connection.close()


if __name__ == '__main__':
    print("Running migration: Add culture_treatments table...")
    run_migration()
