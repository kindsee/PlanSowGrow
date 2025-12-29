-- Migration: Add culture_treatments table
-- Date: 2025-12-29
-- Description: Adds support for assigning treatments to specific cultures

-- Create culture_treatments table
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Verify table was created
SELECT 'Table culture_treatments created successfully' AS status;
