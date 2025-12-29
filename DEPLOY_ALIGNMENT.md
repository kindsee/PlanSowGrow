# Guía de Despliegue - Actualización de Alineación

## Fecha: 2024
## Cambios: Sistema de alineación para evitar superposición de iconos

---

## Pasos para Desplegar en Servidor Ubuntu

### 1. Respaldar Base de Datos (IMPORTANTE)

```bash
cd /home/jmgalaminos/PlanSowGrow
mysqldump -u plansowgrow_user -p plansowgrow > backups/backup_$(date +%Y%m%d_%H%M%S).sql
```

### 2. Actualizar Código desde GitHub

```bash
cd /home/jmgalaminos/PlanSowGrow
git pull origin main
```

### 3. Revisar Archivos Modificados

Los siguientes archivos han sido modificados y deben estar presentes:

**Archivos Backend:**
- `models.py` - Campo `alignment` en CulturePlant
- `services.py` - Parámetro `alignments` en create_culture()
- `routes.py` - Procesamiento de alignment en create/edit

**Archivos Frontend:**
- `templates/cultures/create.html` - Selector de alineación
- `templates/cultures/edit.html` - Selector de alineación con valor actual
- `templates/cultures/view.html` - Visualización de alineación
- `templates/beds/view.html` - Pasa alignment al visualizador
- `static/js/bancal-visualizer.js` - Lógica de posicionamiento

**Migración:**
- `migrations/004_add_visual_plantation.sql` - Añade columna alignment

**Documentación:**
- `CHANGELOG_ALIGNMENT.md` - Documentación detallada de cambios
- `README.md` - Actualizado con nueva funcionalidad

### 4. Ejecutar Migración de Base de Datos

```bash
cd /home/jmgalaminos/PlanSowGrow
python3 run_migration.py migrations/004_add_visual_plantation.sql
```

**Salida esperada:**
```
Running migration: Add visual plantation fields...
✅ Migration completed successfully!
✅ Columns added: icon, row_position, spacing_cm, alignment
✅ Plant icons updated
```

### 5. Verificar Migración

```bash
mysql -u plansowgrow_user -p plansowgrow -e "DESCRIBE culture_plants;"
```

**Debes ver las siguientes columnas:**
```
+-------------------+------------------------------------------------+------+-----+---------+
| Field             | Type                                           | Null | Key | Default |
+-------------------+------------------------------------------------+------+-----+---------+
| id                | int(11)                                        | NO   | PRI | NULL    |
| culture_id        | int(11)                                        | NO   | MUL | NULL    |
| plant_id          | int(11)                                        | NO   | MUL | NULL    |
| quantity_planted  | int(11)                                        | YES  |     | 1       |
| quantity_grown    | int(11)                                        | YES  |     | NULL    |
| icon              | varchar(10)                                    | YES  |     | 🌱      |
| row_position      | enum('superior','central','inferior')          | YES  |     | central |
| spacing_cm        | int(11)                                        | YES  |     | 30      |
| alignment         | enum('left','center','right')                  | YES  |     | center  |
+-------------------+------------------------------------------------+------+-----+---------+
```

### 6. Reiniciar Apache

```bash
sudo systemctl restart apache2
```

### 7. Verificar Estado del Servicio

```bash
sudo systemctl status apache2
```

**Salida esperada:**
```
● apache2.service - The Apache HTTP Server
   Loaded: loaded (/lib/systemd/system/apache2.service; enabled)
   Active: active (running) since ...
```

### 8. Verificar Logs (si hay errores)

```bash
# Logs de Apache
sudo tail -f /var/log/apache2/error.log

# Logs específicos de PlanSowGrow
sudo tail -f /var/log/apache2/plansowgrow_error.log
```

---

## Verificación de Funcionalidad

### Prueba 1: Crear Cultivo con Alineación

1. Navegar a: http://192.168.68.200:8082/cultures/create
2. Seleccionar un bancal
3. Agregar al menos 2 plantas diferentes
4. Para cada planta:
   - Seleccionar la misma fila (ej: superior)
   - Asignar diferentes alineaciones (izquierda y derecha)
   - Guardar cultivo

**Resultado esperado:** Cultivo creado sin errores

### Prueba 2: Visualizar Bancal

1. Navegar a la vista del bancal (ej: /beds/1)
2. Verificar que aparece el canvas de visualización
3. Comprobar que los iconos de las plantas no se superponen

**Resultado esperado:** Los iconos se muestran correctamente alineados

### Prueba 3: Editar Cultivo Existente

1. Editar un cultivo: /cultures/<id>/edit
2. Cambiar la alineación de una planta
3. Guardar cambios
4. Ver bancal de nuevo

**Resultado esperado:** La visualización refleja los cambios

---

## Rollback (si algo sale mal)

### Opción 1: Restaurar Base de Datos

```bash
cd /home/jmgalaminos/PlanSowGrow
mysql -u plansowgrow_user -p plansowgrow < backups/backup_YYYYMMDD_HHMMSS.sql
```

### Opción 2: Revertir Código

```bash
cd /home/jmgalaminos/PlanSowGrow
git log --oneline  # Ver commits
git revert <commit-hash>  # Revertir commit específico
# O
git reset --hard HEAD~1  # Volver al commit anterior (CUIDADO)
```

### Opción 3: Eliminar Columna de Migración

```bash
mysql -u plansowgrow_user -p plansowgrow -e "ALTER TABLE culture_plants DROP COLUMN alignment;"
```

---

## Comandos Útiles

### Verificar Conexión a Base de Datos

```bash
mysql -u plansowgrow_user -p plansowgrow -e "SELECT COUNT(*) FROM culture_plants;"
```

### Ver Cultivos con Alignment

```bash
mysql -u plansowgrow_user -p plansowgrow -e "SELECT id, culture_id, plant_id, alignment FROM culture_plants LIMIT 10;"
```

### Reiniciar Solo WSGI (más rápido)

```bash
sudo touch /home/jmgalaminos/PlanSowGrow/plansowgrow.wsgi
```

### Ver Procesos de Apache

```bash
ps aux | grep apache
```

---

## Troubleshooting

### Error: "Unknown column 'alignment'"

**Causa:** La migración no se ejecutó correctamente

**Solución:**
```bash
python3 run_migration.py migrations/004_add_visual_plantation.sql
```

### Error: "Syntax error in JavaScript"

**Causa:** Error en bancal-visualizer.js

**Solución:**
1. Verificar que el archivo se subió correctamente
2. Limpiar caché del navegador (Ctrl+Shift+R)
3. Verificar en consola de desarrollador (F12)

### Error: "Internal Server Error (500)"

**Causa:** Error de Python en el backend

**Solución:**
```bash
# Ver logs detallados
sudo tail -50 /var/log/apache2/plansowgrow_error.log

# Verificar sintaxis Python
cd /home/jmgalaminos/PlanSowGrow
python3 -m py_compile models.py
python3 -m py_compile services.py
python3 -m py_compile routes.py
```

### Canvas no muestra plantas

**Causa:** JavaScript no se carga o hay error en datos

**Solución:**
1. Abrir consola de desarrollador (F12)
2. Ver errores en pestaña Console
3. Verificar que culture_plants tiene datos:
```bash
mysql -u plansowgrow_user -p plansowgrow -e "SELECT * FROM culture_plants WHERE culture_id = <id>;"
```

---

## Contacto de Soporte

Si encuentras problemas durante el despliegue:
1. Revisar logs de Apache
2. Verificar que la migración se ejecutó
3. Comprobar que todos los archivos se actualizaron desde GitHub
4. Realizar rollback si es necesario

---

## Checklist de Despliegue

- [ ] Backup de base de datos realizado
- [ ] Código actualizado desde GitHub
- [ ] Migración ejecutada correctamente
- [ ] Apache reiniciado
- [ ] Prueba 1: Crear cultivo con alineación - OK
- [ ] Prueba 2: Visualizar bancal - OK
- [ ] Prueba 3: Editar cultivo existente - OK
- [ ] Logs revisados - Sin errores

---

**Fecha de despliegue:** _______________
**Realizado por:** _______________
**Notas adicionales:** _______________
