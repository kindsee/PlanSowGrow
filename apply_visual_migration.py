"""Execute the visual plantation migration."""
import pymysql
from config import Config

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
        with open('migrations/004_add_visual_plantation.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Split by semicolon and execute each statement
        statements = [s.strip() for s in sql_content.split(';') if s.strip() and not s.strip().startswith('--')]
        
        for statement in statements:
            print(f"Executing: {statement[:80]}...")
            cursor.execute(statement)
        
        connection.commit()
        print("\n✅ Migration 004_add_visual_plantation completed successfully!")
        
        # Verify columns were added
        cursor.execute("DESCRIBE culture_plants")
        columns = cursor.fetchall()
        print("\n📋 Current culture_plants columns:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
        
except Exception as e:
    connection.rollback()
    print(f"❌ Error during migration: {e}")
    raise

finally:
    connection.close()
