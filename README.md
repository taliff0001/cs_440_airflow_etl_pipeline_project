
# Airflow ETL Pipeline

Welcome to our Airflow ETL Pipeline project! This project demonstrates how to use Apache Airflow to orchestrate and manage complex ETL (Extract, Transform, Load) workflows. The pipeline integrates two datasets from Kaggle, processes the data, and stores the results in a PostgreSQL database.

## YouTube Demo

Check out the demo of this project [here](https://www.youtube.com/watch?v=nFSXnFCr-gc).

## Features

- **Data Integration**: Combine data from various sources.
- **Data Cleaning**: Clean and preprocess data to ensure quality.
- **Data Transformation**: Transform data to the desired format.
- **Data Loading**: Load the processed data into a PostgreSQL database.
- **Resource Management**: Efficiently manage resources using Docker and Docker Compose.

## Prerequisites

- Docker
- Docker Compose
- Kaggle API credentials
- Python (for generating the Fernet key)

## Setup Instructions

### Clone the Repository

```bash
git clone https://github.com/taliff0001/cs_440_airflow_etl_pipeline_project.git
```

```bash
cd cs_440_airflow_etl_pipeline_project
```
### Set the Airflow Home Directory

```bash
export AIRFLOW_HOME=$(pwd)
```

### Configure the `.env` File

1. Create a `.env` file in the root directory of the project
2. Add your Kaggle API credentials to the `.env` file:

```env
K_USER=your_kaggle_username
K_KEY=your_kaggle_key
```

### Generate a Fernet Key for the `.env` File

Airflow uses a Fernet key to encrypt sensitive data in its database (e.g., connection passwords). Generate a Fernet key as follows:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Add the generated key to the `.env` file:

```env
FERNET_KEY=your_generated_fernet_key
```

Create a new directory in the root of the project for data, and one for logs (They are defined in the YAML so airflow expects them to be there)

```bash
mkdir data && mkdir logs
```

### Initialize the Airflow Metadata Database

Run the following command to initialize the Airflow metadata database:

```bash
docker-compose run airflow airflow db init
```

### Create an Airflow Admin User

Create an admin user for accessing the Airflow web interface:

```bash
docker-compose run airflow airflow users create     --username admin     --firstname Admin     --lastname User     --role Admin     --email admin@example.com     --password admin
```

### Start the Airflow Services

```bash
docker-compose up -d
```

### Access the Airflow Web Interface

Open a web browser and navigate to `http://localhost:8080` to access the web interface and run the DAG.

- Username: `admin`
- Password: `admin`

### Reset the Airflow Services (Optional)

If you encounter issues or need to reset the environment:

```bash
docker-compose down && docker-compose up -d --remove-orphans
```

### Stop the Airflow Services

```bash
docker-compose down
```

## Optional: Clean Up Docker Resources

For a fresh start, you can remove all Docker containers, disconnected resources (volumes and networks), and images by running the bash commands in `docker_cleanup.md`.

---


## Accessing the PostgreSQL Database

Once the DAG has been successfully executed and data has been loaded into the PostgreSQL database, you can log into the PostgreSQL container to inspect the data.

- Access the database:
   ```bash
   docker exec -it postgres psql -U airflow -d airflow
   ```

- Run SQL queries to inspect the data. For example:
   ```sql
   SELECT * FROM merged_data LIMIT 10;
   ```

- Exit the PostgreSQL shell:
   ```sql
   \q
   ```

- Exit the container:
   ```bash
   exit
   ```

---

