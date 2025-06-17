from airflow.sdk import dag, task
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

# sensors check if something is true (if API is availible for example), true means sucess
from airflow.sdk.bases.sensor import PokeReturnValue

# extract data with python
from airflow.providers.standard.operators.python import PythonOperator

# postgres hook
from airflow.providers.postgres.hooks.postgres import PostgresHook


@dag
def user_processing():
    # making variable
    create_table = SQLExecuteQueryOperator(  # interacts with sql database
        task_id="create_table",  # what you see in airflow UI
        conn_id="postgres",
        sql=""" 
        create table if not exists users (
            id INT PRIMARY KEY, 
            firstName VARCHAR(255), 
            lastName VARCHAR(255), 
            email VARCHAR(255), 
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
            """,
    )

    # checking condition, 300 is 5 minutes
    @task.sensor(poke_interval=5, timeout=300)
    def is_api_availible() -> PokeReturnValue:
        import requests

        response = requests.get(
            "https://raw.githubusercontent.com/marclamberti/datasets/refs/heads/main/fakeuser.json"
        )
        print(response.status_code)
        if response.status_code == 200:
            condition = True
            fake_user = response.json()
        else:
            condition = False
            fake_user = None
        return PokeReturnValue(is_done=condition, xcom_value=fake_user)

    @task
    def extract_user(fake_user):
        return {
            "id": fake_user["id"],
            "firstname": fake_user["personalInfo"]["firstName"],
            "lastname": fake_user["personalInfo"]["lastName"],
            "email": fake_user["personalInfo"]["email"],
        }

    @task
    def process_user(user_info):
        import csv
        from datetime import datetime

        # to simulate run, made user variable
        user_info = {
            "id": 1234,
            "firstname": "Sofia",
            "lastname": "Calderon",
            "email": "cslcalderon@gmail.com",
        }

        user_info["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open("/tmp/user_info.csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=user_info.keys())
            writer.writeheader()
            writer.writerow(user_info)

    @task
    def store_user():
        hook = PostgresHook(postgres_conn_id="postgres")
        # fmt: off
        hook.copy_expert(
            sql="copy users from stdin with csv header", 
            filename="/tmp/user_info.csv"
        )
        # fmt: on

    fake_user = is_api_availible()
    user_info = extract_user(fake_user)
    process_user(user_info)
    store_user()


# need to call or else you wont' see it on airflow UI
user_processing()
