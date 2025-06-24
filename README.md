# AT Bus Load

A Python project for extracting, processing, and loading Auckland Transport (AT) bus data from their GTFS API into Google Cloud Storage and BigQuery for analysis.

## Overview

This project provides a data pipeline for collecting bus transportation data from Auckland Transport's GTFS API, processing it, and storing it in Google Cloud Platform services for further analysis and reporting.

## Features

- **API Data Extraction**: Fetches bus stops and trips data from Auckland Transport's GTFS API
- **Data Processing**: Uses Polars for efficient data manipulation and processing
- **Cloud Storage**: Uploads processed data to Google Cloud Storage as Parquet files
- **BigQuery Integration**: Loads data from GCS into BigQuery for analytics
- **Docker Support**: Containerized deployment with Docker in order to be run in Ariflow with a Docker operator
- **Data Validation**: Includes utilities for checking GCS connectivity and data integrity

## Project Structure

```
at-bus-load/
├── src/at_bus_load/           # Main Python package
│   ├── get_at_api_data.py     # AT API data extraction
│   ├── move_gcs_data_to_bq.py # GCS to BigQuery data loading
│   ├── check_gcs.py           # GCS connectivity checker
│   ├── gcp.py                 # GCP connection utilities
│   └── entrypoints_params.py  # Command line argument parsing
├── notebooks/                 # Jupyter notebooks for data exploration
├── data/                      # Local data storage
├── Dockerfile                 # Docker container configuration
├── Makefile                   # Build and deployment commands
└── pyproject.toml            # Project dependencies and configuration
```

## Prerequisites

- Python 3.12
- Google Cloud Platform account with access to:
  - Google Cloud Storage
  - BigQuery
- Auckland Transport API key
- Docker (for containerized deployment)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd at-bus-load
```

2. Install dependencies using uv:
```bash
uv sync
```

3. Set up environment variables:
```bash
export AT_API_KEY="your_at_api_key"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"
```

## Usage

### Command Line Tools

The project provides several command-line tools for different operations:

#### 1. Extract AT API Data
```bash
uv run get_at_api_data --date 2024-01-15
```
Fetches bus stops and trips data for a specific date and uploads to GCS.

#### 2. Load Data to BigQuery
```bash
uv run move_gcs_data_to_bq --date 2024-01-15
```
Moves data from GCS to BigQuery tables.

#### 3. Check GCS Connectivity
```bash
uv run check_gcs
```
Verifies connectivity to Google Cloud Storage.

### Data Pipeline

The typical data pipeline workflow:

1. **Data Extraction**: Use `get_at_api_data` to fetch data from AT API
2. **Data Storage**: Data is automatically stored in GCS as Parquet files
3. **Data Loading**: Use `move_gcs_data_to_bq` to load data into BigQuery
4. **Analysis**: Use the provided Jupyter notebooks for data exploration

### Data Structure

#### Stops Data
- Location: `gs://pne-open-data/at-bus/{date}/stops.parquet`
- BigQuery Table: `at_bus_bronze.stops_{date}`

#### Trips Data
- Location: `gs://pne-open-data/at-bus/{date}/trips_{route_id}.parquet`
- BigQuery Table: `at_bus_bronze.trips_{route_id}_{date}`

## Development

### Code Quality

The project uses several tools for code quality:

```bash
# Run linting
make ruff_check

# Fix import sorting
make ruff_isort

# Run type checking
make mypy
```

### Docker Deployment

Build and deploy using Docker:

```bash
# Build Docker image
make build_docker_image

# Tag for GCP
make tag_docker_image_for_gcp

# Push to GCP Artifact Registry
make push_docker_image_to_gcp
```

## Configuration

### Environment Variables

- `AT_API_KEY`: Auckland Transport API key
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to GCP service account key

### GCP Configuration

- **Project ID**: `glossy-apex-462002-i3`
- **Region**: `australia-southeast1`
- **GCS Bucket**: `pne-open-data`
- **BigQuery Dataset**: `at_bus_bronze`

## Dependencies

Key dependencies include:
- `polars`: Fast DataFrame library for data processing
- `google-cloud-storage`: GCS client library
- `google-cloud-bigquery`: BigQuery client library
- `requests`: HTTP client for API calls
- `loguru`: Structured logging
- `plotly`: Data visualization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run code quality checks
5. Submit a pull request

## Support

For issues and questions, please create an issue in the repository.