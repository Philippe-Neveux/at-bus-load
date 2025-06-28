import datetime
import os
from typing import Dict, Optional

import polars as pl
import requests
import typer
from dotenv import load_dotenv
from google.cloud import storage  # type: ignore
from loguru import logger

from at_bus_load import entrypoints_params
from at_bus_load.gcp import ConnectGCS, get_token_from_env_var


def get_at_gtfs_data_from_at_mobile_api(
    data_name: str,
    params: Dict[str, str | int] = {},
    headers: Dict[str, str] = {}
) -> pl.DataFrame:
    
    """
    Fetches data from Auckland Transport's GTFS API.

    Args:
        data_name: The name of the data to fetch.
        params: Additional query parameters to pass to the request.
        headers: Additional headers to pass to the request.

    Returns:
        A Polars DataFrame containing the fetched data.
    """
    url = f"https://api.at.govt.nz/gtfs/v3/{data_name}"
    
    response = requests.get(
        url,
        params=params, 
        headers=headers
    )
    
    # logger.info(f"Request URL: {response.url}")
    if response.status_code != 200:
        logger.error(f"Request failed with status code {response.status_code}: {response.text}")
        raise Exception(f"Request failed with status code {response.status_code}: {response.text}")
    else:
        data = response.json()
        if "data" not in data:
            logger.error("Expected 'data' key in the JSON response")
        
        logger.info(f"Successfully getting data from request '{response.url}'.")
        
        json_data = data["data"]

        # Load data into Polars DataFrame
        df = pl.DataFrame(json_data)
        
        for col, dtype in df.schema.items():
            if isinstance(dtype, pl.datatypes.Struct):
                df = df.unnest(col)
                
        return df
    
def get_at_api_key() -> str:
    """
    Retrieves the Auckland Transport API key from environment variables.

    Returns:
        str: The API key for accessing Auckland Transport services.

    Raises:
        ValueError: If the API key is not found in the environment variables.

    Logs:
        Logs an error if the API key is not found.
        Logs an info message if the API key is successfully retrieved.
    """

    api_key = os.getenv("AT_API_KEY")
    
    if not api_key:
        logger.error("Auckland Transport API key not found in environment variables.")
        raise ValueError("Auckland Transport API key not found.")
    
    logger.info("Successfully retrieved Auckland Transport API key.")
    
    return api_key

def get_stops_data(api_date: str) -> pl.DataFrame:
    """
    Fetches the stops data for a given date from the Auckland Transport GTFS API.

    Args:
        api_date (str): The date for which to fetch the stops data in 'YYYY-MM-DD' format.

    Returns:
        pl.DataFrame: A Polars DataFrame containing the stops data with an additional column 'api_date_ingestion'
                      indicating the date of data ingestion.

    Raises:
        Exception: If there is an error while fetching or processing the data, the exception is logged and re-raised.
    """

    try:
        df_stops = get_at_gtfs_data_from_at_mobile_api(
            data_name="stops",
            params={
                "filter[date]": api_date
            },
            headers = {
                "Cache-Control": "no-cache",
                "Ocp-Apim-Subscription-Key": get_at_api_key()
            }
        ).with_columns(
            pl.lit(api_date).cast(pl.Date).alias("api_date_ingestion"),
        )
            
        return df_stops
    except Exception as e:
        logger.error(f"Error loading stops data: {e}")
        raise

def filter_stops_data(stops_data: pl.DataFrame) -> pl.DataFrame:
    """
    Filters stops data to only include stops with codes in a predefined list.

    Args:
        stops_data (pl.DataFrame): The stops data to filter.

    Returns:
        pl.DataFrame: A filtered DataFrame containing only stops with codes in the predefined list.

    Raises:
        Exception: If there is an error while filtering the data, the exception is logged and re-raised.

    Logs:
        Logs an info message if the filtering is successful.
        Logs an error if there is an error while filtering the data.
    """
    try:
        stop_codes = [
            "8147",
            "8545",
            "7149",
            "8331",
            "7133"
        ]
        
        _df = (
            stops_data
            .filter(
                pl.col("stop_code")
                .is_in(stop_codes)
            )
        )
        logger.info("Successfully filtered stop data.")
        return _df
    except Exception as e:
        logger.error(f"Error filtering stop data: {e}")
        raise

def send_stop_data_to_gcs(
    client: storage.Client,
    df_stops: pl.DataFrame,
    api_date: str
) -> None:
    """
    Sends the stops data to Google Cloud Storage.

    This function takes a Polars DataFrame containing stop data, and uploads it as a Parquet file to Google Cloud Storage.
    The Parquet file is stored in the "at-bus" bucket with the following structure:
    "at-bus/{api_date}/stops.parquet"

    Args:
        client: An instance of the Google Cloud Storage client.
        df_stops: A Polars DataFrame containing stop data.
        api_date: The date of the data in the source Parquet file.

    Returns:
        None

    Raises:
        Exception: If there is an error while uploading the data to GCS, the exception is logged and re-raised.

    Logs:
        Logs an info message if the upload is successful.
        Logs an error if there is an error while uploading the data to GCS.
    """
    try:
        bucket = client.bucket("pne-open-data")
        blob = bucket.blob(f"at-bus/{api_date}/stops.parquet")
        
        df_stops.write_parquet("data/stops.parquet")
        
        blob.upload_from_filename("data/stops.parquet")
        
        logger.info("Successfully uploaded stop data to GCS.")
    except Exception as e:
        logger.error(f"Error uploading stop data to GCS: {e}")
        raise

def get_trips_data(stop_id: str, api_date: str) -> pl.DataFrame:
    """
    Fetches the trips data for a given stop and date from the AT API, and returns it as a Polars DataFrame.

    Args:
        stop_id (str): The ID of the stop for which to fetch trips data.
        api_date (str): The date for which to fetch trips data.

    Returns:
        pl.DataFrame: A Polars DataFrame containing the trips data for the specified stop and date.

    Raises:
        Exception: If there is an error while fetching the data from the AT API, the exception is logged and re-raised.

    Logs:
        Logs an info message if the data is loaded successfully.
        Logs an error if there is an error while loading the data from the AT API.
    """
    try:
        df_trips = get_at_gtfs_data_from_at_mobile_api(
            data_name=f"stops/{stop_id}/stoptrips",
            params={
                "filter[date]": api_date,
                "filter[start_hour]": 3,
                "filter[hour_range]": 24
            },
            headers = {
                "Cache-Control": "no-cache",
                "Ocp-Apim-Subscription-Key": get_at_api_key()
            }
        ).with_columns(
            pl.lit(api_date).cast(pl.Date).alias("api_date_ingestion"),
        )
        
        logger.info(f"Successfully loaded trip data for stop {stop_id} on date {api_date}.")
        return df_trips
    except Exception as e:
        logger.error(f"Error loading trips data for stop {stop_id} on date {api_date}: {e}")
        raise

def send_trips_data_to_gcs(
    client: storage.Client,
    df_trips: pl.DataFrame,
    stop_id: str,
    api_date: str
) -> None:
    """
    Sends the trips data to Google Cloud Storage.

    This function takes a Polars DataFrame containing trip data, and uploads it as a Parquet file to Google Cloud Storage.
    The Parquet file is stored in the "at-bus" bucket with the following structure:
    "at-bus/{api_date}/trips_{stop_id}.parquet"

    Args:
        client: An instance of the Google Cloud Storage client.
        df_trips: A Polars DataFrame containing trip data.
        stop_id: The ID of the stop for which to upload trips data.
        api_date: The date of the data in the source Parquet file.

    Returns:
        None

    Raises:
        Exception: If there is an error while uploading the data to GCS, the exception is logged and re-raised.

    Logs:
        Logs an info message if the upload is successful.
        Logs an error if there is an error while uploading the data to GCS.
    """
    try:
        bucket = client.bucket("pne-open-data")
        blob = bucket.blob(f"at-bus/{api_date}/trips_{stop_id}.parquet")
        
        df_trips.write_parquet(f"data/trips_{stop_id}.parquet")
        
        blob.upload_from_filename(f"data/trips_{stop_id}.parquet")
        
        logger.info(f"Successfully uploaded trip data for stop {stop_id} to GCS.")
    except Exception as e:
        logger.error(f"Error uploading trip data for stop {stop_id} to GCS: {e}")
        raise


def main(
    date: str = typer.Option(
        default=datetime.date.today().strftime("%Y-%m-%d"),
        help="Date for which to fetch the data (format: YYYY-MM-DD). Default is today."
    ),
    env_var_token: Optional[str] = typer.Option(
        default=None,
        help="The environment variable where to get the token for GCS"
    )
) -> None:
    """
    Main function to fetch and process Auckland Transport bus data.

    This function parses command line arguments, loads environment variables,
    and establishes a connection to Google Cloud Storage using a token. It
    retrieves bus stop data for a specified date, filters the data, and uploads
    it to GCS. For each bus stop, it fetches trip data and uploads it to GCS.

    Raises:
        Exception: If there are any errors uploading data to GCS.
    """
    
    entrypoints_params.validate_date(date)
    api_date = date
    
    logger.info(f"Fetching data for date: {api_date}")
    
    load_dotenv()
    
    token = get_token_from_env_var(env_var_token)
    client = ConnectGCS(token).client
    
    df_stops = get_stops_data(api_date)
    df_stops = filter_stops_data(df_stops)
    
    send_stop_data_to_gcs(client, df_stops, api_date)
    
    stop_ids = df_stops["id"].to_list()
    for stop_id in stop_ids:
        logger.info(f"Fetching trips for stop {stop_id} on date {api_date}")
        
        df_trips = get_trips_data(stop_id, api_date)
        send_trips_data_to_gcs(client, df_trips, stop_id, api_date)

def entrypoint():
    """CLI entry point for the script."""
    typer.run(main)


if __name__ == "__main__":
    typer.run(main)
