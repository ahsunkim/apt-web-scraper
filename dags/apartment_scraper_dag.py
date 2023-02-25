from datetime import timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'apartment_scraper',
    default_args=default_args,
    description='Scrapes apartment rent listings and stores them in a PostgreSQL database',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(1),
    tags=['apartment-scraper'],
)

run_scraper = BashOperator(
    task_id='run_scraper',
    bash_command='python3 ../apartment_scraper.py',
    dag=dag,
)

run_scraper
