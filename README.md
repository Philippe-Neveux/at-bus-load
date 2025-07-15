# AT Bus Load: Real-time Auckland Transport Data Pipeline

This repository is a part of AT Bus project. This project aims to build an ELT pipeline from open source data to a dashboard in order to visualise what are the best route bus from Avondale to Sagrado Cantina, a Mexican Restaurant in K Road, Auckland, New Zealand. The open data is provided by Auckland Transport [here](https://dev-portal.at.govt.nz/api-details#api=gtfs-api&operation=get-calendars-id).

All of the repositories of this project are the follow ones:

- [at-bus-load](https://github.com/Philippe-Neveux/at-bus-load): Python repository for loading data from the open API provided by Auckland Transport to a Google Cloud Storage bucket and then moved to BigQuery.
- [at-bus-transform](https://github.com/Philippe-Neveux/at-bus-transform): dbt project for transforming the data from BigQuery bronze dataset to a BigQuery gold dataset.
- [at-bus-superset-server](https://github.com/Philippe-Neveux/at-bus-superset-server): Superset server for visualising the BigQuery gold dataset (Ansible).
- [at-bus-airflow-server](https://github.com/Philippe-Neveux/at-bus-airflow-server): Airflow server for orchestrating the ELT pipeline (Ansible).
- [at-bus-infrastructure](https://github.com/Philippe-Neveux/at-bus-infrastructure): Infrastructure repository for managing the infrastructure of the project (Terraform).
 
![at-bus-architecture](./docs/at-bus_infra-drawio.png)

---

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