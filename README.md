# Drift Monitoring Backend

A backend server to allow users to store drift jobs and information for
monitoring.

Before starting the server, you need to generate the following secrets
on `/secrets` folder:

- app_database_password: Mongo database password.

# Development

A Flask API that handles drift run data and job status.
Contains swagger documentation (openapi 3.1) for above APIs.
Saves drift run data to a MongoDB database.
Provides endpoints for saving job status and get data with multiple filters.

- [ ] Add sentry_sdk for error tracking:
      https://flask.palletsprojects.com/en/2.3.x/errorhandling/#error-logging-tools

Create a conda environment, make sure conda is installed
(https://conda.io/docs/user-guide/install/):

```bash
$ conda create --name drift-run python=3.11
$ conda activate drift-run
$ pip install -r requirements.txt
$ pip install -r requirements-dev.txt
$ pip install -r requirements-test.txt
```

To run and debug the backend in local, you can use the following command:

```bash
export FLASK_APP=backend/autoapp:app
python -m flask run <args>
```

You will need to export to the environment the application required variables,
see the file `.env.sample` for the required variables. Additionally you can create
your `.env` file and launch the application using the vscode debugger
configuration at `.vscode/launch.json`.

For testing you need a database running to run the tests, you can use the following
commands to run bring up the database and then run the tests:

```bash
$ docker run --name drift-database -p 27017:27017 -d mongo:6.0.3
```

# Testing

The repository is configure so vscode can locate the tests and run them using the debugger.
To obtain the test plan you can use the following command:

```bash
python -m pytest --setup-plan tests
```

To run tests you can simply run:

```bash
$ python -m pytest -x -n=auto tests
```
