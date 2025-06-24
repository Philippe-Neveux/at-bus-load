import google.auth
from google.cloud import storage
import google.auth.transport.requests
import google.oauth2.credentials
from loguru import logger

def get_gcp_token_from_default_credentials() -> str:
    creds, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])

    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)

    return creds.token

class ConnectGCS:
    def __init__(
        self,
        token: str | None = None,
    ) -> None:
        self._connnect_to_gcs(token)
    
    @property
    def client(self) -> storage.Client:
        return self._client
        
    def _connnect_to_gcs(
        self,
        token: str | None = None
    ) -> None:
        if token:
            logger.info("Using token to connect to GCS")
            creds = google.oauth2.credentials.Credentials(token)
        else:
            logger.info("Using default creds to connect to GCS")
            creds = None
        
        self._client =  storage.Client(credentials=creds)