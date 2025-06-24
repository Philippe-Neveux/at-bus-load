import re
from typing import List

from google.cloud import bigquery, storage  # type: ignore
from loguru import logger

from at_bus_load.entrypoints_params import get_args_params
from at_bus_load.gcp import ConnectBQ, ConnectGCS, get_token_from_env_var


def move_parquet_file_to_bq_dataset(
    bq_client: bigquery.Client,
    dataset_id: str,
    table_id: str,
    source_uri: str
) -> None:
    """
    Loads a Parquet file from Google Cloud Storage into a BigQuery dataset.

    Args:
        bq_client: An instance of the BigQuery client.
        dataset_id: The ID of the BigQuery dataset.
        table_id: The ID of the BigQuery table.
        source_uri: The URI of the source Parquet file in Google Cloud Storage.

    Returns:
        None
    """

    table_ref = bq_client.dataset(dataset_id).table(table_id)

    # Load the Parquet file into BigQuery
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
    )

    logger.info(f"Loading '{source_uri}' into '{dataset_id}.{table_id}'")
    load_job = bq_client.load_table_from_uri(
        source_uri, table_ref, job_config=job_config
    )

    # Wait for the load job to complete
    load_job.result()

def move_stops_data_to_bq(
    bq_client: bigquery.Client,
    source_bucket_name: str,
    exec_date: str
) -> None:
    """
    Loads a Parquet file from Google Cloud Storage into a BigQuery dataset.

    This function assumes that the Parquet file is located at
    `gs://{source_bucket_name}/at-bus/{date}/stops.parquet`.

    The data is loaded into the BigQuery dataset `at_bus_bronze` with a table name
    that is the same as the date in the source URI.

    Args:
        bq_client: An instance of the BigQuery client.
        source_bucket_name: The name of the Google Cloud Storage bucket containing
            the source Parquet file.
        exec_date: The date of the data in the source Parquet file.

    Returns:
        None
    """
    source_file_name = f'at-bus/{exec_date}/stops.parquet'

    # Define the destination BigQuery dataset and table
    dataset_id = 'at_bus_bronze'
    table_id = f'stops_{exec_date}'

    # Create a reference to the source Parquet file
    source_uri = f'gs://{source_bucket_name}/{source_file_name}'

    move_parquet_file_to_bq_dataset(bq_client, dataset_id, table_id, source_uri)
    

def get_all_route_id_from_trips_file_name(
    gcs_client: storage.Client,
    source_bucket_name: str,
    exec_date: str
) -> List[str]:
    """
    Get a list of all route IDs from the trips file names in the source bucket.
    
    Args:
        gcs_client: The GCS client instance.
        source_bucket_name: The name of the source bucket.
        exec_date: The date of the data to be processed.
    
    Returns:
        A list of route IDs.
    """

    bucket = gcs_client.get_bucket(f"{source_bucket_name}")
    
    # Get a list of all blobs in the source bucket with the given prefix
    blobs = list(bucket.list_blobs(prefix=f"at-bus/{exec_date}"))

    route_ids = []
    
    # Iterate over each blob and extract the route ID from the file name
    for blob in blobs:
        blob_name = blob.name.rsplit('/', 1)[-1]
        
        # Use a regular expression to search for the route ID in the file name
        search_regex = re.search(r'trips_(.*)\.parquet', blob_name)
        if search_regex:
            # If the route ID is found, add it to the list
            route_ids.append(search_regex.group(1))
    
    return route_ids
    
def move_trips_data_to_bq(
    gcs_client: storage.Client,
    bq_client: bigquery.Client,
    source_bucket_name: str,
    exec_date: str
) -> None:
    
    """
    Move trips data from GCS to BigQuery.

    This function takes all the Parquet files in the source GCS bucket with the
    given date and moves them to BigQuery as separate tables.

    Args:
        gcs_client: The GCS client instance.
        bq_client: The BigQuery client instance.
        source_bucket_name: The name of the source bucket.
        date: The date of the data to be processed.
    """
    dataset_id = 'at_bus_bronze'
    
    route_ids: List[str] = get_all_route_id_from_trips_file_name(
        gcs_client,
        source_bucket_name,
        exec_date
    )
    
    for route_id in route_ids:
        source_file_name = f'at-bus/{exec_date}/trips_{route_id}.parquet'
        table_id = f'trips_{route_id}_{exec_date}'

        # Create a reference to the source Parquet file
        source_uri = f'gs://{source_bucket_name}/{source_file_name}'

        move_parquet_file_to_bq_dataset(bq_client, dataset_id, table_id, source_uri)


def main():
    # Set up credentials and client instances
    """
    Main entry point for the script.

    This function sets up credentials and client instances, determines the current
    date, and moves the stops and trips data from GCS to BigQuery.
    """
    args = get_args_params()
    exec_date = args.date
    
    logger.info(f"Moving data from GCS to for date: {exec_date}")
    
    
    token = get_token_from_env_var(args.env_var_token)
    client_gcs = ConnectGCS(token).client
    client_bq = ConnectBQ(token).client
    
    source_bucket_name = 'pne-open-data'
    
    move_stops_data_to_bq(client_bq, source_bucket_name, exec_date)
    move_trips_data_to_bq(client_gcs, client_bq, source_bucket_name, exec_date)


if __name__ == "__main__":
    main()
