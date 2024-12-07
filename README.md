# Airflow ETL Pipeline

Welcome our Airflow ETL Pipeline project! This project demonstrates how to use Apache Airflow to orchestrate and manage complex ETL (Extract, Transform, Load) workflows. The pipeline integrates two datasets from Kaggle, processes the data, and stores the results in a PostgreSQL database.

## Features

- **Data Integration**: Combine data from multiple sources.
- **Data Cleaning**: Clean and preprocess data to ensure quality.
- **Data Transformation**: Transform data to the desired format.
- **Data Loading**: Load the processed data into a PostgreSQL database.
- **Resource Management**: Efficiently manage resources using Docker and Docker Compose.

## Prerequisites

- Docker
- Docker Compose
- Kaggle API credentials

## Setup Instructions

### Clone the repository

To clone the repository, run the following command:

```bash
git clone https://github.com/taliff0001/cs_440_airflow_etl_pipeline_project.git
cd cs_440_airflow_etl_pipeline_project
```

#### *Run the bash commands in* `docker_cleanup.md` *to remove all Docker containers, disconnected resources* *(volumes and networks), and images for a clean install (optional).*

---

### Set the Airflow home directory

```bash
export AIRFLOW_HOME=$(pwd)
```

### Create the Airflow configuration file and initialize the metadata database

```bash
docker-compose run airflow airflow db init
```

### Create an admin user

```bash
docker-compose run airflow airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin
```

### Start the Airflow services

```bash
docker-compose up -d
```

### Reset the Airflow services

```bash
docker-compose down && docker-compose up -d --remove-orphans
```

### Access the Airflow web interface to run the pipeline

Open a web browser and navigate to `http://localhost:8080`.

- Username: `admin`
- Password: `admin`

### Stop the Airflow services

```bash
docker-compose down
```
