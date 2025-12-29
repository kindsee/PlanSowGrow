"""
Create culture_treatments table directly.
"""
import pymysql
from config import Config

def create_table():
    """Create the culture_treatments table."""
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
            print("Creating table culture_treatments...")
            
            # Create the table
            sql = """
            CREATE TABLE IF NOT EXISTS culture_treatments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                culture_id INT NOT NULL,
                treatment_id INT NOT NULL,
                start_date DATE NOT NULL,
                frequency_days INT,
                notes TEXT,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (culture_id) REFERENCES cultures(id) ON DELETE CASCADE,
                FOREIGN KEY (treatment_id) REFERENCES treatments(id) ON DELETE CASCADE,
                INDEX idx_culture_id (culture_id),
                INDEX idx_treatment_id (treatment_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            cursor.execute(sql)
            connection.commit()
            
            print("✅ Table created successfully!")
            
            # Verify
            cursor.execute("SHOW TABLES LIKE 'culture_treatments'")
            result = cursor.fetchone()
            
            if result:
                print("✅ Verification: Table 'culture_treatments' exists")
                cursor.execute("DESCRIBE culture_treatments")
                columns = cursor.fetchall()
                print("\nTable structure:")
                for col in columns:
                    print(f"  {col[0]:20} {col[1]:20} {col[2]}")
            else:
                print("❌ Verification failed: Table does not exist")
    
    except Exception as e:
        connection.rollback()
        print(f"❌ Error: {e}")
        raise
    
    finally:
        connection.close()


if __name__ == '__main__':
    create_table()
