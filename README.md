authentication:

gcloud auth application-default login --scopes=https://www.googleapis.com/auth/drive,https://www.googleapis.com/auth/bigquery

example call:

on windows

curl -X POST http://localhost:8080 -H "Content-Type: application/json" -d "{\"dbt_command\":{\"run\":{\"--target\": \"prod_eu\", \"--select\": \"tag:a\"}}}"
