import datetime

from loguru import logger

def main():
    now = datetime.datetime.now()
    logger.info(f"Today is: {now.strftime("%d-%m-%Y")} and I'm executing the script move_gcs_data_to_bq.py")

if __name__ == "__main__":
    main()
