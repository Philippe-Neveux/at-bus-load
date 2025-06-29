# Pydantic Data Validation

This document describes the Pydantic integration for validating Auckland Transport API responses before processing them into Polars DataFrames.

## Overview

The project now uses Pydantic models to validate API response data types and formats before converting them to Polars DataFrames. This ensures data integrity and catches errors early in the data processing pipeline.

## Models

### Stop Models

#### `StopAttributes`
Validates individual stop attributes:
- `stop_id`: String identifier
- `stop_code`: Public-facing stop code
- `stop_name`: Stop name
- `stop_lat`: Latitude (-90 to 90)
- `stop_lon`: Longitude (-180 to 180)
- `location_type`: Location type (0-4)
- `wheelchair_boarding`: Accessibility (0-2)

#### `StopData`
Validates individual stop data objects:
- `type`: Must be "stops"
- `id`: Unique identifier
- `attributes`: StopAttributes object

#### `StopResponse`
Validates complete stop API responses:
- `data`: List of StopData objects

### Trip Models

#### `TripAttributes`
Validates individual trip attributes:
- `arrival_time`: Time in HH:MM:SS format
- `departure_time`: Time in HH:MM:SS format
- `direction_id`: Direction (0 or 1)
- `drop_off_type`: Drop-off type (0-3)
- `pickup_type`: Pickup type (0-3)
- `route_id`: Route identifier
- `service_date`: Date in YYYY-MM-DD format
- `shape_id`: Shape identifier
- `stop_headsign`: Stop headsign
- `stop_id`: Stop identifier
- `stop_sequence`: Positive integer
- `trip_headsign`: Trip headsign
- `trip_id`: Trip identifier
- `trip_start_time`: Time in HH:MM:SS format

#### `TripData`
Validates individual trip data objects:
- `type`: Must be "stoptrips"
- `id`: Unique identifier
- `attributes`: TripAttributes object

#### `TripResponse`
Validates complete trip API responses:
- `data`: List of TripData objects

## Usage

### In API Functions

The `get_at_gtfs_data_from_at_mobile_api` function now automatically validates responses:

```python
# For stops data
if data_name == "stops":
    validated_response = StopResponse(**data)
    
# For trips data
elif "stoptrips" in data_name:
    validated_response = TripResponse(**data)
```

### Manual Validation

You can also validate data manually:

```python
from at_bus_load.models import StopResponse, TripResponse
from pydantic import ValidationError

try:
    stop_response = StopResponse(**api_data)
    # Data is valid, proceed with processing
except ValidationError as e:
    # Handle validation errors
    logger.error(f"Data validation failed: {e}")
```

## Validation Features

### Type Checking
- Ensures all fields have the correct data types
- Converts compatible types where possible

### Format Validation
- Time formats (HH:MM:SS)
- Date formats (YYYY-MM-DD)
- Coordinate ranges (latitude: -90 to 90, longitude: -180 to 180)

### Value Validation
- Direction IDs must be 0 or 1
- Location types must be 0-4
- Stop sequences must be positive
- Service types must be 0-3

### Structure Validation
- Ensures required fields are present
- Validates nested object structures
- Checks response type consistency

## Error Handling

When validation fails, Pydantic provides detailed error messages:

```python
try:
    response = StopResponse(**invalid_data)
except ValidationError as e:
    print(e)
    # Output: 1 validation error for StopResponse
    # data -> 0 -> attributes -> stop_lat
    #   Latitude must be between -90 and 90 (type=value_error)
```

## Testing

Comprehensive tests are available in `tests/test_models.py`:

```bash
python -m pytest tests/test_models.py -v
```

The tests cover:
- Valid data scenarios
- Invalid data types
- Format violations
- Value range violations
- Structure errors

## Example

Run the validation example:

```bash
python examples/validation_example.py
```

This demonstrates:
- Valid data validation
- Invalid data detection
- Error message clarity
- Integration with the existing codebase

## Benefits

1. **Early Error Detection**: Catches data issues before processing
2. **Type Safety**: Ensures correct data types throughout the pipeline
3. **Documentation**: Models serve as living documentation of API structure
4. **Debugging**: Clear error messages help identify data issues
5. **Maintainability**: Centralized validation logic
6. **Reliability**: Prevents downstream errors from invalid data

## Integration with Existing Code

The validation is seamlessly integrated into the existing `get_at_gtfs_data_from_at_mobile_api` function:

1. API response is received
2. Pydantic models validate the data structure and types
3. If validation passes, data is converted to Polars DataFrame
4. If validation fails, detailed error is logged and exception is raised

This ensures that only valid data reaches the Polars processing stage, improving the reliability of the entire data pipeline. 