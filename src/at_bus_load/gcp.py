import os

import google.auth
import google.auth.transport.requests
import google.oauth2.credentials
from google.cloud import bigquery, storage  # type: ignore
from loguru import logger


def get_gcp_token_from_default_credentials() -> str:
    """
    Obtain an access token from Google Cloud Platform default credentials.

    This function retrieves default application credentials, refreshes them
    to ensure they are valid, and returns the access token. The token can be
    used to authenticate requests to Google Cloud Platform services.

    Returns:
        str: The access token obtained from the default credentials.
    """

    creds, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])

    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)

    return creds.token


def get_token_from_env_var(env_var_token: str | None) -> str | None:
    if env_var_token:
        return os.getenv(env_var_token)
    else:
        return None

class ConnectGCS:
    def __init__(
        self,
        token: str | None = None,
    ) -> None:
        """
        Initialize the ConnectGCS class.

        Args:
            token (str | None): Optional, a GCP token to use for authentication.
                If not provided, default credentials will be used.
        """
        self._connnect_to_gcs(token)
    
    @property
    def client(self) -> storage.Client:
        return self._client
        
    def _connnect_to_gcs(
        self,
        token: str | None = None
    ) -> None:
        """
        Connect to GCS using the provided token, or default credentials if no token is provided
        """
        if token:
            logger.info("Using token to connect to GCS")
            creds = google.oauth2.credentials.Credentials(token)
        else:
            logger.info("Using default creds to connect to GCS")
            creds = None
        
        self._client =  storage.Client(credentials=creds)
        
        logger.info("Connected to GCS")
        
        
class ConnectBQ:
    def __init__(
        self,
        token: str | None = None,
    ) -> None:
        """
        Initialize the ConnectBQ class.

        Args:
            token (str | None): Optional, a GCP token to use for authentication.
                If not provided, default credentials will be used.
        """
        self._connnect_to_bq(token)
    
    @property
    def client(self) -> bigquery.Client:
        return self._client
        
    def _connnect_to_bq(
        self,
        token: str | None = None
    ) -> None:
        """
        Connect to BQ using the provided token, or default credentials if no token is provided
        """
        if token:
            logger.info("Using token to connect to BQ")
            creds = google.oauth2.credentials.Credentials(token)
        else:
            logger.info("Using default creds to connect to BQ")
            creds = None
        
        self._client =  bigquery.Client(credentials=creds)
        
        logger.info("Connected to BQ")