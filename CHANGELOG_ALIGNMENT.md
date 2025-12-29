# Changelog - Parámetro de Alineación

## Fecha: 2024
## Objetivo: Evitar superposición de iconos en la visualización del bancal

### Problema
Cuando múltiples plantas se colocan en la misma fila (superior, central o inferior), los iconos se superponían porque todas las plantas se centraban horizontalmente en el bancal.

**Ejemplo del problema:**
- Tomates en fila superior con espaciado 30cm (centrados)
- Coles en fila superior con espaciado 40cm (centrados)
- Resultado: Los iconos se superponían en el centro

### Solución
Se ha añadido un parámetro de **alineación** (izquierda, centro, derecha) que permite distribuir las plantas horizontalmente dentro de su fila, evitando así las superposiciones.

**Ejemplo de solución:**
- Tomates en fila superior, alineación derecha, espaciado 30cm
- Coles en fila superior, alineación izquierda, espaciado 40cm
- Resultado: Los iconos no se superponen

---

## Cambios Realizados

### 1. Modelo de Datos (`models.py`)
```python
# Se añadió campo alignment al modelo CulturePlant
alignment = db.Column(
    db.Enum('left', 'center', 'right', name='alignment_type'),
    nullable=False,
    default='center',
    comment='Horizontal alignment of plants in row'
)
```

### 2. Migración de Base de Datos (`migrations/004_add_visual_plantation.sql`)
```sql
-- Se añadieron 4 columnas a la tabla culture_plants:
ALTER TABLE culture_plants 
    ADD COLUMN icon VARCHAR(10) DEFAULT '🌱',
    ADD COLUMN row_position ENUM('superior', 'central', 'inferior') DEFAULT 'central',
    ADD COLUMN spacing_cm INT DEFAULT 30,
    ADD COLUMN alignment ENUM('left', 'center', 'right') DEFAULT 'center';

-- Se actualizaron iconos predeterminados para plantas comunes
UPDATE plants SET icon = '🍅' WHERE name LIKE '%tomate%';
UPDATE plants SET icon = '🥬' WHERE name LIKE '%col%' OR name LIKE '%repollo%';
-- ... más actualizaciones ...
```

### 3. Servicios (`services.py`)
```python
# Se añadió parámetro alignments a create_culture()
def create_culture(bed_id: int, start_date: date, start_type: str,
                   plant_ids: List[int], 
                   quantities_planted: List[int] = None,
                   quantities_grown: List[int] = None, 
                   row_positions: List[str] = None,
                   spacing_cms: List[int] = None,
                   alignments: List[str] = None,  # NUEVO
                   end_date: date = None,
                   notes: str = None) -> Culture:
    # ...
    alignment = alignments[i] if alignments and i < len(alignments) else 'center'
    culture_plant = CulturePlant(
        # ...
        alignment=alignment  # NUEVO
    )
```

### 4. Rutas (`routes.py`)

#### Ruta de Creación
```python
# Se extrae alignment del formulario
alignments = []
for plant_id in plant_ids:
    alignment = request.form.get(f'alignment_{plant_id}') or 'center'
    alignments.append(alignment)

# Se pasa al servicio
culture = services.create_culture(
    bed_id, start_date, start_type, plant_ids,
    quantities_planted, quantities_grown, 
    row_positions, spacing_cms, alignments,  # NUEVO
    notes=notes
)
```

#### Ruta de Edición
```python
# Se actualiza alignment si se proporciona
for cp in culture.plants:
    alignment = request.form.get(f'alignment_{cp.id}')
    if alignment:
        cp.alignment = alignment  # NUEVO
```

### 5. Plantillas HTML

#### Formulario de Creación (`templates/cultures/create.html`)
```html
<!-- Selector de alineación -->
<div class="col-md-2">
    <label for="alignment_{{ plant.id }}" class="form-label">Alineación</label>
    <select class="form-select" id="alignment_{{ plant.id }}" name="alignment_{{ plant.id }}">
        <option value="left">⬅️ Izquierda</option>
        <option value="center" selected>↔️ Centro</option>
        <option value="right">➡️ Derecha</option>
    </select>
</div>
```

#### Formulario de Edición (`templates/cultures/edit.html`)
```html
<!-- Selector de alineación con valor actual -->
<div class="col-md-2">
    <label for="alignment_{{ cp.id }}" class="form-label">Alineación</label>
    <select class="form-select" id="alignment_{{ cp.id }}" name="alignment_{{ cp.id }}">
        <option value="left" {% if cp.alignment == 'left' %}selected{% endif %}>⬅️ Izquierda</option>
        <option value="center" {% if cp.alignment == 'center' %}selected{% endif %}>↔️ Centro</option>
        <option value="right" {% if cp.alignment == 'right' %}selected{% endif %}>➡️ Derecha</option>
    </select>
</div>
```

#### Vista de Cultivo (`templates/cultures/view.html`)
```html
<!-- Muestra la alineación en la información de la planta -->
| Alineación: <span class="badge badge-sm bg-primary">
    {% if cp.alignment == 'left' %}⬅️ Izquierda
    {% elif cp.alignment == 'right' %}➡️ Derecha
    {% else %}↔️ Centro{% endif %}
</span>
```

### 6. Visualizador JavaScript (`static/js/bancal-visualizer.js`)

#### Cálculo de Posiciones
```javascript
calculatePlantPositions(quantity, spacingCm, rowPosition, alignment = 'center') {
    const positions = [];
    const yCm = this.getRowYCenter(rowPosition);
    const totalWidth = (quantity - 1) * spacingCm;
    
    // Determinar posición X inicial según alineación
    let startX;
    if (alignment === 'left') {
        startX = 0;
    } else if (alignment === 'right') {
        startX = this.BED_WIDTH_CM - totalWidth;
    } else { // center (default)
        startX = (this.BED_WIDTH_CM - totalWidth) / 2;
    }
    
    // Calcular posiciones individuales
    for (let i = 0; i < quantity; i++) {
        const xCm = startX + (i * spacingCm);
        positions.push({
            x: this.cmToPixel(xCm, 'x'),
            y: this.cmToPixel(yCm, 'y')
        });
    }
    
    return positions;
}
```

#### Renderizado
```javascript
drawCultures() {
    this.cultures.forEach(culture => {
        const positions = this.calculatePlantPositions(
            culture.quantity,
            culture.spacing,
            culture.row,
            culture.alignment || 'center'  // NUEVO
        );
        
        positions.forEach(pos => {
            this.drawPlant(pos.x, pos.y, culture.icon, culture.color);
        });
    });
}
```

#### Integración en Vista del Bancal (`templates/beds/view.html`)
```javascript
visualizer.addCulture({
    name: '{{ cp.plant.name }}',
    icon: '{{ cp.plant.icon }}',
    quantity: {{ cp.quantity_grown }},
    spacing: {{ cp.spacing_cm }},
    row: '{{ cp.row_position }}',
    alignment: '{{ cp.alignment or "center" }}',  // NUEVO
    color: getPlantColor('{{ cp.plant.name }}')
});
```

---

## Opciones de Alineación

| Valor | Emoji | Descripción | Uso Recomendado |
|-------|-------|-------------|-----------------|
| `left` | ⬅️ | Izquierda | Plantas que ocupan el lado izquierdo del bancal |
| `center` | ↔️ | Centro | Valor por defecto, centra las plantas (comportamiento original) |
| `right` | ➡️ | Derecha | Plantas que ocupan el lado derecho del bancal |

---

## Casos de Uso

### Caso 1: Una sola planta por fila
```
Fila superior: 13 tomates, espaciado 30cm, alineación centro
→ Comportamiento igual que antes
```

### Caso 2: Dos plantas en la misma fila
```
Fila superior: 
  - 8 tomates, espaciado 30cm, alineación derecha
  - 6 coles, espaciado 40cm, alineación izquierda
→ Las plantas no se superponen
```

### Caso 3: Tres filas diferentes
```
Fila superior: 10 lechugas, espaciado 20cm, alineación centro
Fila central: 8 tomates, espaciado 40cm, alineación izquierda
Fila inferior: 5 calabacines, espaciado 100cm, alineación derecha
→ Distribución vertical sin conflictos
```

---

## Testing

### Para Probar en Desarrollo
1. Crear un nuevo cultivo con múltiples plantas en la misma fila
2. Asignar diferentes alineaciones a cada planta
3. Verificar en la vista del bancal que los iconos no se superponen

### Ejemplo de Prueba
```
Bancal: Bancal 1
Fecha: Hoy
Plantas:
  - Tomates (8 unidades, fila superior, espaciado 30cm, alineación derecha)
  - Coles (6 unidades, fila superior, espaciado 40cm, alineación izquierda)

Resultado esperado: 
- Los tomates aparecen en el lado derecho
- Las coles aparecen en el lado izquierdo
- No hay superposición de iconos
```

---

## Despliegue en Servidor

### Pasos para Aplicar en Producción
1. **Respaldar base de datos:**
   ```bash
   mysqldump -u plansowgrow_user -p plansowgrow > backup_before_alignment.sql
   ```

2. **Actualizar código del servidor:**
   ```bash
   cd /home/jmgalaminos/PlanSowGrow
   git pull origin main
   ```

3. **Ejecutar migración:**
   ```bash
   python3 run_migration.py migrations/004_add_visual_plantation.sql
   ```

4. **Reiniciar Apache:**
   ```bash
   sudo systemctl restart apache2
   ```

5. **Verificar cambios:**
   - Crear un cultivo de prueba
   - Verificar que el selector de alineación aparece
   - Comprobar visualización en vista del bancal

---

## Notas Adicionales

- El campo `alignment` tiene valor por defecto `'center'` para mantener compatibilidad con cultivos existentes
- Los cultivos anteriores a esta actualización mantendrán el comportamiento centrado original
- La migración también añade iconos automáticos a las plantas más comunes
- Los emojis utilizados son compatibles con UTF-8 (charset utf8mb4)

---

## Archivos Modificados

| Archivo | Descripción del Cambio |
|---------|------------------------|
| `models.py` | Campo `alignment` en `CulturePlant` |
| `migrations/004_add_visual_plantation.sql` | Columna `alignment` y actualizaciones de iconos |
| `services.py` | Parámetro `alignments` en `create_culture()` |
| `routes.py` | Procesamiento de `alignment` en create y edit |
| `templates/cultures/create.html` | Selector de alineación |
| `templates/cultures/edit.html` | Selector de alineación con valor actual |
| `templates/cultures/view.html` | Visualización de alineación |
| `templates/beds/view.html` | Pasar alignment al visualizador |
| `static/js/bancal-visualizer.js` | Lógica de posicionamiento con alineación |

---

## Autor
GitHub Copilot

## Fecha de Implementación
2024
