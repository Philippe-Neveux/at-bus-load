"""
Unit tests for get_at_api_data module.
"""
import os
from unittest.mock import Mock, patch

import polars as pl
import pytest
import requests
from google.cloud import storage

from at_bus_load.get_at_api_data import (
    filter_stops_data,
    get_at_api_key,
    get_at_gtfs_data_from_at_mobile_api,
    get_stops_data,
    send_stop_data_to_gcs,
    send_trips_data_to_gcs
)


class TestGetAtApiKey:
    """Test cases for get_at_api_key function."""

    def test_get_at_api_key_success(self, mock_env_vars):
        """Test successful retrieval of API key from environment."""
        api_key = get_at_api_key()
        assert api_key == "test-api-key-12345"

    def test_get_at_api_key_missing(self):
        """Test error handling when API key is missing from environment."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Auckland Transport API key not found."):
                get_at_api_key()


class TestGetAtGtfsDataFromAtMobileApi:
    """Test cases for get_at_gtfs_data_from_at_mobile_api function."""

    @patch('at_bus_load.get_at_api_data.requests.get')
    def test_get_at_gtfs_data_success(self, mock_get, mock_requests_response):
        """Test successful API data retrieval."""
        mock_get.return_value = mock_requests_response
        
        result = get_at_gtfs_data_from_at_mobile_api("stops")
        
        assert isinstance(result, pl.DataFrame)
        assert len(result) == 1

    @patch('at_bus_load.get_at_api_data.requests.get')
    def test_get_at_gtfs_data_with_params_and_headers(self, mock_get, mock_requests_response):
        """Test API call with custom parameters and headers."""
        mock_get.return_value = mock_requests_response
        
        params = {"filter[date]": "2024-01-01"}
        headers = {"Authorization": "Bearer token"}
        
        result = get_at_gtfs_data_from_at_mobile_api("stops", params=params, headers=headers)
        
        mock_get.assert_called_once_with(
            "https://api.at.govt.nz/gtfs/v3/stops",
            params=params,
            headers=headers
        )
        assert isinstance(result, pl.DataFrame)

    @patch('at_bus_load.get_at_api_data.requests.get')
    def test_get_at_gtfs_data_api_error(self, mock_get):
        """Test handling of API errors."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response
        
        # Should raise an exception for non-200 status codes
        with pytest.raises(Exception, match="Request failed with status code 404: Not Found"):
            get_at_gtfs_data_from_at_mobile_api("stops")

    @patch('at_bus_load.get_at_api_data.requests.get')
    def test_get_at_gtfs_data_with_nested_columns(self, mock_get):
        """Test handling of nested JSON structures."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "stop_id": "8147",
                    "location": {
                        "lat": -36.8485,
                        "lon": 174.7633
                    }
                }
            ]
        }
        mock_response.url = "https://api.at.govt.nz/gtfs/v3/stops"
        mock_get.return_value = mock_response
        
        result = get_at_gtfs_data_from_at_mobile_api("stops")
        
        assert isinstance(result, pl.DataFrame)
        # Should unnest the nested location column
        assert "lat" in result.columns
        assert "lon" in result.columns

    @patch('at_bus_load.get_at_api_data.requests.get')
    def test_get_at_gtfs_data_api_error_500(self, mock_get):
        """Test handling of 500 API errors."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response
        
        # Should raise an exception for 500 status code
        with pytest.raises(Exception, match="Request failed with status code 500: Internal Server Error"):
            get_at_gtfs_data_from_at_mobile_api("stops")

    @patch('at_bus_load.get_at_api_data.requests.get')
    def test_get_at_gtfs_data_api_error_403(self, mock_get):
        """Test handling of 403 API errors."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        mock_get.return_value = mock_response
        
        # Should raise an exception for 403 status code
        with pytest.raises(Exception, match="Request failed with status code 403: Forbidden"):
            get_at_gtfs_data_from_at_mobile_api("stops")


class TestGetStopsData:
    """Test cases for get_stops_data function."""

    @patch('at_bus_load.get_at_api_data.get_at_gtfs_data_from_at_mobile_api')
    @patch('at_bus_load.get_at_api_data.get_at_api_key')
    def test_get_stops_data_success(self, mock_get_api_key, mock_get_gtfs_data, sample_stops_data):
        """Test successful stops data retrieval."""
        mock_get_api_key.return_value = "test-api-key"
        mock_get_gtfs_data.return_value = sample_stops_data
        
        result = get_stops_data("2024-01-01")
        
        assert isinstance(result, pl.DataFrame)
        assert "api_date_ingestion" in result.columns
        
        # Verify the function was called with correct parameters
        mock_get_gtfs_data.assert_called_once_with(
            data_name="stops",
            params={"filter[date]": "2024-01-01"},
            headers={
                "Cache-Control": "no-cache",
                "Ocp-Apim-Subscription-Key": "test-api-key"
            }
        )

    @patch('at_bus_load.get_at_api_data.get_at_gtfs_data_from_at_mobile_api')
    @patch('at_bus_load.get_at_api_data.get_at_api_key')
    def test_get_stops_data_exception_handling(self, mock_get_api_key, mock_get_gtfs_data):
        """Test exception handling in get_stops_data."""
        mock_get_api_key.return_value = "test-api-key"
        mock_get_gtfs_data.side_effect = Exception("API Error")
        
        with pytest.raises(Exception, match="API Error"):
            get_stops_data("2024-01-01")


class TestFilterStopsData:
    """Test cases for filter_stops_data function."""

    def test_filter_stops_data_success(self, sample_stops_data):
        """Test successful filtering of stops data."""
        result = filter_stops_data(sample_stops_data)
        
        assert isinstance(result, pl.DataFrame)
        assert len(result) == 5  # All stops should be included as they're in the predefined list
        assert all(stop_code in ["8147", "8545", "7149", "8331", "7133"] for stop_code in result["stop_code"])

    def test_filter_stops_data_with_extra_stops(self):
        """Test filtering when DataFrame contains stops not in the predefined list."""
        df_with_extra = pl.DataFrame({
            'stop_id': ['8147', '8545', '9999', '8888'],
            'stop_code': ['8147', '8545', '9999', '8888'],
            'stop_name': ['Stop A', 'Stop B', 'Extra Stop 1', 'Extra Stop 2']
        })
        
        result = filter_stops_data(df_with_extra)
        
        assert isinstance(result, pl.DataFrame)
        assert len(result) == 2  # Only predefined stops should remain
        assert all(stop_code in ["8147", "8545"] for stop_code in result["stop_code"])

    def test_filter_stops_data_empty_result(self):
        """Test filtering when no stops match the predefined list."""
        df_no_matches = pl.DataFrame({
            'stop_id': ['9999', '8888'],
            'stop_code': ['9999', '8888'],
            'stop_name': ['Extra Stop 1', 'Extra Stop 2']
        })
        
        result = filter_stops_data(df_no_matches)
        
        assert isinstance(result, pl.DataFrame)
        assert len(result) == 0

    def test_filter_stops_data_exception_handling(self):
        """Test exception handling in filter_stops_data."""
        # Create a DataFrame that will cause an error when filtering
        invalid_df = "not a dataframe"
        
        with pytest.raises(Exception):
            filter_stops_data(invalid_df)


class TestSendStopDataToGcs:
    """Test cases for send_stop_data_to_gcs function."""

    @patch('at_bus_load.get_at_api_data.pl.DataFrame.write_parquet')
    def test_send_stop_data_to_gcs_success(self, mock_write_parquet, mock_storage_client, sample_stops_data):
        """Test successful upload of stops data to GCS."""
        send_stop_data_to_gcs(mock_storage_client, sample_stops_data, "2024-01-01")
        
        # Verify the bucket and blob were accessed correctly
        mock_storage_client.bucket.assert_called_once_with("at-bus-open-data")
        mock_storage_client.bucket().blob.assert_called_once_with("2024-01-01/stops.parquet")
        
        # Verify the parquet file was written
        mock_write_parquet.assert_called_once_with("data/stops.parquet")
        
        # Verify the blob was uploaded
        mock_storage_client.bucket().blob().upload_from_filename.assert_called_once_with("data/stops.parquet")

    def test_send_stop_data_to_gcs_exception_handling(self, mock_storage_client, sample_stops_data):
        """Test exception handling in send_stop_data_to_gcs."""
        # Make the upload fail
        mock_storage_client.bucket().blob().upload_from_filename.side_effect = Exception("Upload failed")
        
        with pytest.raises(Exception, match="Upload failed"):
            send_stop_data_to_gcs(mock_storage_client, sample_stops_data, "2024-01-01")


class TestSendTripsDataToGcs:
    """Test cases for send_trips_data_to_gcs function."""

    @patch('at_bus_load.get_at_api_data.pl.DataFrame.write_parquet')
    def test_send_trips_data_to_gcs_success(self, mock_write_parquet, mock_storage_client, sample_trips_data):
        """Test successful upload of trips data to GCS."""
        send_trips_data_to_gcs(mock_storage_client, sample_trips_data, "route_001", "2024-01-01")
        
        # Verify the bucket and blob were accessed correctly
        mock_storage_client.bucket.assert_called_once_with("at-bus-open-data")
        mock_storage_client.bucket().blob.assert_called_once_with("2024-01-01/trips_route_001.parquet")
        
        # Verify the parquet file was written
        mock_write_parquet.assert_called_once_with("data/trips_route_001.parquet")
        
        # Verify the blob was uploaded
        mock_storage_client.bucket().blob().upload_from_filename.assert_called_once_with("data/trips_route_001.parquet")

    def test_send_trips_data_to_gcs_exception_handling(self, mock_storage_client, sample_trips_data):
        """Test exception handling in send_trips_data_to_gcs."""
        # Make the upload fail
        mock_storage_client.bucket().blob().upload_from_filename.side_effect = Exception("Upload failed")
        
        with pytest.raises(Exception, match="Upload failed"):
            send_trips_data_to_gcs(mock_storage_client, sample_trips_data, "route_001", "2024-01-01") 