"""
Script para verificar y crear la tabla plant_pests si no existe.
"""
import pymysql
from config import Config

def check_and_create_plant_pests_table():
    """Verifica y crea la tabla plant_pests si no existe."""
    
    connection = pymysql.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    try:
        with connection.cursor() as cursor:
            # Verificar si la tabla existe
            cursor.execute("SHOW TABLES LIKE 'plant_pests'")
            result = cursor.fetchone()
            
            if result:
                print("✓ La tabla plant_pests YA existe")
                cursor.execute("DESCRIBE plant_pests")
                print("\nEstructura de la tabla:")
                for row in cursor.fetchall():
                    print(f"  - {row['Field']}: {row['Type']}")
            else:
                print("✗ La tabla plant_pests NO existe. Creándola...")
                
                # Crear la tabla
                create_table_sql = """
                CREATE TABLE plant_pests (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    plant_id INT NOT NULL,
                    pest_id INT NOT NULL,
                    severity ENUM('high', 'medium', 'low') DEFAULT 'medium',
                    notes TEXT,
                    FOREIGN KEY (plant_id) REFERENCES plants(id) ON DELETE CASCADE,
                    FOREIGN KEY (pest_id) REFERENCES pests(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_plant_pest (plant_id, pest_id),
                    INDEX idx_plant_id (plant_id),
                    INDEX idx_pest_id (pest_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                """
                
                cursor.execute(create_table_sql)
                connection.commit()
                
                print("✓ Tabla plant_pests creada exitosamente!")
                
                # Verificar
                cursor.execute("DESCRIBE plant_pests")
                print("\nEstructura de la tabla creada:")
                for row in cursor.fetchall():
                    print(f"  - {row['Field']}: {row['Type']}")
                    
    finally:
        connection.close()

if __name__ == "__main__":
    check_and_create_plant_pests_table()
