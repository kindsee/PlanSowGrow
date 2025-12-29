-- Migration: Add culture_cares table
-- Date: 2025-12-29
-- Description: Adds support for assigning care actions to specific cultures

-- Create culture_cares table
CREATE TABLE IF NOT EXISTS culture_cares (
    id INT AUTO_INCREMENT PRIMARY KEY,
    culture_id INT NOT NULL,
    care_action_id INT NOT NULL,
    scheduled_date DATE NOT NULL,
    frequency_days INT,
    notes TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (culture_id) REFERENCES cultures(id) ON DELETE CASCADE,
    FOREIGN KEY (care_action_id) REFERENCES care_actions(id) ON DELETE CASCADE,
    INDEX idx_culture_id (culture_id),
    INDEX idx_care_action_id (care_action_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Verify table was created
SELECT 'Table culture_cares created successfully' AS status;
