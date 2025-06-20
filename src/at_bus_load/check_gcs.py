from google.cloud import storage
from loguru import logger

def main():
        # Create a client instance
    client = storage.Client()

    # Specify the bucket and file name
    bucket_name = 'pne-open-data'
    file_name = 'personality_dataset.csv'

    # Get the bucket instance
    bucket = client.get_bucket(bucket_name)

    # Check if the file exists
    blob = bucket.blob(file_name)
    if blob.exists():
        print(f'The file {file_name} exists in bucket {bucket_name}')
    else:
        print(f'The file {file_name} does not exist in bucket {bucket_name}')
        
if __name__ == "__main__":
    main()