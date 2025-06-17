from airflow.sdk import dag, task
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

# sensors check if something is true (if API is availible for example), true means sucess
from airflow.sdk.bases.sensor import PokeReturnValue
import requests


@dag
def user_processing():
    # making variable
    create_table = SQLExecuteQueryOperator(  # interacts with sql database
        task_id="create_table",  # what you see in airflow UI
        conn_id="postgres",
        sql=""" 
        create table if not exists users (
            id INT PRIMARY KEY, 
            firstname VARCHAR(255), 
            lastname VARCHAR(255), 
            email VARCHAR(255), 
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
            """,
    )

    # checking condition, 300 is 5 minutes
    @task.sensor(poke_interval=5, timeout=300)
    def is_api_availible() -> PokeReturnValue:
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

    is_api_availible()


# need to call or else you wont' see it on airflow UI
user_processing()
