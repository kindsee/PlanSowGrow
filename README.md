# PlanSowGrow 🌱

Sistema de gestión de huertos ecológicos para planificar, sembrar y cultivar de forma organizada.

## Características

- 📊 Gestión de bancales (raised beds) de 4m x 1m
- 🌿 Catálogo de plantas con ciclos de crecimiento
- 📅 Registro de cultivos activos e históricos
- 🐛 Gestión de plagas y tratamientos ecológicos
- ✂️ Acciones de cuidado (poda, entutorado, etc.)
- 📆 Calendario automático de tareas de jardín

## Requisitos

- Python 3.11+
- MariaDB 10.5+
- pip

## Instalación

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd PlanSowGrow
```

### 2. Crear entorno virtual

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos

Crear la base de datos en MariaDB:

```sql
CREATE DATABASE plansowgrow CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Configurar variables de entorno

Copiar el archivo de ejemplo y ajustar las credenciales:

```bash
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

Editar `.env` con tus credenciales de base de datos:

```ini
DB_HOST=localhost
DB_PORT=3306
DB_NAME=plansowgrow
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña

FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=genera_una_clave_secreta_aqui
```

### 6. Inicializar la base de datos

```bash
# Solo crear tablas
python init_db.py

# O crear tablas y cargar datos de ejemplo
python init_db.py --drop --sample
```

## Ejecución

### Desarrollo

```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

### Producción

Se recomienda usar un servidor WSGI como Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

## Estructura del Proyecto

```
PlanSowGrow/
├── app.py              # Inicialización de Flask
├── config.py           # Configuración y variables de entorno
├── models.py           # Modelos SQLAlchemy
├── services.py         # Lógica de negocio
├── routes.py           # Rutas HTTP
├── init_db.py          # Script de inicialización de BD
├── requirements.txt    # Dependencias Python
├── .env.example        # Plantilla de variables de entorno
└── templates/          # Plantillas Jinja2
    ├── base.html
    ├── beds/
    ├── plants/
    ├── cultures/
    ├── pests/
    ├── treatments/
    ├── care/
    └── calendar/
```

## Arquitectura

### Principios

- **Separación de responsabilidades**: Modelos, servicios y rutas están claramente separados
- **Lógica de negocio en servicios**: Las rutas solo manejan HTTP, toda la lógica está en `services.py`
- **Integridad histórica**: Los datos nunca se eliminan, solo se cierran o archivan
- **Generación automática**: El calendario se genera automáticamente basándose en cultivos y cuidados

### Flujo de Datos

```
HTTP Request → Route (routes.py) → Service (services.py) → Model (models.py) → Database
```

### Módulos de Rutas

- `/beds` - Gestión de bancales
- `/plants` - Catálogo de plantas
- `/cultures` - Cultivos activos e históricos
- `/pests` - Catálogo de plagas
- `/treatments` - Tratamientos ecológicos
- `/care` - Acciones de cuidado
- `/calendar` - Calendario de tareas

## Uso

### 1. Crear Bancales

Registra tus bancales con nombre, ubicación y descripción.

### 2. Agregar Plantas al Catálogo

Define las plantas que cultivarás con sus periodos de crecimiento y cosecha.

### 3. Iniciar Cultivos

Asocia plantas a bancales con fechas de inicio y tipo (semilla, plántula, trasplante).

### 4. Revisar Calendario

El sistema genera automáticamente tareas de cuidado basándose en los cultivos activos.

### 5. Gestionar Plagas y Tratamientos

Registra plagas comunes y sus tratamientos ecológicos asociados.

## Desarrollo

### Agregar Nuevas Características

1. Actualizar `models.py` si se necesitan nuevas tablas
2. Agregar lógica de negocio en `services.py`
3. Crear rutas en `routes.py`
4. Diseñar vistas en `templates/`

### Testing

```bash
# Por implementar
pytest
```

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

[Por definir]

## Créditos

Inspirado en PlanBuyCook para la gestión sistemática de actividades.
