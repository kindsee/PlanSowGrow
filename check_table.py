"""
Check if culture_treatments table exists in the database.
"""
import pymysql
from config import Config

def check_table():
    """Check if the table exists."""
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
            # Check if table exists
            cursor.execute("SHOW TABLES LIKE 'culture_treatments'")
            result = cursor.fetchone()
            
            if result:
                print("✅ Table 'culture_treatments' EXISTS")
                
                # Show table structure
                cursor.execute("DESCRIBE culture_treatments")
                columns = cursor.fetchall()
                print("\nTable structure:")
                for col in columns:
                    print(f"  - {col}")
            else:
                print("❌ Table 'culture_treatments' DOES NOT EXIST")
                print("\nAvailable tables:")
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                for table in tables:
                    print(f"  - {table[0]}")
    
    finally:
        connection.close()


if __name__ == '__main__':
    check_table()
