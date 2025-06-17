from airflow.sdk import dag, task
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

# sensors check if something is true (if API is availible for example), true means sucess
from airflow.sdk.bases.sensor import PokeReturnValue


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


# need to call or else you wont' see it on airflow UI
user_processing()
