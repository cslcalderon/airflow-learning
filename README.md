# Apache Airflow Learning Repo 🚀

Welcome to my Airflow learning repository!  
This is a hands-on space where I'm learning how to build and orchestrate data pipelines using **Apache Airflow 3.0.2**, with **Docker**, **VS Code**, and **Python**.

## 🛠️ Tech Stack

- **Airflow**: v3.0.2  
- **Docker**: For containerized development  
- **Python**: DAGs, sensors, assets, and task logic  
- **VS Code**: My primary development environment  
- **PostgreSQL**: Metadata store and database  
- **Celery**: For distributed task execution  
- **LocalExecutor / CeleryExecutor**: For testing queueing and parallel execution  

## 📁 Project Structure

```
.
├── dags/
│   ├── user_processing.py   # My first DAG
│   └── user.py              # Asset-based data processing example
├── docker-compose.yml       # Docker environment for Airflow + Postgres
├── requirements.txt         # Python dependencies
├── airflow.cfg              # Optional: custom Airflow config
└── README.md                # You are here :)
```

## 📄 DAGs in This Repo

### ✅ `user_processing.py`
- My first DAG built using `@dag` and `@task` decorators.
- Includes:
  - Creating a `users` table in PostgreSQL
  - Sensor to check API availability
  - Extract → Process → Load pipeline using temporary CSV
  - Demonstrates task chaining and dependency management

### ✅ `user.py`
- Demonstrates Airflow **assets**
- Uses `@asset(schedule=...)` for declarative scheduling
- Simulates extracting structured data from an API (randomuser)

## ⚙️ Features I’m Exploring

- [x] Writing DAGs using Python  
- [x] Using `@task` and `@task.sensor` decorators  
- [x] Using `@asset` from the new asset-based API  
- [x] Using **Docker Compose** to run Airflow locally  
- [x] Managing workflows via the **Airflow UI**  
- [x] Parallel task execution with **CeleryExecutor**  
- [x] Understanding **task queues**  
- [x] Implementing **Task Groups** for DAG organization  
- [ ] Creating dynamic DAGs  
- [ ] Connecting with GCP (BigQuery, GCS)  

## 🐳 Running Locally with Docker

1. Clone the repo:
    ```bash
    git clone https://github.com/cslcalderon/airflow-learning.git
    cd airflow-learning
    ```

2. Start the Airflow environment:
    ```bash
    docker compose up
    ```

3. Access the Airflow UI at:  
   [http://localhost:8080](http://localhost:8080)

   Default credentials:  
   - **Username**: `airflow`  
   - **Password**: `airflow`

4. To trigger DAGs, either:  
   - Use the Airflow UI  
   - Or run from CLI:
     ```bash
     docker exec -it <webserver_container_name> airflow dags trigger user_processing
     ```

## 💬 Why I’m Doing This

Data engineering is where software meets data at scale.  
As someone with a strong foundation in software engineering and data science, Airflow feels like the perfect bridge to automate, orchestrate, and scale meaningful data workflows.

This repo is my playground to:
- Learn orchestration best practices  
- Understand distributed task execution  
- Optimize end-to-end ETL/ELT pipelines  

## 🚀 What’s Next

This project confirmed something important for me:

> **Data engineering is exactly where I want to go.**

It’s the intersection of everything I care about: automation, optimization, coding, and working with meaningful data.

**Next steps:**

- ✅ Build a more advanced DAG with branching logic  
- ☁️ Integrate with Google Cloud (BigQuery + Cloud Storage)  
- 🔁 Explore `dbt` and `Kafka` for batch and stream processing  
- 🐳 Keep refining my Docker and deployment skills  

## 📚 Resources

- 🎓 [Udemy: The Complete Hands-On Course to Master Apache Airflow](https://www.udemy.com/course/the-complete-hands-on-course-to-master-apache-airflow/)  
- 📖 [Airflow Docs (v3.0+)](https://airflow.apache.org/docs/apache-airflow/stable/index.html)

## 🙋‍♀️ About Me

I'm Sofia Calderon, a data-driven learner passionate about using tech for impact.  
Check out my [GitHub](https://github.com/your-username) or connect with me on [LinkedIn](https://www.linkedin.com/in/your-linkedin/)
