#!/bin/bash
# Script de deployment para PlanSowGrow en Ubuntu con Apache

set -e  # Exit on error

echo "================================================"
echo "  Deployment Script para PlanSowGrow"
echo "================================================"
echo ""

# Variables de configuración
APP_DIR="/var/www/plansowgrow"
REPO_URL="https://github.com/kindsee/PlanSowGrow.git"
VENV_DIR="$APP_DIR/venv"
APACHE_CONF="/etc/apache2/sites-available/plansowgrow.conf"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Paso 1: Verificando dependencias del sistema...${NC}"
# Verificar que Apache y mod_wsgi estén instalados
if ! command -v apache2 &> /dev/null; then
    echo -e "${RED}Apache no está instalado. Instalando...${NC}"
    sudo apt-get update
    sudo apt-get install -y apache2
fi

if ! dpkg -l | grep -q libapache2-mod-wsgi-py3; then
    echo -e "${RED}mod_wsgi para Python 3 no está instalado. Instalando...${NC}"
    sudo apt-get install -y libapache2-mod-wsgi-py3
fi

# Verificar que Python 3 y pip estén instalados
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 no está instalado. Por favor instálalo primero.${NC}"
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}pip3 no está instalado. Instalando...${NC}"
    sudo apt-get install -y python3-pip python3-venv
fi

# Verificar MariaDB/MySQL
if ! command -v mysql &> /dev/null; then
    echo -e "${YELLOW}MariaDB no está instalado. Asegúrate de instalarlo:${NC}"
    echo "  sudo apt-get install mariadb-server"
    echo "  sudo mysql_secure_installation"
    read -p "¿Continuar de todas formas? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${GREEN}✓ Dependencias verificadas${NC}"
echo ""

echo -e "${YELLOW}Paso 2: Creando directorio de aplicación...${NC}"
if [ ! -d "$APP_DIR" ]; then
    sudo mkdir -p "$APP_DIR"
    echo -e "${GREEN}✓ Directorio creado${NC}"
else
    echo -e "${GREEN}✓ Directorio ya existe${NC}"
fi

echo -e "${YELLOW}Paso 3: Clonando/actualizando repositorio...${NC}"
if [ -d "$APP_DIR/.git" ]; then
    echo "Actualizando repositorio existente..."
    cd "$APP_DIR"
    sudo git pull origin main
else
    echo "Clonando repositorio..."
    sudo git clone "$REPO_URL" "$APP_DIR"
fi
echo -e "${GREEN}✓ Código actualizado${NC}"
echo ""

echo -e "${YELLOW}Paso 4: Configurando entorno virtual Python...${NC}"
if [ ! -d "$VENV_DIR" ]; then
    sudo python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}✓ Entorno virtual creado${NC}"
else
    echo -e "${GREEN}✓ Entorno virtual ya existe${NC}"
fi

echo -e "${YELLOW}Paso 5: Instalando dependencias Python...${NC}"
cd "$APP_DIR"
sudo "$VENV_DIR/bin/pip" install --upgrade pip
sudo "$VENV_DIR/bin/pip" install -r requirements.txt
echo -e "${GREEN}✓ Dependencias instaladas${NC}"
echo ""

echo -e "${YELLOW}Paso 6: Configurando archivo .env...${NC}"
if [ ! -f "$APP_DIR/.env" ]; then
    if [ -f "$APP_DIR/.env.production.example" ]; then
        sudo cp "$APP_DIR/.env.production.example" "$APP_DIR/.env"
        echo -e "${YELLOW}⚠ Archivo .env creado desde ejemplo${NC}"
        echo -e "${YELLOW}⚠ IMPORTANTE: Edita $APP_DIR/.env con tus valores reales${NC}"
        echo -e "${YELLOW}   Especialmente: SECRET_KEY, DB_PASSWORD${NC}"
    else
        echo -e "${RED}✗ No se encontró .env.production.example${NC}"
    fi
else
    echo -e "${GREEN}✓ Archivo .env ya existe${NC}"
fi
echo ""

echo -e "${YELLOW}Paso 7: Configurando base de datos...${NC}"
echo "Ejecuta estos comandos en MySQL/MariaDB (como root):"
echo ""
echo "  sudo mysql"
echo "  CREATE DATABASE IF NOT EXISTS plansowgrow CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
echo "  CREATE USER IF NOT EXISTS 'plansowgrow_user'@'localhost' IDENTIFIED BY 'tu_contraseña';"
echo "  GRANT ALL PRIVILEGES ON plansowgrow.* TO 'plansowgrow_user'@'localhost';"
echo "  FLUSH PRIVILEGES;"
echo "  EXIT;"
echo ""
echo "Luego ejecuta las migraciones:"
echo "  cd $APP_DIR"
echo "  source venv/bin/activate"
echo "  python init_db.py"
echo ""
read -p "Presiona Enter cuando hayas configurado la base de datos..."
echo ""

echo -e "${YELLOW}Paso 8: Configurando permisos...${NC}"
sudo chown -R www-data:www-data "$APP_DIR"
sudo chmod -R 755 "$APP_DIR"
sudo chmod 600 "$APP_DIR/.env"  # Proteger archivo de configuración
echo -e "${GREEN}✓ Permisos configurados${NC}"
echo ""

echo -e "${YELLOW}Paso 9: Configurando Apache...${NC}"
if [ -f "$APP_DIR/apache-plansowgrow.conf" ]; then
    sudo cp "$APP_DIR/apache-plansowgrow.conf" "$APACHE_CONF"
    echo -e "${GREEN}✓ Configuración de Apache copiada${NC}"
    echo -e "${YELLOW}⚠ Edita $APACHE_CONF para ajustar ServerName y otros valores${NC}"
else
    echo -e "${RED}✗ No se encontró apache-plansowgrow.conf${NC}"
fi
echo ""

echo -e "${YELLOW}Paso 10: Habilitando sitio y módulos...${NC}"
sudo a2enmod wsgi
sudo a2ensite plansowgrow.conf
echo -e "${GREEN}✓ Sitio habilitado${NC}"
echo ""

echo -e "${YELLOW}Paso 11: Verificando configuración de Apache...${NC}"
sudo apache2ctl configtest
echo ""

echo -e "${YELLOW}Paso 12: Reiniciando Apache...${NC}"
sudo systemctl restart apache2
echo -e "${GREEN}✓ Apache reiniciado${NC}"
echo ""

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  Deployment completado!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "${YELLOW}Pasos siguientes:${NC}"
echo "1. Edita $APP_DIR/.env con tus valores de producción"
echo "2. Edita $APACHE_CONF con tu dominio"
echo "3. Configura la base de datos (ver comandos arriba)"
echo "4. Ejecuta: python init_db.py para crear las tablas"
echo "5. Ejecuta las migraciones de la carpeta migrations/"
echo "6. Reinicia Apache: sudo systemctl restart apache2"
echo ""
echo -e "${YELLOW}Para ver logs de errores:${NC}"
echo "  sudo tail -f /var/log/apache2/plansowgrow-error.log"
echo ""
echo -e "${YELLOW}Para actualizar la aplicación:${NC}"
echo "  cd $APP_DIR && sudo git pull && sudo systemctl restart apache2"
echo ""
