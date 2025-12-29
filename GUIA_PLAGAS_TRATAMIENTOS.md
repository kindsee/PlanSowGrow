# Guía: Cómo Relacionar Plagas y Tratamientos en PlanSowGrow

## 📋 Pasos para Configurar Tratamientos con Plagas

### 1. Crear/Editar un Tratamiento

1. Ve a **Tratamientos** → **Nuevo Tratamiento** (o edita uno existente)
2. Rellena la información básica:
   - Nombre del tratamiento
   - Descripción
   - Método de aplicación
   - Frecuencia sugerida en días

3. **Guarda el tratamiento** (ahora NO requiere asociar una plaga inicialmente)

### 2. Asociar Plagas al Tratamiento

1. Después de crear el tratamiento, serás redirigido a la página de **Editar Tratamiento**
2. Busca la sección **"Plagas que Combate"** (debajo del formulario principal)
3. Haz clic en el botón **"Añadir Plaga"**
4. En el modal que aparece:
   - Selecciona la **plaga** de la lista
   - Indica la **efectividad** (Alta, Media, Baja)
   - Añade **notas** opcionales sobre esta asociación
5. Haz clic en **"Añadir"**

### 3. Asociar Múltiples Plagas

- Puedes repetir el proceso anterior para asociar el tratamiento con **múltiples plagas**
- Cada asociación tendrá su propio nivel de efectividad
- Por ejemplo: "Purín de ortiga" puede ser efectivo contra "Pulgón" (Alta) y "Mosca blanca" (Media)

### 4. Ver Tratamientos desde una Plaga

1. Ve a **Plagas** → Selecciona una plaga para editar
2. Verás la sección **"Tratamientos Disponibles"**
3. Se mostrará una tabla con:
   - Todos los tratamientos efectivos contra esa plaga
   - Nivel de efectividad de cada uno
   - Frecuencia sugerida
   - Notas

### 5. Planificar Tratamientos para Cultivos (Sugerencias Inteligentes)

Cuando añadas un tratamiento a un cultivo:

1. Ve a un **Cultivo** activo
2. En la sección de **"Plagas Potenciales"** verás qué plagas pueden afectar ese cultivo según sus plantas
3. Haz clic en **"Añadir Tratamiento"**
4. Verás dos secciones:
   - **Tratamientos Recomendados** ⭐ (efectivos contra las plagas potenciales)
   - **Otros Tratamientos** (resto de tratamientos disponibles)
5. Los tratamientos recomendados muestran contra qué plagas son efectivos con badges de colores

## 🎯 Flujo Completo de Ejemplo

```
1. Plantas → Haba Aguadulce
   └─ Asociar plaga: "Pulgón negro"
   └─ Asociar plaga: "Mildiu"

2. Tratamientos → "Purín de ortiga"
   └─ Añadir plaga: "Pulgón negro" (Efectividad: Alta)
   └─ Añadir plaga: "Mosca blanca" (Efectividad: Media)

3. Tratamientos → "Jabón potásico"
   └─ Añadir plaga: "Pulgón negro" (Efectividad: Alta)
   └─ Añadir plaga: "Cochinilla" (Efectividad: Alta)

4. Cultivos → Cultivo de Habas en Bancal 1
   └─ Ver "Plagas Potenciales": Pulgón negro, Mildiu
   └─ Añadir Tratamiento
      └─ Tratamientos Recomendados:
          ⭐ Purín de ortiga (contra Pulgón negro - Alta)
          ⭐ Jabón potásico (contra Pulgón negro - Alta)
```

## ✨ Beneficios

- **Flexibilidad**: Un tratamiento puede combatir múltiples plagas
- **Inteligencia**: El sistema sugiere tratamientos relevantes automáticamente
- **Trazabilidad**: Nivel de efectividad documentado para cada combinación
- **Prevención**: Conoce las plagas potenciales antes de que aparezcan

## 🔗 Enlaces Rápidos en la Aplicación

- Lista de Tratamientos: http://localhost:5001/treatments/list
- Lista de Plagas: http://localhost:5001/pests/list
- Lista de Cultivos: http://localhost:5001/cultures/list

---

**Nota**: Los cambios se han guardado automáticamente en la base de datos. ¡Ya puedes empezar a relacionar plagas y tratamientos!
