# Architecture Documentation

## Clean Architecture Overview

PlanSowGrow follows clean architecture principles with clear separation of concerns across three main layers:

```
┌─────────────────────────────────────────────────┐
│                   Routes Layer                   │
│         (HTTP Request/Response Handling)         │
│  - Thin controllers                              │
│  - Extract request data                          │
│  - Call service methods                          │
│  - Return responses                              │
└─────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────┐
│                  Services Layer                  │
│              (Business Logic)                    │
│  - Validation                                    │
│  - Business rules                                │
│  - Transaction management                        │
│  - Orchestration                                 │
└─────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────┐
│                   Models Layer                   │
│            (Database Entities)                   │
│  - Entity definitions                            │
│  - Relationships                                 │
│  - Basic CRUD operations                         │
│  - Domain logic (properties)                     │
└─────────────────────────────────────────────────┘
```

## Principles

### 1. Business Logic in Services

**Rule**: ALL business logic MUST live in services, NEVER in routes.

**Why**:
- Business logic can be tested independently of HTTP
- Logic can be reused across different interfaces (web, API, CLI)
- Easier to maintain and understand
- Follows Single Responsibility Principle

**Example**:

❌ **Wrong** - Business logic in routes:
```python
@app.route('/gardens/new', methods=['POST'])
def create_garden():
    name = request.form.get('name')
    
    # Business logic in route - BAD!
    if not name or not name.strip():
        flash('Name is required', 'error')
        return redirect(url_for('gardens.new'))
    
    if len(name) > 100:
        flash('Name too long', 'error')
        return redirect(url_for('gardens.new'))
    
    garden = Garden(name=name.strip())
    garden.save()
    return redirect(url_for('gardens.list'))
```

✅ **Correct** - Business logic in service:
```python
# In service
class GardenService:
    @classmethod
    def create_garden(cls, name, **kwargs):
        # Business logic in service - GOOD!
        if not name or not name.strip():
            raise ValueError("Name is required")
        
        if len(name) > 100:
            raise ValueError("Name too long")
        
        return cls.create(name=name.strip(), **kwargs)

# In route
@app.route('/gardens/new', methods=['POST'])
def create_garden():
    try:
        # Route only handles HTTP concerns
        garden = GardenService.create_garden(
            name=request.form.get('name')
        )
        flash('Garden created', 'success')
        return redirect(url_for('gardens.view', id=garden.id))
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('gardens.new'))
```

### 2. Explicit and Documented Models

Models should be clear and self-documenting:

```python
class Garden(BaseModel, SoftDeleteMixin):
    """
    Represents a garden or growing space.
    
    Gardens can be soft-deleted to preserve historical data.
    """
    
    name = db.Column(
        db.String(100),
        nullable=False,
        doc="Name of the garden"
    )
    
    # Explicit relationship
    beds = db.relationship(
        'Bed',
        backref='garden',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
```

### 3. Historical Data Preservation

Data is NEVER permanently deleted:

- Use `SoftDeleteMixin` for entities that should be archived
- `soft_delete()` marks records as deleted
- `restore()` brings back deleted records
- Queries filter deleted records by default

```python
# Soft delete a garden
garden.soft_delete()  # Sets deleted_at timestamp

# Get only active gardens
active = Garden.get_active()

# Restore if needed
garden.restore()  # Clears deleted_at
```

### 4. Date and Period Management

Core concept with built-in support:

```python
class Season(BaseModel, PeriodMixin):
    """Season with start/end dates."""
    pass

# Use built-in properties
season.is_active  # True if currently active
season.is_closed  # True if end date passed
season.duration_days  # Total days in period

# Use built-in methods
season.close()  # Set end date
Season.get_active_periods()  # Query active periods
```

## Layer Responsibilities

### Routes Layer

**Responsibilities**:
- Receive HTTP requests
- Extract and parse request data
- Call appropriate service methods
- Handle service exceptions
- Return HTTP responses (JSON, HTML, redirects)
- Set flash messages
- HTTP-specific concerns only

**Must NOT**:
- Contain business logic
- Directly modify models
- Perform validation (beyond basic type checking)

### Services Layer

**Responsibilities**:
- Implement business logic
- Validate data
- Enforce business rules
- Manage transactions
- Orchestrate operations across models
- Log business events
- Raise meaningful exceptions

**Must NOT**:
- Know about HTTP (no request/response objects)
- Render templates
- Handle HTTP status codes

### Models Layer

**Responsibilities**:
- Define database schema
- Define relationships
- Provide basic CRUD operations
- Implement domain properties and methods
- Database-agnostic business rules

**Must NOT**:
- Contain HTTP-specific code
- Implement complex business logic
- Perform validation beyond database constraints

## Common Patterns

### Creating Entities

```python
# Service method
@classmethod
def create_garden(cls, name, description=None, **kwargs):
    # Validation
    if not name or not name.strip():
        raise ValueError("Name is required")
    
    # Business logic
    name = name.strip()
    
    # Delegate to base service
    return cls.create(name=name, description=description, **kwargs)
```

### Updating Entities

```python
# Service method
@classmethod
def update_garden(cls, garden_id, **kwargs):
    # Validation
    if 'name' in kwargs:
        if not kwargs['name']:
            raise ValueError("Name is required")
        kwargs['name'] = kwargs['name'].strip()
    
    # Delegate to base service
    return cls.update(garden_id, **kwargs)
```

### Querying

```python
# Service method - encapsulates query logic
@classmethod
def get_active_gardens(cls):
    return cls.model.get_active().all()

@classmethod
def get_garden_with_beds(cls, garden_id):
    garden = cls.get_by_id(garden_id)
    if not garden:
        return None, None
    beds = garden.beds.filter_by(deleted_at=None).all()
    return garden, beds
```

### Error Handling

```python
# In route
try:
    garden = GardenService.create_garden(**data)
    flash('Success', 'success')
    return redirect(url_for('gardens.view', id=garden.id))
except ValueError as e:
    # Business validation error
    flash(str(e), 'error')
    return render_template('form.html')
except Exception as e:
    # Unexpected error
    current_app.logger.error(f'Error: {e}')
    flash('An error occurred', 'error')
    return render_template('form.html')
```

## Testing Strategy

### Unit Tests

Test services in isolation:

```python
def test_create_garden_success(db):
    garden = GardenService.create_garden(name="Test")
    assert garden.name == "Test"

def test_create_garden_empty_name_fails(db):
    with pytest.raises(ValueError):
        GardenService.create_garden(name="")
```

### Integration Tests

Test routes with the full stack:

```python
def test_create_garden_form_post(client, db):
    response = client.post('/gardens/new', data={
        'name': 'Test Garden'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'created successfully' in response.data
```

## Best Practices

1. **Keep routes thin** - Extract, call service, return response
2. **Services contain business logic** - Always
3. **Validate in services** - Not in routes or models
4. **Use soft delete** - Preserve historical data
5. **Document everything** - Models, services, complex logic
6. **Test business logic** - Comprehensive service tests
7. **Handle errors gracefully** - Clear error messages
8. **Log important events** - Especially in services
9. **Use transactions** - Ensure data consistency
10. **Keep it simple** - Don't over-engineer

## Example: Adding a New Feature

To add a "Plant" entity:

1. **Define model** (`app/models/plant.py`):
```python
class Plant(BaseModel, SoftDeleteMixin):
    """Represents a plant variety."""
    name = db.Column(db.String(100), nullable=False)
    # ...
```

2. **Create service** (`app/services/plant_service.py`):
```python
class PlantService(BaseService):
    model = Plant
    
    @classmethod
    def create_plant(cls, name, **kwargs):
        # Business logic and validation
        if not name:
            raise ValueError("Name required")
        return cls.create(name=name, **kwargs)
```

3. **Add routes** (`app/routes/plant_routes.py`):
```python
@plant_bp.route('/new', methods=['POST'])
def create_plant():
    try:
        plant = PlantService.create_plant(**request.form)
        flash('Plant created', 'success')
        return redirect(url_for('plants.view', id=plant.id))
    except ValueError as e:
        flash(str(e), 'error')
        return render_template('plants/form.html')
```

4. **Write tests** (`tests/unit/test_plant_service.py`):
```python
def test_create_plant_success(db):
    plant = PlantService.create_plant(name="Tomato")
    assert plant.name == "Tomato"
```

This maintains clean architecture throughout the feature!
