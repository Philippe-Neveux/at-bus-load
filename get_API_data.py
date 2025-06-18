import argparse
from datetime import date
import requests
from typing import Dict
import os

from dotenv import load_dotenv
from google.cloud import storage
from loguru import logger
import polars as pl


def get_at_gtfs_data_from_at_mobile_api(
    data_name: str,
    params: Dict[str, str | int] = {},
    headers: Dict[str, str] = {}
) -> pl.DataFrame:
    
    url = f"https://api.at.govt.nz/gtfs/v3/{data_name}"
    
    response = requests.get(
        url,
        params=params, 
        headers=headers
    )
    
    # logger.info(f"Request URL: {response.url}")
    if response.status_code != 200:
        logger.error(f"Request failed with status code {response.status_code}: {response.text}")
    
    data = response.json()
    if "data" not in data:
        logger.error("Expected 'data' key in the JSON response")
    
    logger.info(f"Successfully loaded data from request '{response.url}' into .")
    
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
    """
    api_key = os.getenv("AT_API_KEY")
    
    if not api_key:
        logger.error("Auckland Transport API key not found in environment variables.")
        raise ValueError("Auckland Transport API key not found.")
    
    logger.info("Successfully retrieved Auckland Transport API key.")
    
    return api_key

def get_stops_data(api_date: str) -> pl.DataFrame:
    """
    Fetches stop data from a API request and returns it as a Polars DataFrame.
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
    Filters the stops data to include only relevant stops id
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

def send_stop_data_to_gcs(df_stops: pl.DataFrame, api_date: str) -> None:
    """
    Sends the stops data to Google Cloud Storage.
    """
    try:
        client = storage.Client()  # Assumes GOOGLE_APPLICATION_CREDENTIALS is set
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
    Fetches trip data for a specific stop on a given date.
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

def send_trips_data_to_gcs(df_trips: pl.DataFrame, stop_id: str, api_date: str) -> None:
    """
    Sends the trips data to Google Cloud Storage.
    """
    try:
        client = storage.Client()  # Assumes GOOGLE_APPLICATION_CREDENTIALS is set
        bucket = client.bucket("pne-open-data")
        blob = bucket.blob(f"at-bus/{api_date}/trips_{stop_id}.parquet")
        
        df_trips.write_parquet(f"data/trips_{stop_id}.parquet")
        
        blob.upload_from_filename(f"data/trips_{stop_id}.parquet")
        
        logger.info(f"Successfully uploaded trip data for stop {stop_id} to GCS.")
    except Exception as e:
        logger.error(f"Error uploading trip data for stop {stop_id} to GCS: {e}")
        raise

def get_args_params() -> argparse.Namespace:
    """
    Parses command line arguments.
    """
    parser = argparse.ArgumentParser(description="Fetch and process Auckland Transport bus data.")
    
    parser.add_argument(
        "--date",
        type=str,
        default=date.today().strftime("%Y-%m-%d"),
        help="Date for which to fetch the data (format: YYYY-MM-DD). Default is today."
    )
    
    args = parser.parse_args()
    
    logger.info(f"Arguments received: {args}")
    
    return args

def main():
    
    args = get_args_params()
    api_date = args.date
    
    logger.info(f"Fetching data for date: {api_date}")
    
    load_dotenv()
    
    df_stops: pl.DataFrame = get_stops_data(api_date)
    df_stops: pl.DataFrame = filter_stops_data(df_stops)
    
    send_stop_data_to_gcs(df_stops, api_date)
    
    stop_ids = df_stops["id"].to_list()
    for stop_id in stop_ids:
        logger.info(f"Fetching trips for stop {stop_id} on date {api_date}")
        
        df_trips = get_trips_data(stop_id, api_date)
        send_trips_data_to_gcs(df_trips, stop_id, api_date)
    


if __name__ == "__main__":
    main()
