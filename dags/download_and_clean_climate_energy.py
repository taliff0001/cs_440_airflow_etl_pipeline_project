# Import required modules
from airflow import DAG  # DAG stands for Directed Acyclic Graph and is used to organize tasks in Airflow
from airflow.operators.bash import BashOperator  # BashOperator allows executing bash commands in Airflow
from datetime import datetime, timedelta  # datetime and timedelta are used for handling dates and times
import kaggle  # kaggle is used for interacting with the Kaggle API
from airflow.operators.python import PythonOperator  # PythonOperator allows executing Python functions in Airflow
from sqlalchemy import create_engine  # create_engine is used for connecting to databases
import pandas as pd  # pandas is used for data manipulation and analysis
import os  # os is used for interacting with the operating system


# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',  # The owner of the DAG
    'depends_on_past': False,  # Whether task instances should depend on the success of previous instances
    'email_on_failure': False,  # Whether to send an email on task failure
    'email_on_retry': False,  # Whether to send an email on task retry
    'retries': 1,  # Number of retries before failing the task
    'retry_delay': timedelta(minutes=5),  # Time to wait before retrying a failed task
}

# Define the DAG
with DAG(
    dag_id='kaggle_dataset_download',  # Unique identifier for the DAG
    default_args=default_args,  # Default arguments defined above
    description='Downloads datasets from Kaggle',  # A brief description of the DAG
    schedule_interval=None,  # How often the DAG should run; None means it needs to be triggered manually
    start_date=datetime(2024, 11, 30),  # The start date for the DAG
    catchup=False  # Whether to catch up on missed runs
) as dag:

    # Define a task to download the climate change dataset from Kaggle using BashOperator
    download_climate_change_dataset = BashOperator(
        task_id='download_climate_change_dataset',  # Unique identifier for the task
        bash_command="""
        cd /opt/airflow/data && \
        kaggle datasets download -d tommyaliff/the-twitter-climate-change-dataset-geocoded --unzip && \
        mv "twitter_with_countries.csv" twitter.csv
        """  # Bash command to download and unzip the dataset, then rename the file
    )

    # Define a task to download the world energy consumption dataset from Kaggle using BashOperator
    download_world_energy_consumption = BashOperator(
        task_id='download_world_energy_consumption',  # Unique identifier for the task
        bash_command="""
        cd /opt/airflow/data && \
        kaggle datasets download -d pralabhpoudel/world-energy-consumption --unzip && \
        mv "World Energy Consumption.csv" energy.csv
        """  # Bash command to download and unzip the dataset, then rename the file
    )

    # Define a Python function to clean the energy data
    def clean_energy_data():
        # Read the energy data from a CSV file into a pandas DataFrame
        energy_data = pd.read_csv('/opt/airflow/data/energy.csv')
        # Filter the data to include only the years 2008 to 2019
        energy_data = energy_data[(energy_data['year'] >= 2008) & (energy_data['year'] <= 2019)]
        # Filter out rows where the country is 'ASEAN (Ember)'
        energy_data = energy_data[energy_data['country'] != 'ASEAN (Ember)']
        # Select specific columns from the DataFrame
        energy_data = energy_data[
            ['country', 'year', 'renewables_share_energy', 'fossil_share_energy', 'primary_energy_consumption']]
        # Drop rows where both 'renewables_share_energy' and 'fossil_share_energy' columns are NaN
        energy_data = energy_data.dropna(subset=['renewables_share_energy', 'fossil_share_energy'], how='all')
        # Save the cleaned data back to the CSV file
        energy_data.to_csv('/opt/airflow/data/energy.csv', index=False)

    # Define a Python function to merge the cleaned energy data with the climate change data and store the result
    def merge_and_store():
        try:
            # Read the cleaned energy data and climate change data into pandas DataFrames
            df1 = pd.read_csv('/opt/airflow/data/energy.csv')
            df2 = pd.read_csv('/opt/airflow/data/twitter.csv')
            # Merge the two DataFrames on the 'year' and 'country' columns
            merged_df = pd.merge(df1, df2, how='inner', on=['year', 'country'])
            # Save the merged DataFrame to a CSV file
            merged_df.to_csv('/opt/airflow/data/merged.csv', index=False)
        except Exception as e:
            # Print an error message if something goes wrong
            print(f"Error merging datasets: {str(e)}")
            # Raise the exception to fail the task
            raise


    # Define a Python function to store the merged data in a PostgreSQL database
    def store_in_postgres():
        try:
            # Read the merged data from the CSV file into a pandas DataFrame
            merged_df = pd.read_csv('/opt/airflow/data/merged.csv')
            # Define the connection string for the PostgreSQL database
            db_conn = f"postgresql+psycopg2://airflow:airflow@postgres:5432/airflow"
            # Create a SQLAlchemy engine for connecting to the database
            engine = create_engine(db_conn)
            # Save the merged DataFrame to a table in the PostgreSQL database
            merged_df.to_sql('merged_data', engine, if_exists='replace', index=False)
            # Print a success message
            print("Data merged and stored in PostgreSQL.")
        except Exception as e:
            # Print an error message if something goes wrong
            print(f"Error storing data in PostgreSQL: {str(e)}")
            # Raise the exception to fail the task
            raise


    # Define a task to clean the energy data using PythonOperator
    task_clean_energy_data = PythonOperator(
        task_id='clean_energy_data',  # Unique identifier for the task
        python_callable=clean_energy_data  # The Python function to execute
    )

    # Define a task to merge the datasets using PythonOperator
    task_merge_datasets = PythonOperator(
        task_id='merge_datasets',  # Unique identifier for the task
        python_callable=merge_and_store  # The Python function to execute
    )

    # Define a task to store the merged data in PostgreSQL using PythonOperator
    task_store_in_postgres = PythonOperator(
        task_id='store_in_postgres',  # Unique identifier for the task
        python_callable=store_in_postgres  # The Python function to execute
    )

    # Define the task dependencies
    # The 'clean_energy_data' task depends on the completion of both download tasks
    download_climate_change_dataset >> task_clean_energy_data
    download_world_energy_consumption >> task_clean_energy_data
    # The 'merge_datasets' task depends on the completion of the 'clean_energy_data' task
    task_clean_energy_data >> task_merge_datasets
    # The 'store_in_postgres' task depends on the completion of the 'merge_datasets' task
    task_merge_datasets >> task_store_in_postgres
