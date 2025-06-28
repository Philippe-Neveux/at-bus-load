from loguru import logger

from at_bus_load.gcp import ConnectGCS, get_gcp_token_from_default_credentials


def main():

    token = get_gcp_token_from_default_credentials()
    client = ConnectGCS(token).client

    # Specify the bucket and file name
    bucket_name = 'pne-open-data'
    file_name = 'personality_dataset.csv'

    # Get the bucket instance
    bucket = client.get_bucket(bucket_name)

    # Check if the file exists
    blob = bucket.blob(file_name)
    if blob.exists():
        logger.info(f'The file {file_name} exists in bucket {bucket_name}')
    else:
        logger.info(f'The file {file_name} does not exist in bucket {bucket_name}')
        
def entrypoint():
    """CLI entry point for the script."""
    main()


if __name__ == "__main__":
    main()