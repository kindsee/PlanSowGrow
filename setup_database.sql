-- Script para configurar la base de datos y usuario de PlanSowGrow
-- Ejecuta estos comandos en MariaDB como root

-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS plansowgrow CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Crear el usuario
-- Cambia 'tu_contraseña_segura' por una contraseña real
CREATE USER IF NOT EXISTS 'plansowgrow_user'@'localhost' IDENTIFIED BY 'tu_contraseña_segura';

-- Otorgar privilegios al usuario en la base de datos
GRANT ALL PRIVILEGES ON plansowgrow.* TO 'plansowgrow_user'@'localhost';

-- Si necesitas acceso desde la red local (192.168.x.x)
CREATE USER IF NOT EXISTS 'plansowgrow_user'@'192.168.%' IDENTIFIED BY 'tu_contraseña_segura';
GRANT ALL PRIVILEGES ON plansowgrow.* TO 'plansowgrow_user'@'192.168.%';

-- Aplicar los cambios
FLUSH PRIVILEGES;

-- Verificar que el usuario fue creado
SELECT User, Host FROM mysql.user WHERE User = 'plansowgrow_user';

-- Verificar que la base de datos fue creada
SHOW DATABASES LIKE 'plansowgrow';
