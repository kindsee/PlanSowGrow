# Guía de Deployment - PlanSowGrow en Ubuntu con Apache

Esta guía explica cómo desplegar PlanSowGrow en un servidor Ubuntu usando Apache y mod_wsgi.

## Requisitos Previos

- Servidor Ubuntu 20.04+ con acceso root/sudo
- Python 3.8 o superior
- MariaDB/MySQL instalado y configurado
- Apache2 instalado
- Acceso SSH al servidor

## Instalación Rápida

### 1. Preparar el Servidor

```bash
# Actualizar el sistema
sudo apt-get update
sudo apt-get upgrade -y

# Instalar dependencias
sudo apt-get install -y apache2 libapache2-mod-wsgi-py3 python3-pip python3-venv git mariadb-server

# Asegurar MariaDB
sudo mysql_secure_installation
```

### 2. Clonar el Repositorio

```bash
# Crear directorio de la aplicación
sudo mkdir -p /var/www/plansowgrow
cd /var/www/plansowgrow

# Clonar desde GitHub
sudo git clone https://github.com/kindsee/PlanSowGrow.git .
```

### 3. Ejecutar Script de Deployment

El proyecto incluye un script automático:

```bash
cd /var/www/plansowgrow
sudo chmod +x deploy.sh
sudo ./deploy.sh
```

El script realizará:
- ✅ Verificación de dependencias
- ✅ Creación del entorno virtual Python
- ✅ Instalación de paquetes Python
- ✅ Configuración de Apache
- ✅ Configuración de permisos

### 4. Configurar Base de Datos

```bash
# Acceder a MariaDB
sudo mysql

# Crear base de datos y usuario
CREATE DATABASE IF NOT EXISTS plansowgrow CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'plansowgrow_user'@'localhost' IDENTIFIED BY 'tu_contraseña_segura';
GRANT ALL PRIVILEGES ON plansowgrow.* TO 'plansowgrow_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 5. Configurar Variables de Entorno

```bash
# Editar archivo .env
sudo nano /var/www/plansowgrow/.env
```

Configurar estos valores:

```env
SECRET_KEY=genera-una-clave-muy-larga-y-aleatoria-aqui
FLASK_ENV=production

DB_HOST=localhost
DB_PORT=3306
DB_NAME=plansowgrow
DB_USER=plansowgrow_user
DB_PASSWORD=tu_contraseña_segura
```

**Generar SECRET_KEY segura:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 6. Inicializar Base de Datos

```bash
cd /var/www/plansowgrow
source venv/bin/activate

# Crear tablas iniciales
python init_db.py

# Ejecutar migraciones
cd migrations
mysql -u plansowgrow_user -p plansowgrow < 001_add_culture_treatments.sql
mysql -u plansowgrow_user -p plansowgrow < 002_add_culture_cares.sql
mysql -u plansowgrow_user -p plansowgrow < 003_add_pest_treatments.sql

# O usar los scripts Python
cd ..
python fix_pest_treatments.py
python check_plant_pests_table.py
```

### 7. Configurar Apache

Editar la configuración del sitio:

```bash
sudo nano /etc/apache2/sites-available/plansowgrow.conf
```

Ajustar `ServerName` y `ServerAlias`:

```apache
ServerName plansowgrow.tudominio.com
ServerAlias www.plansowgrow.tudominio.com
```

### 8. Activar y Reiniciar

```bash
# Habilitar módulos y sitio
sudo a2enmod wsgi
sudo a2ensite plansowgrow.conf

# Verificar configuración
sudo apache2ctl configtest

# Reiniciar Apache
sudo systemctl restart apache2
```

## Verificación

### Verificar que la aplicación está corriendo:

```bash
# Ver estado de Apache
sudo systemctl status apache2

# Ver logs en tiempo real
sudo tail -f /var/log/apache2/plansowgrow-error.log
sudo tail -f /var/log/apache2/plansowgrow-access.log

# Probar desde el navegador
curl http://localhost
# O accede desde tu navegador a tu dominio/IP
```

## Mantenimiento

### Actualizar la Aplicación

```bash
cd /var/www/plansowgrow
sudo git pull origin main
source venv/bin/activate
sudo venv/bin/pip install -r requirements.txt
sudo systemctl restart apache2
```

### Ver Logs

```bash
# Errores de la aplicación
sudo tail -f /var/log/apache2/plansowgrow-error.log

# Accesos
sudo tail -f /var/log/apache2/plansowgrow-access.log

# Apache general
sudo journalctl -u apache2 -f
```

### Backup de Base de Datos

```bash
# Crear backup
mysqldump -u plansowgrow_user -p plansowgrow > backup_$(date +%Y%m%d).sql

# Restaurar backup
mysql -u plansowgrow_user -p plansowgrow < backup_20251229.sql
```

## Troubleshooting

### Error 500 - Internal Server Error

1. Verificar logs:
   ```bash
   sudo tail -100 /var/log/apache2/plansowgrow-error.log
   ```

2. Verificar permisos:
   ```bash
   sudo chown -R www-data:www-data /var/www/plansowgrow
   sudo chmod -R 755 /var/www/plansowgrow
   ```

3. Verificar .env:
   ```bash
   ls -la /var/www/plansowgrow/.env
   ```

### Error de Base de Datos

1. Verificar que MariaDB está corriendo:
   ```bash
   sudo systemctl status mariadb
   ```

2. Verificar credenciales en .env

3. Probar conexión:
   ```bash
   mysql -u plansowgrow_user -p plansowgrow
   ```

### Apache no arranca

1. Verificar configuración:
   ```bash
   sudo apache2ctl configtest
   ```

2. Verificar puertos:
   ```bash
   sudo netstat -tulpn | grep :80
   ```

## Configuración SSL (Opcional pero Recomendado)

### Con Let's Encrypt (Certbot):

```bash
# Instalar Certbot
sudo apt-get install certbot python3-certbot-apache

# Obtener certificado
sudo certbot --apache -d plansowgrow.tudominio.com -d www.plansowgrow.tudominio.com

# Renovación automática está configurada
sudo certbot renew --dry-run
```

## Seguridad Adicional

### Configurar Firewall

```bash
sudo ufw allow 'Apache Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

### Proteger archivo .env

```bash
sudo chmod 600 /var/www/plansowgrow/.env
sudo chown www-data:www-data /var/www/plansowgrow/.env
```

## Contacto y Soporte

Para problemas o preguntas, consulta:
- README.md del proyecto
- Issues en GitHub: https://github.com/kindsee/PlanSowGrow/issues
