"""
Script para crear la tabla pest_treatments directamente.
"""
import pymysql
from config import Config

def create_pest_treatments_table():
    """Crea la tabla pest_treatments si no existe."""
    
    # Conexión directa usando pymysql
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
            cursor.execute("SHOW TABLES LIKE 'pest_treatments'")
            result = cursor.fetchone()
            
            if result:
                print("✓ La tabla pest_treatments YA existe")
                cursor.execute("DESCRIBE pest_treatments")
                print("\nEstructura de la tabla:")
                for row in cursor.fetchall():
                    print(f"  - {row['Field']}: {row['Type']}")
            else:
                print("✗ La tabla pest_treatments NO existe. Creándola...")
                
                # Crear la tabla
                create_table_sql = """
                CREATE TABLE pest_treatments (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    pest_id INT NOT NULL,
                    treatment_id INT NOT NULL,
                    effectiveness ENUM('high', 'medium', 'low') DEFAULT 'medium',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (pest_id) REFERENCES pests(id) ON DELETE CASCADE,
                    FOREIGN KEY (treatment_id) REFERENCES treatments(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_pest_treatment (pest_id, treatment_id),
                    INDEX idx_pest_id (pest_id),
                    INDEX idx_treatment_id (treatment_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                """
                
                cursor.execute(create_table_sql)
                connection.commit()
                
                print("✓ Tabla pest_treatments creada exitosamente!")
                
                # Verificar
                cursor.execute("DESCRIBE pest_treatments")
                print("\nEstructura de la tabla creada:")
                for row in cursor.fetchall():
                    print(f"  - {row['Field']}: {row['Type']}")
                    
    finally:
        connection.close()

if __name__ == "__main__":
    create_pest_treatments_table()
