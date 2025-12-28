# PlanSowGrow

A garden planning and tracking application built with clean architecture principles.

## Overview

PlanSowGrow is a web application designed to help gardeners plan, organize, and track their gardens. It's built with a focus on clean architecture, separation of concerns, and maintainable code.

## Architecture

The application follows clean architecture principles with clear separation between layers:

### Technology Stack

- **Backend**: Python 3 + Flask
- **ORM**: SQLAlchemy
- **Database**: MariaDB (SQLite for testing)
- **Frontend**: HTML + Bootstrap 5 + Jinja2
- **Testing**: pytest

### Project Structure

```
PlanSowGrow/
├── app/
│   ├── models/          # Database models (entities)
│   │   ├── base.py      # Base model with common functionality
│   │   ├── garden.py    # Garden entity
│   │   ├── bed.py       # Bed entity
│   │   └── season.py    # Season entity
│   ├── services/        # Business logic layer
│   │   ├── base.py      # Base service class
│   │   ├── garden_service.py
│   │   ├── bed_service.py
│   │   └── season_service.py
│   ├── routes/          # HTTP request handlers
│   │   ├── main_routes.py
│   │   ├── garden_routes.py
│   │   └── season_routes.py
│   ├── templates/       # Jinja2 HTML templates
│   ├── static/          # CSS, JS, images
│   └── utils/           # Utility functions
├── config/              # Configuration files
├── tests/               # Test suite
│   ├── unit/           # Unit tests
│   └── integration/    # Integration tests
├── migrations/          # Database migrations
├── requirements.txt     # Python dependencies
└── run.py              # Application entry point
```

## Design Principles

### 1. Clean Architecture

The application is organized into distinct layers with clear responsibilities:

- **Models Layer**: Defines database entities and relationships
- **Services Layer**: Contains all business logic and validation
- **Routes Layer**: Handles HTTP requests and responses

### 2. Business Logic in Services

**All business logic lives in services, never in routes.** Routes are kept thin and only handle HTTP concerns. This ensures:

- Business logic can be tested independently of HTTP
- Logic can be reused across different interfaces (web, API, CLI)
- Code is more maintainable and easier to understand

### 3. Explicit and Documented Models

Models are explicit, readable, and well-documented:

- Clear field definitions with docstrings
- Explicit relationships
- Type hints where appropriate
- Built-in methods for common operations

### 4. Historical Data Preservation

The system uses soft delete patterns to ensure **historical data is never permanently removed**:

- `SoftDeleteMixin` provides soft delete functionality
- Records are marked as deleted rather than removed
- Queries can include or exclude deleted records
- Data can be restored if needed

### 5. Date and Period Management

Dates and periods are core concepts:

- `PeriodMixin` provides consistent handling of time-based entities
- Built-in support for start/end dates
- Active period queries
- Period closing and reopening

## Getting Started

### Prerequisites

- Python 3.8 or higher
- MariaDB 10.5 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/kindsee/PlanSowGrow.git
cd PlanSowGrow
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. Create the database:
```bash
# Log into MariaDB
mysql -u root -p

# Create database
CREATE DATABASE plansowgrow_dev;
exit;
```

6. Run the application:
```bash
python run.py
```

The application will be available at `http://localhost:5000`

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/unit/test_garden_service.py

# Run with verbose output
pytest -v
```

## Features

### Gardens

- Create and manage multiple gardens
- Track garden location and size
- Soft delete for archiving
- View garden details and associated beds

### Beds

- Organize gardens into beds
- Track bed dimensions
- Calculate bed areas
- Associate plantings with beds

### Seasons

- Define growing seasons with start/end dates
- Track active and closed seasons
- Open-ended seasons for ongoing periods
- Close and reopen seasons as needed

## API Endpoints

The application provides both HTML views and JSON API endpoints:

### Gardens

- `GET /gardens/` - List all gardens
- `GET /gardens/<id>` - View garden details
- `POST /gardens/new` - Create new garden
- `POST /gardens/<id>/edit` - Update garden
- `POST /gardens/<id>/archive` - Archive garden
- `GET /gardens/api/gardens` - JSON list of gardens
- `GET /gardens/api/gardens/<id>` - JSON garden details

### Seasons

- `GET /seasons/` - List all seasons
- `GET /seasons/<id>` - View season details
- `POST /seasons/new` - Create new season
- `POST /seasons/<id>/edit` - Update season
- `POST /seasons/<id>/close` - Close season
- `POST /seasons/<id>/reopen` - Reopen season
- `GET /seasons/api/seasons` - JSON list of seasons
- `GET /seasons/api/seasons/active` - JSON active seasons

## Development

### Code Style

- Follow PEP 8 for Python code
- Use docstrings for all classes and functions
- Keep functions small and focused
- Write tests for all business logic

### Adding New Features

1. Define models in `app/models/`
2. Implement business logic in `app/services/`
3. Create routes in `app/routes/`
4. Add templates in `app/templates/`
5. Write tests in `tests/`

### Database Migrations

For production use, set up Alembic for database migrations:

```bash
# Initialize Alembic
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

## Configuration

The application supports multiple environments:

- **Development**: Debug enabled, SQLite or MariaDB
- **Testing**: In-memory SQLite, CSRF disabled
- **Production**: Debug disabled, MariaDB required

Configure through environment variables in `.env`:

```
FLASK_ENV=development
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_NAME=plansowgrow_dev
DATABASE_USER=root
DATABASE_PASSWORD=your_password
SECRET_KEY=your-secret-key
```

## Contributing

Contributions are welcome! Please:

1. Follow the existing code style and architecture
2. Write tests for new features
3. Keep business logic in services
4. Document your code
5. Create focused pull requests

## License

This project is open source and available under the MIT License.

## Contact

For questions or support, please open an issue on GitHub.