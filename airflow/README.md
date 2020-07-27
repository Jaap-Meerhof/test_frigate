# Setup

1. Create a conda environment by using environment.yml
2. In the environment, install airflow with pip by using requirements.txt

The reason to use pip for airflow is that the version in Conda repos is buggy and not the latest one (latest version as of June 21, 2020 is 1.10.11).

# Running

1. Change to the airflow directory of Frigate.

2. Set the env variable for the Airflow folder:

```
export AIRFLOW_HOME="$(pwd)"
```

3. then run:

```
airflow initdb
```

4. then run the Airflow scheduler:

```
airflow scheduler
```

5. And finally, the Web server

```
airflow webserver --port 8080
```

The dag's code is located inside the subfolder "dags"
