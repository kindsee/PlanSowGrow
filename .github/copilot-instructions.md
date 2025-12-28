# PlanSowGrow - Copilot Instructions

## Project Overview
PlanSowGrow is a web application for ecological vegetable garden planning and management. Inspired by PlanBuyCook, it helps manage raised beds (bancales), track crops over time, maintain historical records, and automatically generate care and treatment calendars.

## Architecture Principles
**Clean architecture with strict separation of concerns:**
- **Models** (`models.py`): SQLAlchemy models only - no business logic
- **Services** (`services.py`): ALL business logic lives here, never in routes
- **Routes** (`routes.py`): HTTP handlers only - delegate to services immediately
- **Historical integrity**: Never delete historical data, only close or archive

**File Structure:**
- `app.py` - Flask application initialization
- `config.py` - Configuration and environment variables
- `models.py` - SQLAlchemy models
- `services.py` - Business logic layer
- `routes.py` - HTTP route definitions
- `init_db.py` - Database initialization script

## Tech Stack
- **Language**: Python 3.11+
- **Backend**: Flask
- **ORM**: SQLAlchemy
- **Database**: MariaDB
- **Frontend**: HTML + Bootstrap + Jinja2 templates
- **Style**: Clear English names, docstrings on models and services, clarity over cleverness

## Domain Model

### Core Concepts
- **Raised Beds**: Fixed-size garden beds (4m x 1m) - the fundamental spatial unit
- **Plants**: Catalog with growth cycles and harvest periods
- **Cultures**: Active plantings in a bed over a specific period (supports multiple plants per bed)
- **Pests**: Catalog of pests that affect plants
- **Treatments**: Ecological treatments associated with specific pests
- **Care Actions**: Additional activities (pruning, pinching, tutoring, etc.)
- **Calendar Events**: Auto-generated from cultures, pests, treatments, and care actions
- **Historical Records**: Immutable crop history per bed

### Culture Properties
- Start type: `seed` | `seedling` | `transplant`
- Date ranges are core - cultures have start/end dates
- Multiple plants can coexist in one bed simultaneously

## Database Design Rules
1. Use explicit foreign keys with clear naming
2. Define SQLAlchemy relationships for navigation
3. Create many-to-many association tables where needed
4. Cultures must support multiple plants per bed
5. Calendar events must reference either a care action or treatment
6. All date/time fields should consider temporal tracking

## Routing Structure
Routes are organized by domain concept:
- `/beds` - Raised bed management
- `/plants` - Plant catalog
- `/cultures` - Active and historical crop management
- `/pests` - Pest catalog
- `/treatments` - Ecological treatment catalog
- `/care` - Care action management
- `/calendar` - Generated garden calendar view
- `/history` - Bed and crop history analysis

## Code Conventions

### Business Logic Rules
- **NEVER** put business logic in routes
- Services must be pure functions or service classes
- Routes only: parse request → call service → return response
- Complex queries and data manipulation belong in services

### Naming Conventions
- Use clear, explicit English names
- Models: singular nouns (e.g., `Plant`, `Culture`, `RaisedBed`)
- Services: verb-based functions (e.g., `create_culture()`, `get_bed_history()`)
- Routes: RESTful patterns where applicable

### Documentation
- Add docstrings to all models explaining their purpose
- Add docstrings to service functions explaining parameters and return values
- Comment complex business logic, not obvious code

## Development Workflow
**Incremental implementation order:**
1. SQLAlchemy models
2. Database initialization
3. Core services
4. Routes and views
5. Calendar automation
6. Historical analysis

**Work incrementally** - wait for confirmation before moving to the next phase.

## Important Notes
- **Dates are core**: Many operations revolve around planting/harvest periods
- **Historical integrity**: Data represents real-world garden activity - preserve it
- **Calendar automation**: Events should be generated, not manually created
- **Multi-tenancy consideration**: Design may need to support multiple gardens/users later
