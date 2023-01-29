# copy in the latest dbt cli container
FROM ghcr.io/dbt-labs/dbt-bigquery:1.4.0
USER root
ENV APP_HOME /app
ENV PORT 8080
WORKDIR $APP_HOME
COPY . .

RUN python3 -m venv /server-env
# since every run command is a separate process it needs to be chained to be installed
# in virtual env
RUN . /server-env/bin/activate && pip install -r requirements.txt && dbt deps

# Copy local code to the container image.
ENV PYTHONFAULTHANDLER True
# COPY . ./

# Run the web service on container startup.
# Use gunicorn webserver with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
ENTRYPOINT . /server-env/bin/activate && gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app