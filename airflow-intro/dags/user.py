from airflow.sdk import asset, Asset, Context

# context lets us grab the xcom


@asset(schedule="@daily", uri="https://randomuser.me/api/")
def user(self) -> dict[str]:
    import requests

    r = requests.get(self.uri)
    return r.json()


# don't need to call it explicitly like a dag

# fmt: off
@asset.multi(
        outlets=[
            Asset(name="user_location"), Asset(name="user_login")
        ], 
        schedule=user
)
def user_info(user: Asset, context: Context) -> list[dict[str]]:
    # fmt: off
    user_data = context["ti"].xcom_pull(
        dag_id=user.name, 
        task_ids=user.name, 
        include_prior_dates=True
    )
     
    return [
         user_data['results'][0]['location'], 
         user_data['results'][0]['login']
    ]
# fmt: on
