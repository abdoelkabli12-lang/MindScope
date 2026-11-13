# MindScope

MindScope is an end-to-end data science project for exploring student wellbeing
factors and estimating mental-health risk categories with machine learning.

## Streamlit dashboard

With Python 3.14 and the project dependencies installed, run the dashboard from
the repository root:

```powershell
python -m pip install -r requirements.txt
streamlit run app\streamlit_app.py
```

The dashboard includes:

- An overview of risk categories, missing values, and group-level patterns.
- Dataset filters, a searchable record table, summary statistics, and CSV export.
- Wellbeing charts and numeric-feature correlations.
- Holdout evaluation and model comparison for logistic regression, random forest,
  and Gaussian naive Bayes.
- An interactive risk-category estimate using the project logistic-regression
  pipeline.

The dashboard uses `data/processed/cleaned_dataset.csv` by default when it is
available, otherwise it uses `data/raw/student_mental_health.csv`. A compatible
CSV can also be uploaded in the sidebar. Uploaded files must include the
project's 17 columns and use the categorical values expected by the existing
preprocessing pipeline.

The risk estimate is a research/demo output, not a diagnosis or substitute for
professional care. The model excludes age and gender, and dashboard filters do
not affect model training or holdout evaluation.

## Airflow with Docker Compose

The Airflow setup uses the [official Airflow 3.4.0 Docker Compose quick-start](https://airflow.apache.org/docs/apache-airflow/3.4.0/howto/docker-compose/index.html).
Its Compose file is included as `docker-compose.yaml`; the local image extends
the official Python 3.14 Airflow image with the project's modeling and dashboard
dependencies. This setup is for local learning and development, not production.

From PowerShell at the repository root, create the Airflow folders and local
environment file:

```powershell
New-Item -ItemType Directory -Force dags, logs, plugins, config, data\raw, data\processed, models | Out-Null
$fernetKey = & .\.venv\Scripts\python.exe -c "import base64, secrets; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"
$envLines = Get-Content .env.example | ForEach-Object { if ($_ -eq "FERNET_KEY=") { "FERNET_KEY=$fernetKey" } else { $_ } }
[System.IO.File]::WriteAllLines((Join-Path $PWD ".env"), [string[]]$envLines)
```

Build the customized image, initialize Airflow, then start the services:

```powershell
docker compose build
docker compose up airflow-init
docker compose up -d
```

Open [http://localhost:8080](http://localhost:8080) and sign in with the
development account `airflow` / `airflow`. Stop the services with
`docker compose down`. The `dags`, `logs`, `plugins`, and `config` directories
are mounted from the repository; the DAG reads
`data/raw/student_mental_health.csv` and writes the cleaned data and IQR outlier
report to `data/processed`. The trained pipeline and evaluation report are
written to `models/`. Unpause `mindscope_pipeline` in the Airflow UI to enable
its daily schedule, or trigger it manually. Do not commit `.env`; it contains a local Fernet key.
The example creates an administrator with a default development password, so
do not expose this setup to an untrusted network.
