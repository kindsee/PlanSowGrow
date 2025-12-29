# Visualización Gráfica de Bancales - Nueva Funcionalidad

## 📋 Descripción

Se ha implementado una visualización gráfica Canvas para los bancales que muestra la distribución real de las plantas según su espaciado y posición en filas.

## ✨ Características Implementadas

### 1. **Campos Nuevos en Base de Datos**

#### Tabla `plants`:
- `icon` (VARCHAR(10)): Emoji que representa visualmente la planta (🍅, 🫑, 🍆, etc.)

#### Tabla `culture_plants`:
- `row_position` (ENUM: 'superior', 'central', 'inferior'): Fila donde se planta en el bancal
- `spacing_cm` (INT): Espaciado entre plantas en centímetros

### 2. **Espaciados Disponibles**
- 15 cm
- 20 cm  
- 30 cm (por defecto)
- 40 cm
- 50 cm
- 100 cm

### 3. **Visualización Canvas**

La visualización muestra:
- Bancal de 4m x 1m dividido en 3 filas
- Plantas representadas con su icono emoji
- Círculos de color según el tipo de planta
- Espaciado real según configuración
- Leyenda con información de cada cultivo

## 🚀 Migración de Base de Datos

Ejecuta la migración para añadir los nuevos campos:

```bash
cd /home/jmgalaminos/PlanSowGrow
source venv/bin/activate
mysql -u plansowgrow_user -p plansowgrow < migrations/004_add_visual_plantation.sql
```

Esta migración:
1. Añade el campo `icon` a la tabla `plants`
2. Añade `row_position` y `spacing_cm` a `culture_plants`
3. Actualiza plantas comunes con iconos apropiados

## 📝 Uso

### Al Crear una Planta

1. Ve a **Plantas** > **Nueva Planta**
2. Rellena el nombre
3. **Selecciona un emoji** para el icono (🍅, 🫑, 🍆, 🥕, etc.)
4. Completa el resto de información

### Al Crear un Cultivo

1. Ve a **Cultivos** > **Nuevo Cultivo**
2. Selecciona el bancal y la fecha
3. Para cada planta añadida, configura:
   - **Cantidad sembrada**: Número de semillas/plántulas iniciales
   - **Cantidad crecida**: Plantas que se desarrollaron exitosamente
   - **Fila**: Superior, Central o Inferior
   - **Espaciado**: 15, 20, 30, 40, 50 o 100 cm

### Visualización del Bancal

1. Ve a **Bancales** > Selecciona un bancal
2. Si hay cultivos activos, verás la **Visualización del Bancal**
3. El canvas muestra:
   - Grid de referencia
   - Líneas de división de filas
   - Plantas posicionadas según configuración
   - Leyenda con detalles

## 🎨 Ejemplos de Iconos

```
🍅 Tomate
🌶️ Pimiento  
🍆 Berenjena
🥕 Zanahoria
🥬 Lechuga
🧅 Cebolla
🥒 Pepino
🌾 Haba / Guisante
🌽 Maíz
🥔 Patata
🧄 Ajo
🌿 Judía / Alubia
🥦 Brócoli
🥬 Col / Repollo
🌼 Coliflor
🍓 Fresa
🌸 Flor decorativa
💚 Alcachofa
🍉 Sandía
🍈 Melón
🌱 Genérico (por defecto)
```

## 🔧 Archivos Modificados

### Modelos
- `models.py`: Añadidos campos `icon`, `row_position`, `spacing_cm`

### Servicios
- `services.py`: Actualizados `create_plant()` y `create_culture()` para manejar nuevos campos

### Rutas
- `routes.py`: Actualizadas rutas de plantas y cultivos, añadido `active_cultures` al view_bed

### Templates
- `templates/plants/create.html`: Campo para icono
- `templates/cultures/create.html`: Campos para fila y espaciado
- `templates/beds/view.html`: Canvas de visualización

### Archivos Nuevos
- `static/js/bancal-visualizer.js`: Clase JavaScript para renderizar el canvas
- `static/css/bancal-visualizer.css`: Estilos para la visualización
- `migrations/004_add_visual_plantation.sql`: Migración SQL

## 📊 Ejemplo de Uso Real

Para plantar **13 habas en los bordes exteriores espaciadas 40 cm**:

1. Crear cultivo nuevo
2. Añadir planta "Haba" (🫛)
3. Configurar:
   - Cantidad crecida: 13
   - Fila: Superior (para el borde superior) o Inferior (para el borde inferior)
   - Espaciado: 40 cm
4. Si quieres ambos bordes, añade la misma planta dos veces con filas diferentes

El canvas calculará automáticamente la distribución centrando las 13 plantas con 40cm de separación en la fila seleccionada.

## 🐛 Troubleshooting

### El canvas no aparece
- Verifica que hay cultivos activos en el bancal
- Revisa la consola del navegador por errores JavaScript
- Asegúrate de que los archivos static están accesibles

### Los iconos no se muestran correctamente
- Verifica que el navegador soporta emojis
- Asegúrate de que el charset de la base de datos es utf8mb4

### Error al crear cultivo
- Ejecuta la migración 004
- Verifica que los nuevos campos existen en la BD

## 📚 Próximas Mejoras Potenciales

- [ ] Click en plantas para ver detalles
- [ ] Arrastrar y soltar para reposicionar
- [ ] Vista 3D del bancal
- [ ] Histórico visual de rotaciones
- [ ] Exportar imagen del bancal
- [ ] Compatibilidad con bancales de diferentes tamaños

