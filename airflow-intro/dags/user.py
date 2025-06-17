from airflow.sdk import asset, Asset, Context

# context lets us grab the xcom


@asset(schedule="@daily", uri="https://randomuser.me/api/")
def user(self) -> dict[str]:
    import requests

    r = requests.get(self.uri)
    return r.json()


# don't need to call it explicitly like a dag


# extracts location of the fake user that is passed through last asset
@asset(schedule=user)  # will materialize when user materailizes
def user_location(user: Asset, context: Context) -> dict[str]:
    # fmt: off
    user_data = context["ti"].xcom_pull(
        dag_id=user.name, 
        task_ids=user.name, 
        include_prior_dates=True
    )

    return user_data['results'][0]['location']

    # fmt: on


# grabbing login information
@asset(schedule=user)
def user_login(user: Asset, context: Context) -> dict[str]:
    # fmt: off
    user_data = context['ti'].xcom_pull(
        dag_id = user.name, 
        task_ids = user.name, 
        include_prior_dates=True
    )
   
    return user_data['results'][0]['login']

    # fmt: on
