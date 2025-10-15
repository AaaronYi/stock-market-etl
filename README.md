# Stock Market ETL Pipeline (Free, Cloud-Native, Automated)

## Overview

This project is a **zero-budget, end-to-end ETL pipeline** that automatically:
- Fetches daily stock market data from the [Alpha Vantage API](https://www.alphavantage.co)
- Loads the data into a Google BigQuery data warehouse (using the free sandbox tier)
- Orchestrates and schedules everything with Apache Airflow, running locally via Docker/Astronomer CLI
- Optionally, can add data quality checks with Great Expectations

**Ideal for learning data engineering, cloud orchestration, and showcasing real-world ETL skills to recruiters.**

---

## Architecture

![etl-diagram](diagram.png) <!-- (Add a diagram if you want) -->

**Pipeline Flow:**
1. **Extract:** Pull equities data from Alpha Vantage (free API, up to 5 calls/min)
2. **Transform:** Clean & structure data in Python (`fetch_and_load.py`)
3. **Load:** Write results to BigQuery's forever-free sandbox
4. **Orchestrate:** Schedule and monitor with Airflow, running in Docker via Astronomer CLI

---

## Prerequisites

- **Windows 10/11** with [WSL2 & Ubuntu](https://learn.microsoft.com/en-us/windows/wsl/)
- **Docker Desktop** (with WSL2 integration enabled)
- **Astronomer CLI** (local Airflow)
- **Google Cloud account** (free, no billing needed for BigQuery Sandbox)
- **Alpha Vantage API Key** (free [here](https://www.alphavantage.co/support/#api-key))

---

## Setup Guide

1. **Enable WSL2 and Install Ubuntu:**  
   See [WSL install docs](https://learn.microsoft.com/en-us/windows/wsl/)

2. **Install Docker Desktop (Windows):**  
   [Download Docker](https://www.docker.com/products/docker-desktop/) and enable WSL2 integration for Ubuntu.

3. **Install Astronomer CLI:**  
   In Ubuntu terminal:  
   ```bash
   curl -sSL https://install.astronomer.io | bash
Clone or Create This Repo:

git clone <this-repo>
cd stock_etl
astro dev init
Place Your Files:

fetch_and_load.py → dags/

Copy your Google credentials:

mkdir -p include/credentials
cp /mnt/c/Users/<YourName>/AppData/Roaming/gcloud/application_default_credentials.json include/credentials/adc.json
requirements.txt should include:

requests
google-cloud-bigquery
Edit/Create DAG:

dags/stock_dag.py — see code in this repo.

Start Airflow:


astro dev start --no-cache
Access Airflow at http://localhost:8080 (login: admin/admin).

Set Alpha Vantage API Key:

Airflow UI → Admin → Variables

Key: alpha_vantage_key

Value: <your-api-key>

Run the DAG:

Toggle on, trigger, and check logs/status.

Verify in BigQuery:

Check that rows are landing in your dataset/table.

File Structure
stock_etl/
├── dags/
│   ├── fetch_and_load.py
│   └── stock_dag.py
├── include/
│   └── credentials/
│       └── adc.json
├── requirements.txt
├── Dockerfile
├── airflow_settings.yaml
├── README.md
└── ...
Customization
Add more stocks: Edit the symbols in fetch_and_load.py

Data quality checks: Integrate Great Expectations or add Pandas assertions

Deduplication: Add a BigQuery query or logic to keep only the latest record per day/symbol

Visualization: Connect Google Data Studio or build a Streamlit dashboard

Credits & License
Built by [Your Name]

Free API via Alpha Vantage

Astronomer for local Airflow dev

Recruiter Notes
This pipeline demonstrates skills in Python, APIs, cloud data warehouses, Airflow orchestration, Docker, and end-to-end automation.

Troubleshooting
BigQuery import errors: Check that google-cloud-bigquery is in requirements.txt and restart with astro dev start --no-cache

Credentials errors: Ensure adc.json is in include/credentials/ and your DAG's path matches /usr/local/airflow/include/credentials/adc.json

Docker issues: Confirm Docker Desktop is running and WSL2 integration is enabled

