-- Migration to add pest_treatments association table
-- This allows many-to-many relationship between pests and treatments

-- Create the new pest_treatments association table
CREATE TABLE IF NOT EXISTS pest_treatments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pest_id INT NOT NULL,
    treatment_id INT NOT NULL,
    effectiveness ENUM('high', 'medium', 'low') DEFAULT NULL,
    notes TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_pest_treatment_pest FOREIGN KEY (pest_id) REFERENCES pests(id) ON DELETE CASCADE,
    CONSTRAINT fk_pest_treatment_treatment FOREIGN KEY (treatment_id) REFERENCES treatments(id) ON DELETE CASCADE,
    CONSTRAINT uq_pest_treatment UNIQUE (pest_id, treatment_id),
    INDEX idx_pest_id (pest_id),
    INDEX idx_treatment_id (treatment_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Migrate existing data from treatments table to pest_treatments
-- This assumes treatments table has pest_id column
INSERT IGNORE INTO pest_treatments (pest_id, treatment_id, effectiveness, created_at)
SELECT pest_id, id, 'high', created_at
FROM treatments
WHERE pest_id IS NOT NULL;

-- After verifying data migration is successful, manually run:
-- ALTER TABLE treatments DROP FOREIGN KEY treatments_ibfk_1;
-- ALTER TABLE treatments DROP COLUMN pest_id;

