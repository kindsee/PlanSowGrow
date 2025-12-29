-- Migration 004: Add visual plantation layout fields
-- Adds icon field to plants and plantation pattern fields to culture_plants

-- Add icon field to plants table
ALTER TABLE plants 
ADD COLUMN icon VARCHAR(10) DEFAULT '🌱' AFTER description;

-- Add visual plantation layout fields to culture_plants table
ALTER TABLE culture_plants
ADD COLUMN row_position ENUM('superior', 'central', 'inferior') DEFAULT 'central' AFTER quantity_grown,
ADD COLUMN spacing_cm INT DEFAULT 30 AFTER row_position,
ADD COLUMN alignment ENUM('left', 'center', 'right') DEFAULT 'center' AFTER spacing_cm;

-- Update common plants with appropriate icons
UPDATE plants SET icon = '🍅' WHERE name LIKE '%tomate%' OR name LIKE '%Tomate%';
UPDATE plants SET icon = '🌶️' WHERE name LIKE '%pimiento%' OR name LIKE '%Pimiento%';
UPDATE plants SET icon = '🍆' WHERE name LIKE '%berenjena%' OR name LIKE '%Berenjena%';
UPDATE plants SET icon = '🥕' WHERE name LIKE '%zanahoria%' OR name LIKE '%Zanahoria%';
UPDATE plants SET icon = '🥬' WHERE name LIKE '%lechuga%' OR name LIKE '%Lechuga%';
UPDATE plants SET icon = '🧅' WHERE name LIKE '%cebolla%' OR name LIKE '%Cebolla%';
UPDATE plants SET icon = '🥒' WHERE name LIKE '%pepino%' OR name LIKE '%Pepino%';
UPDATE plants SET icon = '🌾' WHERE name LIKE '%haba%' OR name LIKE '%Haba%' OR name LIKE '%guisante%' OR name LIKE '%Guisante%';
UPDATE plants SET icon = '🌽' WHERE name LIKE '%maíz%' OR name LIKE '%Maíz%';
UPDATE plants SET icon = '🥔' WHERE name LIKE '%patata%' OR name LIKE '%Patata%';
UPDATE plants SET icon = '🧄' WHERE name LIKE '%ajo%' OR name LIKE '%Ajo%';
UPDATE plants SET icon = '🌿' WHERE name LIKE '%judía%' OR name LIKE '%Judía%' OR name LIKE '%alubia%' OR name LIKE '%Alubia%';
UPDATE plants SET icon = '🥦' WHERE name LIKE '%brócoli%' OR name LIKE '%Brócoli%' OR name LIKE '%broccoli%' OR name LIKE '%Broccoli%' OR name LIKE '%brokoli%' OR name LIKE '%Brokoli%';
UPDATE plants SET icon = '🥬' WHERE name LIKE '%col %' OR name LIKE '%Col %' OR name LIKE '%repollo%' OR name LIKE '%Repollo%';
UPDATE plants SET icon = '🌼' WHERE name LIKE '%coliflor%' OR name LIKE '%Coliflor%';
UPDATE plants SET icon = '🍓' WHERE name LIKE '%fresa%' OR name LIKE '%Fresa%';
UPDATE plants SET icon = '🌸' WHERE name LIKE '%flor%' OR name LIKE '%Flor%';
UPDATE plants SET icon = '💚' WHERE name LIKE '%alcachofa%' OR name LIKE '%Alcachofa%' OR name LIKE '%alcahofa%' OR name LIKE '%Alcahofa%';
UPDATE plants SET icon = '🍉' WHERE name LIKE '%sandía%' OR name LIKE '%Sandía%';
UPDATE plants SET icon = '🍈' WHERE name LIKE '%melón%' OR name LIKE '%Melón%';
