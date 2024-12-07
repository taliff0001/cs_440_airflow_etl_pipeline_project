FROM apache/airflow:2.6.3

# Switch to root user to install system dependencies
USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Switch back to airflow user
USER airflow

COPY requirements.txt .
RUN python -m pip install --upgrade pip && \
pip install --no-cache-dir -r requirements.txt
