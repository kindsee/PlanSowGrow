"""Add alignment column to culture_plants table."""
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
        # Check if alignment column exists
        cursor.execute("DESCRIBE culture_plants")
        columns = [col[0] for col in cursor.fetchall()]
        
        if 'alignment' in columns:
            print("⚠️  Column 'alignment' already exists")
        else:
            print("Adding 'alignment' column...")
            cursor.execute("""
                ALTER TABLE culture_plants
                ADD COLUMN alignment ENUM('left', 'center', 'right') DEFAULT 'center' AFTER spacing_cm
            """)
            connection.commit()
            print("✅ Column 'alignment' added successfully!")
        
        # Verify
        cursor.execute("DESCRIBE culture_plants")
        columns = cursor.fetchall()
        print("\n📋 Updated culture_plants columns:")
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
        
except Exception as e:
    connection.rollback()
    print(f"❌ Error: {e}")
    raise

finally:
    connection.close()
