# AT Bus Load: Real-time Auckland Transport Data Pipeline

This project provides a complete data pipeline for fetching, storing, and analyzing real-time bus data from Auckland Transport (AT). It is designed to run entirely on Google Cloud Platform (GCP), using a suite of tools to automate data ingestion, processing, and storage for advanced analytics.

## Key Features

- **API Data Ingestion**: Fetches live bus data directly from the official AT API, ensuring you always have the most current information
- **Scalable Data Storage**: Utilizes Google Cloud Storage (GCS) for staging raw data and Google BigQuery for structured, long-term storage, enabling powerful analytical queries.

## Getting Started

### Prerequisites

- A Google Cloud Platform (GCP) account with billing enabled.
- The `gcloud` command-line tool installed and authenticated.
- An API key from Auckland Transport for accessing their real-time data.

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/at-bus-load.git
   cd at-bus-load
   ```

2. **Set up the environment**:
   - Create a `.env` file and add your AT API key:
     ```
     AT_API_KEY=your_api_key_here
     ```

### Run the code

1. **Get the data from AT API**:
   ```bash
   make get_api_data DATE=2025-07-11
   ```

2. **Move the data to BigQuery**:
   ```bash
   make move_gcs_data_to_bq DATE=2025-07-11
   ```

### Contributing

We welcome contributions! If you have ideas for new features, improvements, or bug fixes, please open an issue or submit a pull request. See our `CONTRIBUTING.md` for more details on how to get started.

### License

This project is licensed under the MIT License. See the `LICENSE` file for more information.

This is an update