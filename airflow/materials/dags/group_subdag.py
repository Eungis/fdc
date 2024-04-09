from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.subdag import SubDagOperator

from datetime import datetime
from subdags.subdag_downloads import subdag_downloads
from subdags.subdag_transforms import subdag_transforms

with DAG("group_subdag", start_date=datetime(2022, 1, 1), schedule_interval="@daily", catchup=False) as dag:
    # ---- Before grouped ---- #
    # download_a = BashOperator(
    #     task_id='download_a',
    #     bash_command='sleep 10'
    # )

    # download_b = BashOperator(
    #     task_id='download_b',
    #     bash_command='sleep 10'
    # )

    # download_c = BashOperator(
    #     task_id='download_c',
    #     bash_command='sleep 10'
    # )

    # transform_a = BashOperator(
    #     task_id='transform_a',
    #     bash_command='sleep 10'
    # )

    # transform_b = BashOperator(
    #     task_id='transform_b',
    #     bash_command='sleep 10'
    # )

    # transform_c = BashOperator(
    #     task_id='transform_c',
    #     bash_command='sleep 10'
    # )

    # ---- Use SubDags ---- #
    args = {"start_date": dag.start_date, "schedule_interval": dag.schedule_interval, "catchup": dag.catchup}
    downloads = SubDagOperator(
        task_id="downloads",
        # task_id above and the second parameter, which is used as a parameter of SubDag,
        # must be same. Otherwise it would raise error.
        subdag=subdag_downloads(dag.dag_id, "downloads", args),
    )

    check_files = BashOperator(task_id="check_files", bash_command="sleep 10")

    transforms = SubDagOperator(
        task_id="transforms",
        # task_id above and the second parameter, which is used as a parameter of SubDag,
        # must be same. Otherwise it would raise error.
        subdag=subdag_transforms(dag.dag_id, "transforms", args),
    )

    # [download_a, download_b, download_c] >> check_files >> [transform_a, transform_b, transform_c]
    downloads >> check_files >> transforms
