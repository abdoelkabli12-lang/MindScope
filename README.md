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
