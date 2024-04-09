from airflow import DAG, Dataset
from airflow.decorators import task

from datetime import datetime

my_file = Dataset("/tmp/my_file.txt")

with DAG(
    dag_id="consumer",
    # as soon as the task in producer DAG updates the dataset,
    # it triggers the consumer DAG.
    schedule=[my_file],
    start_date=datetime(2024, 1, 1),
    # compare catchup with backfill parameter (also the max_active_runs)
    catchup=False,
):

    @task
    def read_dataset():
        with open(my_file.uri, "r") as f:
            print(f.read())

    read_dataset()
