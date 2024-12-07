# Import required modules
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import kaggle
from airflow.operators.python import PythonOperator
from sqlalchemy import create_engine
import pandas as pd
import os


# Define default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='kaggle_dataset_download',
    default_args=default_args,
    description='Downloads datasets from Kaggle',
    schedule_interval=None,  # You can set a schedule or trigger manually
    start_date=datetime(2024, 11, 30),
    catchup=False
) as dag:

    download_climate_change_dataset = BashOperator(
        task_id='download_climate_change_dataset',
        bash_command="""
        cd /opt/airflow/data && \
        kaggle datasets download -d tommyaliff/the-twitter-climate-change-dataset-geocoded --unzip && \
        mv "twitter_with_countries.csv" twitter.csv
        """
    )

    download_world_energy_consumption = BashOperator(
        task_id='download_world_energy_consumption',
        bash_command="""
        cd /opt/airflow/data && \
        kaggle datasets download -d pralabhpoudel/world-energy-consumption --unzip && \
        mv "World Energy Consumption.csv" energy.csv
        """
    )

    def clean_energy_data():  # Remove unused parameter
        energy_data = pd.read_csv('/opt/airflow/data/energy.csv')
        energy_data = energy_data[(energy_data['year'] >= 2008) & (energy_data['year'] <= 2019)]
        energy_data = energy_data[energy_data['country'] != 'ASEAN (Ember)']
        energy_data = energy_data[
            ['country', 'year', 'renewables_share_energy', 'fossil_share_energy', 'primary_energy_consumption']]
        energy_data = energy_data.dropna(subset=['renewables_share_energy', 'fossil_share_energy'], how='all')
        energy_data.to_csv('/opt/airflow/data/energy.csv', index=False)

    def merge_and_store():
        try:
            df1 = pd.read_csv('/opt/airflow/data/energy.csv')
            df2 = pd.read_csv('/opt/airflow/data/twitter.csv')
            merged_df = pd.merge(df1, df2, how='inner', on=['year', 'country'])
            merged_df.to_csv('/opt/airflow/data/merged.csv', index=False)
        except Exception as e:
            print(f"Error merging datasets: {str(e)}")
            raise


    def store_in_postgres():
        try:
            merged_df = pd.read_csv('/opt/airflow/data/merged.csv')
            db_conn = f"postgresql+psycopg2://airflow:airflow@postgres:5432/airflow"
            engine = create_engine(db_conn)
            merged_df.to_sql('merged_data', engine, if_exists='replace', index=False)
            print("Data merged and stored in PostgreSQL.")
        except Exception as e:
            print(f"Error storing data in PostgreSQL: {str(e)}")
            raise


    task_clean_energy_data = PythonOperator(
        task_id='clean_energy_data',
        python_callable=clean_energy_data

    )

    task_merge_datasets = PythonOperator(
        task_id='merge_datasets',
        python_callable=merge_and_store
    )

    task_store_in_postgres = PythonOperator(
        task_id='store_in_postgres',
        python_callable=store_in_postgres
    )

    download_climate_change_dataset >> task_clean_energy_data
    download_world_energy_consumption >> task_clean_energy_data
    task_clean_energy_data >> task_merge_datasets
    task_merge_datasets >> task_store_in_postgres