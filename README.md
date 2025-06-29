# AT Bus Load

A Python project for fetching and processing Auckland Transport (AT) bus data from their GTFS API.

## Features

- **API Integration**: Fetches bus stop and trip data from Auckland Transport's GTFS API
- **Data Validation**: Uses Pydantic models to validate API response data types and formats
- **Data Processing**: Converts validated data to Polars DataFrames for efficient processing
- **Cloud Storage**: Uploads processed data to Google Cloud Storage
- **BigQuery Integration**: Moves data from GCS to BigQuery for analysis
- **Type Safety**: Comprehensive type hints and validation throughout the pipeline

## Data Validation

The project includes Pydantic models to validate API responses before processing:

- **Stop Data**: Validates stop attributes, coordinates, and accessibility information
- **Trip Data**: Validates trip schedules, routes, and timing information
- **Format Validation**: Ensures correct time formats (HH:MM:SS), date formats (YYYY-MM-DD), and coordinate ranges
- **Value Validation**: Checks for valid direction IDs, location types, and sequence numbers

See [Pydantic Validation Documentation](docs/pydantic_validation.md) for detailed information.

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd at-bus-load

# Install dependencies
uv sync
```

## Usage

### Fetch and Process Bus Data

```bash
# Fetch data for today
python -m at_bus_load.get_at_api_data

# Fetch data for a specific date
python -m at_bus_load.get_at_api_data --date 2024-01-15
```

### Move Data to BigQuery

```bash
python -m at_bus_load.move_gcs_data_to_bq
```

### Check GCS Connection

```bash
python -m at_bus_load.check_gcs
```

## Environment Variables

Set the following environment variables:

```bash
AT_API_KEY=your_auckland_transport_api_key
GOOGLE_APPLICATION_CREDENTIALS=path_to_your_service_account_key.json
```

## Testing

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_models.py -v

# Run with coverage
python -m pytest --cov=src/at_bus_load
```

## Examples

Run the validation example to see Pydantic in action:

```bash
python examples/validation_example.py
```

## Project Structure

```
at-bus-load/
├── src/at_bus_load/
│   ├── models.py              # Pydantic validation models
│   ├── get_at_api_data.py     # API data fetching and validation
│   ├── move_gcs_data_to_bq.py # BigQuery data movement
│   └── gcp.py                 # Google Cloud utilities
├── tests/
│   └── test_models.py         # Pydantic model tests
├── examples/
│   └── validation_example.py  # Validation demonstration
└── docs/
    └── pydantic_validation.md # Validation documentation
```

## Dependencies

- **pydantic**: Data validation and settings management
- **polars**: Fast DataFrame library for data processing
- **requests**: HTTP library for API calls
- **google-cloud-storage**: Google Cloud Storage integration
- **google-cloud-bigquery**: BigQuery integration
- **typer**: Command-line interface
- **loguru**: Logging
- **pytest**: Testing framework