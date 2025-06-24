import argparse
from datetime import date

from loguru import logger


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
    
    parser.add_argument(
        "--env-var-token",
        type=str,
        default=None,
        help="The environment variable where to get the token for GCS"
    )
    
    args = parser.parse_args()
    
    logger.info(f"Arguments received: {args}")                  
    
    return args