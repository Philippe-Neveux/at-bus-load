"""
Unit tests for gcp module.
"""
import os
from unittest.mock import Mock, patch

import pytest
from google.cloud import bigquery, storage

from at_bus_load.gcp import ConnectBQ, ConnectGCS, get_gcp_token_from_default_credentials, get_token_from_env_var


class TestGetGcpTokenFromDefaultCredentials:
    """Test cases for get_gcp_token_from_default_credentials function."""

    @patch('at_bus_load.gcp.google.auth.default')
    @patch('at_bus_load.gcp.google.auth.transport.requests.Request')
    def test_get_gcp_token_from_default_credentials_success(
        self, mock_request, mock_default, mock_gcp_credentials
    ):
        """Test successful token retrieval from default credentials."""
        mock_default.return_value = (mock_gcp_credentials, None)
        
        result = get_gcp_token_from_default_credentials()
        
        # Verify google.auth.default was called with correct scopes
        mock_default.assert_called_once_with(scopes=['https://www.googleapis.com/auth/cloud-platform'])
        
        # Verify credentials were refreshed
        mock_gcp_credentials.refresh.assert_called_once_with(mock_request())
        
        # Verify the token was returned
        assert result == "test-token-12345"

    @patch('at_bus_load.gcp.google.auth.default')
    def test_get_gcp_token_from_default_credentials_exception(self, mock_default):
        """Test exception handling in get_gcp_token_from_default_credentials."""
        mock_default.side_effect = Exception("Authentication failed")
        
        with pytest.raises(Exception, match="Authentication failed"):
            get_gcp_token_from_default_credentials()


class TestGetTokenFromEnvVar:
    """Test cases for get_token_from_env_var function."""

    def test_get_token_from_env_var_with_token(self, mock_env_vars):
        """Test successful token retrieval from environment variable."""
        result = get_token_from_env_var("GCP_TOKEN")
        assert result == "test-gcp-token-12345"

    def test_get_token_from_env_var_without_token(self, mock_env_vars):
        """Test token retrieval when env_var_token is None."""
        result = get_token_from_env_var(None)
        assert result is None

    def test_get_token_from_env_var_missing_variable(self, mock_env_vars):
        """Test token retrieval when environment variable doesn't exist."""
        result = get_token_from_env_var("NONEXISTENT_TOKEN")
        assert result is None

    def test_get_token_from_env_var_empty_environment(self):
        """Test token retrieval with empty environment."""
        with patch.dict(os.environ, {}, clear=True):
            result = get_token_from_env_var("GCP_TOKEN")
            assert result is None


class TestConnectGCS:
    """Test cases for ConnectGCS class."""

    @patch('at_bus_load.gcp.storage.Client')
    def test_connect_gcs_with_token(self, mock_storage_client):
        """Test GCS connection with token authentication."""
        token = "test-token-12345"
        
        connect_gcs = ConnectGCS(token)
        
        # Verify storage.Client was called with credentials
        mock_storage_client.assert_called_once()
        call_args = mock_storage_client.call_args
        assert call_args[1]['credentials'] is not None
        
        # Verify the client property returns the mock client
        assert connect_gcs.client == mock_storage_client()

    @patch('at_bus_load.gcp.storage.Client')
    def test_connect_gcs_without_token(self, mock_storage_client):
        """Test GCS connection without token (using default credentials)."""
        connect_gcs = ConnectGCS()
        
        # Verify storage.Client was called without credentials
        mock_storage_client.assert_called_once()
        call_args = mock_storage_client.call_args
        assert call_args[1]['credentials'] is None
        
        # Verify the client property returns the mock client
        assert connect_gcs.client == mock_storage_client()

    @patch('at_bus_load.gcp.storage.Client')
    def test_connect_gcs_with_none_token(self, mock_storage_client):
        """Test GCS connection with None token."""
        connect_gcs = ConnectGCS(None)
        
        # Verify storage.Client was called without credentials
        mock_storage_client.assert_called_once()
        call_args = mock_storage_client.call_args
        assert call_args[1]['credentials'] is None
        
        # Verify the client property returns the mock client
        assert connect_gcs.client == mock_storage_client()

    @patch('at_bus_load.gcp.storage.Client')
    def test_connect_gcs_exception_handling(self, mock_storage_client):
        """Test exception handling in ConnectGCS."""
        mock_storage_client.side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception, match="Connection failed"):
            ConnectGCS()

    def test_connect_gcs_client_property(self):
        """Test the client property of ConnectGCS."""
        with patch('at_bus_load.gcp.storage.Client') as mock_storage_client:
            mock_client_instance = Mock()
            mock_storage_client.return_value = mock_client_instance
            
            connect_gcs = ConnectGCS()
            
            # Verify the client property returns the correct instance
            assert connect_gcs.client is mock_client_instance


class TestConnectBQ:
    """Test cases for ConnectBQ class."""

    @patch('at_bus_load.gcp.bigquery.Client')
    def test_connect_bq_with_token(self, mock_bigquery_client):
        """Test BigQuery connection with token authentication."""
        token = "test-token-12345"
        
        connect_bq = ConnectBQ(token)
        
        # Verify bigquery.Client was called with credentials
        mock_bigquery_client.assert_called_once()
        call_args = mock_bigquery_client.call_args
        assert call_args[1]['credentials'] is not None
        
        # Verify the client property returns the mock client
        assert connect_bq.client == mock_bigquery_client()

    @patch('at_bus_load.gcp.bigquery.Client')
    def test_connect_bq_without_token(self, mock_bigquery_client):
        """Test BigQuery connection without token (using default credentials)."""
        connect_bq = ConnectBQ()
        
        # Verify bigquery.Client was called without credentials
        mock_bigquery_client.assert_called_once()
        call_args = mock_bigquery_client.call_args
        assert call_args[1]['credentials'] is None
        
        # Verify the client property returns the mock client
        assert connect_bq.client == mock_bigquery_client()

    @patch('at_bus_load.gcp.bigquery.Client')
    def test_connect_bq_with_none_token(self, mock_bigquery_client):
        """Test BigQuery connection with None token."""
        connect_bq = ConnectBQ(None)
        
        # Verify bigquery.Client was called without credentials
        mock_bigquery_client.assert_called_once()
        call_args = mock_bigquery_client.call_args
        assert call_args[1]['credentials'] is None
        
        # Verify the client property returns the mock client
        assert connect_bq.client == mock_bigquery_client()

    @patch('at_bus_load.gcp.bigquery.Client')
    def test_connect_bq_exception_handling(self, mock_bigquery_client):
        """Test exception handling in ConnectBQ."""
        mock_bigquery_client.side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception, match="Connection failed"):
            ConnectBQ()

    def test_connect_bq_client_property(self):
        """Test the client property of ConnectBQ."""
        with patch('at_bus_load.gcp.bigquery.Client') as mock_bigquery_client:
            mock_client_instance = Mock()
            mock_bigquery_client.return_value = mock_client_instance
            
            connect_bq = ConnectBQ()
            
            # Verify the client property returns the correct instance
            assert connect_bq.client is mock_client_instance


class TestIntegrationScenarios:
    """Integration test scenarios for the gcp module."""

    @patch('at_bus_load.gcp.storage.Client')
    @patch('at_bus_load.gcp.bigquery.Client')
    def test_gcs_and_bq_connection_workflow(self, mock_bq_client, mock_gcs_client):
        """Test the workflow of connecting to both GCS and BigQuery."""
        # Set up mock return values
        mock_gcs_instance = Mock()
        mock_bq_instance = Mock()
        mock_gcs_client.return_value = mock_gcs_instance
        mock_bq_client.return_value = mock_bq_instance
        
        # Test GCS connection
        gcs_connection = ConnectGCS("gcs-token")
        assert gcs_connection.client == mock_gcs_instance
        
        # Test BigQuery connection
        bq_connection = ConnectBQ("bq-token")
        assert bq_connection.client == mock_bq_instance
        
        # Verify both clients were created
        mock_gcs_client.assert_called_once()
        mock_bq_client.assert_called_once()

    @patch('at_bus_load.gcp.google.auth.default')
    @patch('at_bus_load.gcp.google.auth.transport.requests.Request')
    @patch('at_bus_load.gcp.storage.Client')
    @patch('at_bus_load.gcp.bigquery.Client')
    def test_full_authentication_workflow(
        self, mock_bq_client, mock_gcs_client, mock_request, mock_default, mock_gcp_credentials
    ):
        """Test the complete authentication workflow."""
        # Set up mock return values
        mock_gcs_instance = Mock()
        mock_bq_instance = Mock()
        mock_gcs_client.return_value = mock_gcs_instance
        mock_bq_client.return_value = mock_bq_instance
        
        # Mock default credentials
        mock_default.return_value = (mock_gcp_credentials, None)
        
        # Get token from default credentials
        token = get_gcp_token_from_default_credentials()
        assert token == "test-token-12345"
        
        # Connect to GCS with the token
        gcs_connection = ConnectGCS(token)
        assert gcs_connection.client == mock_gcs_instance
        
        # Connect to BigQuery with the token
        bq_connection = ConnectBQ(token)
        assert bq_connection.client == mock_bq_instance
        
        # Verify all components were called correctly
        mock_default.assert_called_once()
        mock_gcp_credentials.refresh.assert_called_once()
        mock_gcs_client.assert_called_once()
        mock_bq_client.assert_called_once()


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @patch('at_bus_load.gcp.storage.Client')
    def test_connect_gcs_empty_token_string(self, mock_storage_client):
        """Test GCS connection with empty token string."""
        connect_gcs = ConnectGCS("")
        
        # Should treat empty string as no token
        mock_storage_client.assert_called_once()
        call_args = mock_storage_client.call_args
        assert call_args[1]['credentials'] is None

    @patch('at_bus_load.gcp.bigquery.Client')
    def test_connect_bq_empty_token_string(self, mock_bigquery_client):
        """Test BigQuery connection with empty token string."""
        connect_bq = ConnectBQ("")
        
        # Should treat empty string as no token
        mock_bigquery_client.assert_called_once()
        call_args = mock_bigquery_client.call_args
        assert call_args[1]['credentials'] is None

    def test_get_token_from_env_var_empty_string(self, mock_env_vars):
        """Test token retrieval with empty string environment variable."""
        with patch.dict(os.environ, {'EMPTY_TOKEN': ''}):
            result = get_token_from_env_var("EMPTY_TOKEN")
            assert result == ""

    @patch('at_bus_load.gcp.google.auth.default')
    def test_get_gcp_token_credentials_refresh_failure(self, mock_default):
        """Test handling of credential refresh failure."""
        mock_creds = Mock()
        mock_creds.refresh.side_effect = Exception("Refresh failed")
        mock_default.return_value = (mock_creds, None)
        
        with pytest.raises(Exception, match="Refresh failed"):
            get_gcp_token_from_default_credentials() 