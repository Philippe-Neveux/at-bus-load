"""
Common fixtures for pytest tests.
"""
import os
from unittest.mock import Mock, patch

import polars as pl
import pytest
from google.cloud import bigquery, storage


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    with patch.dict(os.environ, {
        'AT_API_KEY': 'test-api-key-12345',
        'GCP_TOKEN': 'test-gcp-token-12345'
    }):
        yield


@pytest.fixture
def sample_stops_data():
    """Sample stops data for testing."""
    return pl.DataFrame({
        'stop_id': ['8147', '8545', '7149', '8331', '7133'],
        'stop_code': ['8147', '8545', '7149', '8331', '7133'],
        'stop_name': ['Stop A', 'Stop B', 'Stop C', 'Stop D', 'Stop E'],
        'stop_lat': [-36.8485, -36.8486, -36.8487, -36.8488, -36.8489],
        'stop_lon': [174.7633, 174.7634, 174.7635, 174.7636, 174.7637]
    })


@pytest.fixture
def sample_trips_data():
    """Sample trips data for testing."""
    return pl.DataFrame({
        'trip_id': ['trip_001', 'trip_002', 'trip_003'],
        'route_id': ['route_001', 'route_002', 'route_003'],
        'service_id': ['service_001', 'service_002', 'service_003'],
        'shape_id': ['shape_001', 'shape_002', 'shape_003']
    })


@pytest.fixture
def mock_storage_client():
    """Mock Google Cloud Storage client."""
    mock_client = Mock(spec=storage.Client)
    mock_bucket = Mock()
    mock_blob = Mock()
    
    mock_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    mock_client.get_bucket.return_value = mock_bucket
    
    return mock_client


@pytest.fixture
def mock_bigquery_client():
    """Mock Google BigQuery client."""
    mock_client = Mock(spec=bigquery.Client)
    mock_dataset = Mock()
    mock_table = Mock()
    mock_job = Mock()
    
    mock_client.dataset.return_value = mock_dataset
    mock_dataset.table.return_value = mock_table
    mock_client.load_table_from_uri.return_value = mock_job
    
    return mock_client


@pytest.fixture
def mock_requests_response():
    """Mock requests response for API testing."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [
            {
                "stop_id": "8147",
                "stop_code": "8147",
                "stop_name": "Test Stop",
                "stop_lat": -36.8485,
                "stop_lon": 174.7633
            }
        ]
    }
    mock_response.url = "https://api.at.govt.nz/gtfs/v3/stops"
    return mock_response


@pytest.fixture
def mock_gcp_credentials():
    """Mock GCP credentials."""
    mock_creds = Mock()
    mock_creds.token = "test-token-12345"
    return mock_creds


@pytest.fixture
def mock_gcs_blobs():
    """Helper function to create mock GCS blobs with name attributes."""
    def _create_mock_blobs(blob_names):
        """Create mock blobs with the given names."""
        mock_blobs = []
        for blob_name in blob_names:
            mock_blob = Mock()
            mock_blob.name = blob_name
            mock_blobs.append(mock_blob)
        return mock_blobs
    
    return _create_mock_blobs 