# Pasos de Deployment para PlanSowGrow en tu Servidor Ubuntu

## 📍 Configuración específica de tu servidor
- **Directorio**: `/home/jmgalaminos/PlanSowGrow`
- **Puerto**: 8082
- **IP**: 192.168.68.200
- **Usuario**: jmgalaminos
- **Base de datos**: Ya existente con datos

---

## 🚀 Pasos a seguir (en el servidor Ubuntu)

### 1. Crear el entorno virtual Python

```bash
cd /home/jmgalaminos/PlanSowGrow
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Crear el archivo .env

```bash
nano /home/jmgalaminos/PlanSowGrow/.env
```

Contenido del archivo `.env` (ajusta DB_PASSWORD con tu contraseña real):

```env
SECRET_KEY=<genera-una-clave-con-el-comando-de-abajo>
FLASK_ENV=production

DB_HOST=localhost
DB_PORT=3306
DB_NAME=plansowgrow
DB_USER=plansowgrow_user
DB_PASSWORD=TU_CONTRASEÑA_REAL
```

**Generar SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Proteger el archivo .env

```bash
chmod 600 /home/jmgalaminos/PlanSowGrow/.env
```

### 4. Configurar Apache para escuchar en puerto 8082

```bash
# Editar archivo de puertos
sudo nano /etc/apache2/ports.conf
```

Añade esta línea si no existe:
```apache
Listen 8082
```

### 5. Copiar la configuración del sitio

```bash
sudo cp /home/jmgalaminos/PlanSowGrow/apache-plansowgrow.conf /etc/apache2/sites-available/plansowgrow.conf
```

### 6. Habilitar módulos necesarios y el sitio

```bash
sudo a2enmod wsgi
sudo a2ensite plansowgrow.conf
```

### 7. Verificar la configuración de Apache

```bash
sudo apache2ctl configtest
```

Debe decir: **Syntax OK**

### 8. Reiniciar Apache

```bash
sudo systemctl restart apache2
```

### 9. Verificar que está funcionando

```bash
# Ver el estado de Apache
sudo systemctl status apache2

# Ver los logs en tiempo real
sudo tail -f /var/log/apache2/plansowgrow-error.log

# Probar desde el navegador o con curl
curl http://192.168.68.200:8082
```

---

## 🔍 Troubleshooting

### Si hay error de permisos:

```bash
# Dar permisos adecuados
chmod 755 /home/jmgalaminos/PlanSowGrow
chmod +x /home/jmgalaminos/PlanSowGrow/plansowgrow.wsgi

# Si persiste, puedes ajustar el grupo
sudo chgrp www-data /home/jmgalaminos/PlanSowGrow
```

### Ver logs de errores:

```bash
# Errores de Apache
sudo tail -50 /var/log/apache2/error.log

# Errores específicos de PlanSowGrow
sudo tail -50 /var/log/apache2/plansowgrow-error.log

# Logs del sistema
sudo journalctl -u apache2 -n 50
```

### Si el puerto 8082 está en uso:

```bash
# Ver qué está usando el puerto
sudo netstat -tulpn | grep 8082

# O con ss
sudo ss -tulpn | grep 8082
```

### Reiniciar Apache si haces cambios:

```bash
sudo systemctl restart apache2
```

---

## 📝 Acceder a la aplicación

Una vez todo esté funcionando, accede desde tu navegador a:

```
http://192.168.68.200:8082
```

---

## 🔄 Actualizar la aplicación en el futuro

```bash
cd /home/jmgalaminos/PlanSowGrow
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart apache2
```

---

## 📊 Comandos útiles

### Ver logs en tiempo real:
```bash
sudo tail -f /var/log/apache2/plansowgrow-error.log
sudo tail -f /var/log/apache2/plansowgrow-access.log
```

### Verificar conexión a base de datos:
```bash
mysql -u plansowgrow_user -p plansowgrow
```

### Estado de Apache:
```bash
sudo systemctl status apache2
```

### Reiniciar Apache:
```bash
sudo systemctl restart apache2
```
