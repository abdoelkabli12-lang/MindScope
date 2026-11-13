FROM apache/airflow:3.4.0-python3.14

USER airflow

RUN pip install --no-cache-dir \
    "apache-airflow==${AIRFLOW_VERSION}" \
    "matplotlib>=3.11.2" \
    "numpy>=2.5.4" \
    "pandas>=3.1.1" \
    "scikit-learn>=1.9.1" \
    "streamlit>=1.67.0"

COPY --chown=airflow:root src /opt/airflow/src
