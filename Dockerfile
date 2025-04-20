FROM apache/airflow:2.10.4

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    python3-distutils \
    build-essential \
    libpq-dev \
    && apt-get clean

USER airflow

COPY --chown=airflow:airflow requirements.txt .
RUN pip install -r requirements.txt

RUN pip install dbt-postgres==1.7.4
