"""
Unit tests for move_gcs_data_to_bq module.
"""
import re
from unittest.mock import Mock, patch

import pytest
from google.cloud import bigquery, storage

from at_bus_load.move_gcs_data_to_bq import (
    get_all_route_id_from_trips_file_name,
    move_parquet_file_to_bq_dataset,
    move_stops_data_to_bq,
    move_trips_data_to_bq
)


class TestMoveParquetFileToBqDataset:
    """Test cases for move_parquet_file_to_bq_dataset function."""

    def test_move_parquet_file_to_bq_dataset_success(self, mock_bigquery_client):
        """Test successful loading of parquet file to BigQuery."""
        source_uri = "gs://test-bucket/test-file.parquet"
        dataset_id = "test_dataset"
        table_id = "test_table"
        
        move_parquet_file_to_bq_dataset(
            mock_bigquery_client, dataset_id, table_id, source_uri
        )
        
        # Verify dataset and table were accessed correctly
        mock_bigquery_client.dataset.assert_called_once_with(dataset_id)
        mock_bigquery_client.dataset().table.assert_called_once_with(table_id)
        
        # Verify load_table_from_uri was called with correct parameters
        mock_bigquery_client.load_table_from_uri.assert_called_once()
        call_args = mock_bigquery_client.load_table_from_uri.call_args
        assert call_args[0][0] == source_uri  # source_uri
        assert call_args[0][1] == mock_bigquery_client.dataset().table()  # table_ref
        
        # Verify job config
        job_config = call_args[1]['job_config']
        assert job_config.source_format == bigquery.SourceFormat.PARQUET
        assert job_config.write_disposition == bigquery.WriteDisposition.WRITE_TRUNCATE
        
        # Verify job.result() was called
        mock_bigquery_client.load_table_from_uri().result.assert_called_once()

    def test_move_parquet_file_to_bq_dataset_exception_handling(self, mock_bigquery_client):
        """Test exception handling in move_parquet_file_to_bq_dataset."""
        # Make the load job fail
        mock_bigquery_client.load_table_from_uri().result.side_effect = Exception("Load failed")
        
        with pytest.raises(Exception, match="Load failed"):
            move_parquet_file_to_bq_dataset(
                mock_bigquery_client, "dataset", "table", "gs://bucket/file.parquet"
            )


class TestMoveStopsDataToBq:
    """Test cases for move_stops_data_to_bq function."""

    @patch('at_bus_load.move_gcs_data_to_bq.move_parquet_file_to_bq_dataset')
    def test_move_stops_data_to_bq_success(self, mock_move_parquet, mock_bigquery_client):
        """Test successful moving of stops data to BigQuery."""
        source_bucket_name = "test-bucket"
        exec_date = "2024-01-01"
        
        move_stops_data_to_bq(mock_bigquery_client, source_bucket_name, exec_date)
        
        # Verify move_parquet_file_to_bq_dataset was called with correct parameters
        mock_move_parquet.assert_called_once_with(
            mock_bigquery_client,
            'at_bus_bronze',  # dataset_id
            'stops_2024-01-01',  # table_id
            'gs://test-bucket/at-bus/2024-01-01/stops.parquet'  # source_uri
        )


class TestGetAllRouteIdFromTripsFileName:
    """Test cases for get_all_route_id_from_trips_file_name function."""

    def test_get_all_route_id_from_trips_file_name_success(self, mock_storage_client, mock_gcs_blobs):
        """Test successful extraction of route IDs from file names."""
        # Mock blob names that match the pattern
        blob_names = [
            "at-bus/2024-01-01/trips_route_001.parquet",
            "at-bus/2024-01-01/trips_route_002.parquet", 
            "at-bus/2024-01-01/stops.parquet",  # Should be ignored
            "at-bus/2024-01-01/trips_route_003.parquet"
        ]
        mock_blobs = mock_gcs_blobs(blob_names)
        
        # Set up the mock bucket and its list_blobs method
        mock_bucket = Mock()
        mock_bucket.list_blobs.return_value = mock_blobs
        mock_storage_client.get_bucket.return_value = mock_bucket
        
        result = get_all_route_id_from_trips_file_name(
            mock_storage_client, "test-bucket", "2024-01-01"
        )
        
        # Verify the bucket was accessed correctly
        mock_storage_client.get_bucket.assert_called_once_with("test-bucket")
        mock_bucket.list_blobs.assert_called_once_with(
            prefix="at-bus/2024-01-01"
        )
        
        # Verify the correct route IDs were extracted
        expected_route_ids = ["route_001", "route_002", "route_003"]
        assert result == expected_route_ids

    def test_get_all_route_id_from_trips_file_name_no_matches(self, mock_storage_client, mock_gcs_blobs):
        """Test when no files match the trips pattern."""
        # Mock blob names that don't match the pattern
        blob_names = [
            "at-bus/2024-01-01/stops.parquet",
            "at-bus/2024-01-01/other_file.txt"
        ]
        mock_blobs = mock_gcs_blobs(blob_names)
        
        # Set up the mock bucket and its list_blobs method
        mock_bucket = Mock()
        mock_bucket.list_blobs.return_value = mock_blobs
        mock_storage_client.get_bucket.return_value = mock_bucket
        
        result = get_all_route_id_from_trips_file_name(
            mock_storage_client, "test-bucket", "2024-01-01"
        )
        
        # Should return empty list when no matches
        assert result == []

    def test_get_all_route_id_from_trips_file_name_empty_bucket(self, mock_storage_client):
        """Test when bucket is empty or has no matching files."""
        # Set up the mock bucket and its list_blobs method
        mock_bucket = Mock()
        mock_bucket.list_blobs.return_value = []
        mock_storage_client.get_bucket.return_value = mock_bucket
        
        result = get_all_route_id_from_trips_file_name(
            mock_storage_client, "test-bucket", "2024-01-01"
        )
        
        # Should return empty list
        assert result == []

    def test_get_all_route_id_from_trips_file_name_complex_route_ids(self, mock_storage_client, mock_gcs_blobs):
        """Test extraction of complex route IDs with special characters."""
        # Mock blob names with complex route IDs
        blob_names = [
            "at-bus/2024-01-01/trips_route-001-A.parquet",
            "at-bus/2024-01-01/trips_route_002_B.parquet",
            "at-bus/2024-01-01/trips_route003.parquet"
        ]
        mock_blobs = mock_gcs_blobs(blob_names)
        
        # Set up the mock bucket and its list_blobs method
        mock_bucket = Mock()
        mock_bucket.list_blobs.return_value = mock_blobs
        mock_storage_client.get_bucket.return_value = mock_bucket
        
        result = get_all_route_id_from_trips_file_name(
            mock_storage_client, "test-bucket", "2024-01-01"
        )
        
        # Verify the correct route IDs were extracted
        expected_route_ids = ["route-001-A", "route_002_B", "route003"]
        assert result == expected_route_ids


class TestMoveTripsDataToBq:
    """Test cases for move_trips_data_to_bq function."""

    @patch('at_bus_load.move_gcs_data_to_bq.get_all_route_id_from_trips_file_name')
    @patch('at_bus_load.move_gcs_data_to_bq.move_parquet_file_to_bq_dataset')
    def test_move_trips_data_to_bq_success(
        self, mock_move_parquet, mock_get_route_ids, mock_storage_client, mock_bigquery_client
    ):
        """Test successful moving of trips data to BigQuery."""
        route_ids = ["route_001", "route_002", "route_003"]
        mock_get_route_ids.return_value = route_ids
        
        source_bucket_name = "test-bucket"
        exec_date = "2024-01-01"
        
        move_trips_data_to_bq(
            mock_storage_client, mock_bigquery_client, source_bucket_name, exec_date
        )
        
        # Verify get_all_route_id_from_trips_file_name was called
        mock_get_route_ids.assert_called_once_with(
            mock_storage_client, source_bucket_name, exec_date
        )
        
        # Verify move_parquet_file_to_bq_dataset was called for each route
        assert mock_move_parquet.call_count == 3
        
        # Check the calls were made with correct parameters
        expected_calls = [
            (
                mock_bigquery_client,
                'at_bus_bronze',
                'trips_route_001_2024-01-01',
                'gs://test-bucket/at-bus/2024-01-01/trips_route_001.parquet'
            ),
            (
                mock_bigquery_client,
                'at_bus_bronze',
                'trips_route_002_2024-01-01',
                'gs://test-bucket/at-bus/2024-01-01/trips_route_002.parquet'
            ),
            (
                mock_bigquery_client,
                'at_bus_bronze',
                'trips_route_003_2024-01-01',
                'gs://test-bucket/at-bus/2024-01-01/trips_route_003.parquet'
            )
        ]
        
        for i, expected_call in enumerate(expected_calls):
            actual_call = mock_move_parquet.call_args_list[i]
            assert actual_call[0] == expected_call

    @patch('at_bus_load.move_gcs_data_to_bq.get_all_route_id_from_trips_file_name')
    @patch('at_bus_load.move_gcs_data_to_bq.move_parquet_file_to_bq_dataset')
    def test_move_trips_data_to_bq_no_routes(
        self, mock_move_parquet, mock_get_route_ids, mock_storage_client, mock_bigquery_client
    ):
        """Test moving trips data when no routes are found."""
        mock_get_route_ids.return_value = []
        
        source_bucket_name = "test-bucket"
        exec_date = "2024-01-01"
        
        move_trips_data_to_bq(
            mock_storage_client, mock_bigquery_client, source_bucket_name, exec_date
        )
        
        # Verify get_all_route_id_from_trips_file_name was called
        mock_get_route_ids.assert_called_once_with(
            mock_storage_client, source_bucket_name, exec_date
        )
        
        # Verify move_parquet_file_to_bq_dataset was not called
        mock_move_parquet.assert_not_called()

    @patch('at_bus_load.move_gcs_data_to_bq.get_all_route_id_from_trips_file_name')
    @patch('at_bus_load.move_gcs_data_to_bq.move_parquet_file_to_bq_dataset')
    def test_move_trips_data_to_bq_exception_handling(
        self, mock_move_parquet, mock_get_route_ids, mock_storage_client, mock_bigquery_client
    ):
        """Test exception handling in move_trips_data_to_bq."""
        route_ids = ["route_001"]
        mock_get_route_ids.return_value = route_ids
        mock_move_parquet.side_effect = Exception("Move failed")
        
        source_bucket_name = "test-bucket"
        exec_date = "2024-01-01"
        
        with pytest.raises(Exception, match="Move failed"):
            move_trips_data_to_bq(
                mock_storage_client, mock_bigquery_client, source_bucket_name, exec_date
            )


class TestIntegrationScenarios:
    """Integration test scenarios for the move_gcs_data_to_bq module."""

    @patch('at_bus_load.move_gcs_data_to_bq.move_parquet_file_to_bq_dataset')
    def test_full_stops_and_trips_workflow(
        self, mock_move_parquet, mock_storage_client, mock_bigquery_client
    ):
        """Test the complete workflow of moving both stops and trips data."""
        # Test stops data movement
        move_stops_data_to_bq(mock_bigquery_client, "test-bucket", "2024-01-01")
        
        # Verify stops data was moved
        mock_move_parquet.assert_called_with(
            mock_bigquery_client,
            'at_bus_bronze',
            'stops_2024-01-01',
            'gs://test-bucket/at-bus/2024-01-01/stops.parquet'
        )
        
        # Reset mock for trips test
        mock_move_parquet.reset_mock()
        
        # Mock route IDs for trips
        with patch('at_bus_load.move_gcs_data_to_bq.get_all_route_id_from_trips_file_name') as mock_get_routes:
            mock_get_routes.return_value = ["route_001", "route_002"]
            
            # Test trips data movement
            move_trips_data_to_bq(
                mock_storage_client, mock_bigquery_client, "test-bucket", "2024-01-01"
            )
            
            # Verify trips data was moved for each route
            assert mock_move_parquet.call_count == 2
            calls = mock_move_parquet.call_args_list
            
            assert calls[0][0] == (
                mock_bigquery_client,
                'at_bus_bronze',
                'trips_route_001_2024-01-01',
                'gs://test-bucket/at-bus/2024-01-01/trips_route_001.parquet'
            )
            
            assert calls[1][0] == (
                mock_bigquery_client,
                'at_bus_bronze',
                'trips_route_002_2024-01-01',
                'gs://test-bucket/at-bus/2024-01-01/trips_route_002.parquet'
            ) 