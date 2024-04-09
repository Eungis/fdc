import json
from pandas import json_normalize
from datetime import datetime
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook


def _process_user(ti):
    # task instance
    user = ti.xcom_pull(task_ids="extract_user")
    user = user["results"][0]
    processed_user = json_normalize(
        {
            "firstname": user["name"]["first"],
            "lastname": user["name"]["last"],
            "country": user["location"]["country"],
            "username": user["login"]["username"],
            "password": user["login"]["password"],
            "email": user["email"],
        }
    )
    processed_user.to_csv("/tmp/processed_user.csv", index=None, header=False)


def _store_user():
    # the goal of hook is to abstract all the complexity of interaction
    # behind the scene.
    hook = PostgresHook(postgres_conn_id="postgres")
    hook.copy_expert(sql="COPY users FROM stdin WITH DELIMITER as ','", filename="/tmp/processed_user.csv")


with DAG("user_processing", start_date=datetime(2022, 1, 1), schedule_interval="@daily", catchup=False) as dag:
    create_table = PostgresOperator(
        task_id="create_table",
        postgres_conn_id="postgres",
        sql="""
            CREATE TABLE IF NOT EXISTS users (
                firstname TEXT NOT NULL,
                lastname TEXT NOT NULL,
                country TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                email TEXT NOT NULL
            );
        """,
    )

    # A poke function is called every n seconds to check if the criteria is met.
    # parameters:
    # 1. poke_interval: defaults=60 seconds
    # - the sensor checks if the condition is true or not before executing the next task.
    # 2. timeout: defaults=7 days
    # [Reference] https://wookiist.dev/169

    is_api_available = HttpSensor(
        task_id="is_api_available",
        http_conn_id="user_api",
        # connection host: randomuser.me
        endpoint="api/",
    )

    extract_user = SimpleHttpOperator(
        task_id="extract_user",
        http_conn_id="user_api",
        endpoint="api/",
        method="GET",
        response_filter=lambda response: json.loads(response.text),
        log_response=True,
    )

    process_user = PythonOperator(task_id="process_user", python_callable=_process_user)

    store_user = PythonOperator(task_id="store_user", python_callable=_store_user)

    # Bitshift operator is simply a way to depict dependencies in a more concise way.
    create_table >> is_api_available >> extract_user >> process_user >> store_user
