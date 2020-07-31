# Setup

1. Create a conda environment by using environment.yml
2. In the environment, install airflow with pip by using requirements.txt

The reason to use pip for airflow is that the version in Conda repos is buggy and not the latest one (latest version as of June 21, 2020 is 1.10.11).

# Dependencies

1. Python 3 
2. Various Python libraries found in environment.yml (install with conda)
3. Airflow (install with pip install -r requeriments.txt)
4. Docker and Docker-compose
5. SUMO (only for the netconvert command used in FrigateSimulationSetupOperator)

# Running

0. Activate the Conda environment "frigate-airflow" with environment.yml

1. Create PostgreSQL user "root" passwd "root" and database "airflow"

```
createuser --encrypted --pwprompt root
createdb --owner=root airflow
```

TODO: double check this. Reference: https://gist.github.com/gwangjinkim/f13bf596fefa7db7d31c22efd1627c7a

2. Change to the airflow directory of Frigate.

3. Set the env variable for the Airflow folder:

```
export AIRFLOW_HOME="$(pwd)"
export AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://root:alberto@localhost:5432/airflow
export POSTGRES_USER=root
export POSTGRES_PASSWORD=root
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=airflow
export AIRFLOW__CORE__EXECUTOR=LocalExecutor
```

In AIRFLOW__CORE__SQL_ALCHEMY_CONN replace "alberto" with the host username.

4. then run:

```
airflow initdb
```

5. then run the Airflow scheduler:

```
airflow scheduler
```

6. And finally, the Web server

```
airflow webserver --port 8021
```

6. Register the DAGs

The dag's code is located inside the subfolder "dags"

7. Open the Web server to trigger the DAGs
