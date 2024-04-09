from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.models import TaskInstance

from datetime import datetime

# xcom allows to exchange only small amount of data


def _t1(ti: TaskInstance):
    # when the operator runs, it creates a task instance (ti).
    # default key: return_value
    ti.xcom_push(key="my_key", value=42)

    # What happen when you return a value from a python_callable function?
    # The value will be automatically pushed into a Xcom with default key 'return_value'.
    # if you want to set key by yourself, you have to specify it by yourself as above.


def _t2(ti: TaskInstance):
    # How can I know which XCOM will be pulled out in first if they both have the same key?
    # The Xcom having the most recent execution_date will be pulled out in first by default.
    # if you didn't set the execution_date, then execution_date will be automatically set to the date of the DagRun.

    print(f"pull from t1: {ti.xcom_pull(key='my_key', task_ids='t1')}")


def _branch(ti: TaskInstance):
    value = ti.xcom_pull(key="my_key", task_ids="t1")
    if value == 42:
        return "t2"
    return "t3"


with DAG("xcom_dag", start_date=datetime(2022, 1, 1), schedule_interval="@daily", catchup=False) as dag:
    t1 = PythonOperator(task_id="t1", python_callable=_t1)

    branch = BranchPythonOperator(task_id="branch", python_callable=_branch)

    t2 = PythonOperator(task_id="t2", python_callable=_t2)

    t3 = BashOperator(task_id="t3", bash_command="echo ''")

    t4 = BashOperator(task_id="t4", bash_command="echo ''", trigger_rule="none_failed_min_one_success")

    # # before branch
    # t1 >> t2 >> t3

    # Trigger Rules
    # [t1, t2] >> t3
    # 1. all_success
    # 2. all_failed
    # 3. all_done: regardless of states
    # 4. one_sucess: one of the upstream succeed, tridgger the next task right away, without waiting for the t2.
    # 5. one_failed
    # 6. none_failed: All upstream tasks succeed or skipped.
    # 7. none_failed_min_one_success
    # 8.

    # after branch
    t1 >> branch >> [t2, t3] >> t4
