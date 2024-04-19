# Scaleway Consumption Metrics Exporter

This Python script fetches consumption metrics from the Scaleway API and exposes them as Prometheus metrics. It periodically retrieves consumption data for various categories, projects, and months, and exposes them via an HTTP server for Prometheus scraping.

## Requirements

- Python 3.x
- `requests` library
- `prometheus_client` library

## Setup

1. Install the required Python libraries:

pip install requests prometheus_client

2. Set up environment variables for authentication:

export SCW_SECRET_KEY=your_scaleway_secret_key
export SCW_ORGANIZATION_ID=your_scaleway_organization_id

Replace `your_scaleway_secret_key` and `your_scaleway_organization_id` with your actual Scaleway API credentials.

## Usage

1. Run the Python script:

python scaleway_consumption_metrics.py

2. Access the Prometheus metrics at `http://localhost:8000/metrics`.

## Metrics

The script exposes the following Prometheus metrics:

- `scaleway_consumption_total`: Total consumption for the current month.
- `scaleway_consumption_category`: Consumption for a specific category, with labels for category, project ID, and project name.
- `scaleway_consumption_month`: Consumption for a specific month, with labels for month, project ID, and project name.
- `scaleway_consumption_project`: Consumption for a specific project, with labels for project ID and project name.
- `scaleway_consumption_total_projects`: Total consumption across all projects.

## License

This script is released under the MIT License. See [LICENSE](LICENSE) for more information.
