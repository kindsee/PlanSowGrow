"""
Verificar y crear la tabla pest_treatments directamente.
"""
from config import Config
from sqlalchemy import create_engine, text

def verify_and_create_table():
    """Verificar si la tabla existe y crearla si no."""
    db_url = f"mysql+pymysql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{int(Config.DB_PORT)}/{Config.DB_NAME}"
    engine = create_engine(db_url)
    
    with engine.connect() as connection:
        # Verificar si la tabla existe
        result = connection.execute(text("SHOW TABLES LIKE 'pest_treatments'"))
        exists = result.fetchone() is not None
        
        if exists:
            print("✓ La tabla pest_treatments ya existe")
            # Mostrar estructura
            result = connection.execute(text("DESCRIBE pest_treatments"))
            print("\nEstructura actual:")
            for row in result:
                print(row)
        else:
            print("✗ La tabla pest_treatments NO existe. Creándola...")
            
            # Crear la tabla directamente
            create_table_sql = """
            CREATE TABLE pest_treatments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                pest_id INT NOT NULL,
                treatment_id INT NOT NULL,
                effectiveness ENUM('high', 'medium', 'low') DEFAULT NULL,
                notes TEXT,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_pest_treatment_pest FOREIGN KEY (pest_id) 
                    REFERENCES pests(id) ON DELETE CASCADE,
                CONSTRAINT fk_pest_treatment_treatment FOREIGN KEY (treatment_id) 
                    REFERENCES treatments(id) ON DELETE CASCADE,
                CONSTRAINT uq_pest_treatment UNIQUE (pest_id, treatment_id),
                INDEX idx_pest_id (pest_id),
                INDEX idx_treatment_id (treatment_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            
            connection.execute(text(create_table_sql))
            connection.commit()
            print("✓ Tabla pest_treatments creada exitosamente!")
            
            # Verificar creación
            result = connection.execute(text("DESCRIBE pest_treatments"))
            print("\nEstructura de la tabla creada:")
            for row in result:
                print(row)

if __name__ == '__main__':
    verify_and_create_table()
