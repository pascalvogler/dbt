##authentication:

```gcloud auth application-default login --scopes=https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/bigquery```

##example call:

faking a call to the flask app on windows
```bash
curl -X POST http://localhost:8080 -H "Content-Type: application/json" -d "{\"dbt_command\":{\"run\":{\"--target\": \"prod_eu\", \"--select\": \"tag:a\"}}}"
```
on console:
```bash
dbt run --target prod_eu --select tag:a --profiles-dir .
```

##Overall logic

Via workflows each call must contain a target (see below) and a select. The target is used to determine the Location and the Select is freely determining which models are run. 

##--select:
The --select flag accepts one or more arguments. Each argument can be one of:
1) a package name
2) a model name
3) a fully-qualified path to a directory of models
4) a selection method (path:, tag:, config:, test_type:, test_name:)

examples:

| Example call | Effect |
| ------ | ------ |
| ```dbt run --select my_dbt_project_name``` | runs all models in your project |
| ```dbt run --select my_dbt_model``` | runs a specific model |
| ```dbt run --select path.to.my.models``` | runs all models in a specific directory |
| ```dbt run --select my_package.some_model``` | run a specific model in a specific package |
| ```dbt run --select tag:nightly``` | run models with the "nightly" tag |
| ```dbt run --select path/to/models``` | run models contained in path/to/models |
| ```dbt run --select path/to/my_model.sql``` | run a specific model by its path |

##--target:
There are only 4 targets:

| Target | Description |
| ------ | ------ |
| prod_eu | Main target for all PROD runs in Region ```EU``` in the main BQ project (fallback schema: ```dbt_prod_eu```)|
| prod_us |  Main target for all PROD runs in Region ```US``` in the main BQ project (fallback schema: ```dbt_prod_us```) |
| dev_eu | Main target for all DEV runs in Region ```EU```<br />2 Options:<br />- same schema logic and separate mirror BQ project<br />- Same BQ project but all custom schema names have a dev suffix (e.g. ```customer_db_dev_eu```) |
| dev_us | Main target for all DEV runs in Region ```US```<br />2 Options:<br />- same schema logic and separate mirror BQ project<br />- Same BQ project but all custom schema names have a dev suffix (e.g. ```customer_db_dev_us```) |