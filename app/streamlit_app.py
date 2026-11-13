from __future__ import annotations

from io import BytesIO
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline

from src.preprocessing.pipeline import build_preprocessor, split_features_target


ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = ROOT / "data" / "raw" / "student_mental_health.csv"
CLEAN_DATA_PATH = ROOT / "data" / "processed" / "cleaned_dataset.csv"
TARGET = "Mental_Health_Risk"
RISK_ORDER = ["Low", "Medium", "High"]
NUMERIC_COLUMNS = [
    "Age",
    "Year_of_Study",
    "Sleep_Hours",
    "Study_Hours_Per_Week",
    "GPA",
    "Social_Media_Hours",
    "Screen_Time_Hours",
    "Financial_Stress",
    "Family_Support",
    "Attendance_Rate",
]
CATEGORICAL_VALUES = {
    "Gender": {"Male", "Female", "Non-binary"},
    "Physical_Activity": {"Low", "Moderate", "High"},
    "Diet_Quality": {"Poor", "Average", "Good"},
    "Part_Time_Job": {"No", "Yes"},
    "Previous_Mental_Health_History": {"No", "Yes"},
}
REQUIRED_COLUMNS = [
    "Student_ID",
    *NUMERIC_COLUMNS,
    "Gender",
    "Physical_Activity",
    "Diet_Quality",
    "Part_Time_Job",
    "Previous_Mental_Health_History",
    TARGET,
]
MODEL_NAMES = [
    "Logistic Regression",
    "Random Forest",
    "Gaussian Naive Bayes",
]


st.set_page_config(
    page_title="MindScope | Student Wellbeing",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_dataset(uploaded_bytes: bytes | None, source_path: str) -> pd.DataFrame:
    if uploaded_bytes is not None:
        return pd.read_csv(BytesIO(uploaded_bytes))
    return pd.read_csv(source_path)


@st.cache_data(show_spinner=False)
def cached_dataset(uploaded_bytes: bytes | None, source_path: str) -> pd.DataFrame:
    return load_dataset(uploaded_bytes, source_path)


def validate_dataset(data: pd.DataFrame) -> list[str]:
    problems: list[str] = []
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing_columns:
        problems.append(f"Required columns are missing: {', '.join(missing_columns)}.")
        return problems

    for column in NUMERIC_COLUMNS:
        numeric_values = pd.to_numeric(data[column], errors="coerce")
        invalid_values = data[column].notna() & numeric_values.isna()
        if invalid_values.any():
            problems.append(
                f"{column} contains {int(invalid_values.sum())} non-numeric value(s)."
            )

    year_values = pd.to_numeric(data["Year_of_Study"], errors="coerce")
    invalid_years = year_values.notna() & ~year_values.isin([1, 2, 3, 4, 5])
    if invalid_years.any():
        problems.append("Year_of_Study values must be between 1 and 5.")

    for column, allowed_values in CATEGORICAL_VALUES.items():
        observed_values = set(data[column].dropna().astype(str).unique())
        unexpected_values = sorted(observed_values - allowed_values)
        if unexpected_values:
            problems.append(
                f"{column} contains unsupported value(s): {', '.join(unexpected_values)}."
            )

    observed_risks = set(data[TARGET].dropna().astype(str).unique())
    unexpected_risks = sorted(observed_risks - set(RISK_ORDER))
    if unexpected_risks:
        problems.append(
            f"{TARGET} contains unsupported value(s): {', '.join(unexpected_risks)}."
        )
    if data[TARGET].isna().any():
        problems.append(f"{TARGET} cannot be missing for model training.")
    if data.empty:
        problems.append("The dataset has no rows.")
    elif data[TARGET].value_counts().reindex(RISK_ORDER, fill_value=0).min() < 2:
        problems.append("Each risk class needs at least two records for a stratified split.")

    return problems


def normalize_numeric_columns(data: pd.DataFrame) -> pd.DataFrame:
    normalized = data.copy()
    for column in NUMERIC_COLUMNS:
        normalized[column] = pd.to_numeric(normalized[column], errors="raise")
    return normalized


def make_model_pipeline(model_name: str, features: pd.DataFrame) -> Pipeline:
    if model_name == "Logistic Regression":
        estimator = LogisticRegression(random_state=42, max_iter=400)
    elif model_name == "Random Forest":
        estimator = RandomForestClassifier(
            criterion="entropy",
            bootstrap=True,
            max_depth=2,
            min_samples_leaf=2,
            min_samples_split=4,
            max_features=6,
            random_state=42,
        )
    elif model_name == "Gaussian Naive Bayes":
        estimator = GaussianNB()
    else:
        raise ValueError(f"Unknown model: {model_name}")

    return Pipeline(
        [
            ("preprocessor", build_preprocessor(features)),
            ("model", estimator),
        ]
    )


@st.cache_resource(show_spinner="Training model on the project dataset...")
def evaluate_model(
    model_name: str, dataset: pd.DataFrame
) -> tuple[Pipeline, pd.DataFrame, pd.Series, np.ndarray]:
    features, target = split_features_target(dataset)
    train_features, test_features, train_target, test_target = train_test_split(
        features,
        target,
        test_size=0.2,
        shuffle=True,
        stratify=target,
        random_state=42,
    )
    model = make_model_pipeline(model_name, train_features)
    model.fit(train_features, train_target)
    predictions = model.predict(test_features)
    return model, test_features, test_target, predictions


@st.cache_resource(show_spinner="Fitting model for the risk check...")
def fit_full_model(model_name: str, dataset: pd.DataFrame) -> Pipeline:
    features, target = split_features_target(dataset)
    model = make_model_pipeline(model_name, features)
    model.fit(features, target)
    return model


def risk_counts(data: pd.DataFrame) -> pd.Series:
    return data[TARGET].value_counts().reindex(RISK_ORDER, fill_value=0)


def render_overview(data: pd.DataFrame, source_label: str) -> None:
    st.title("Student wellbeing at a glance")
    st.caption(
        f"Exploring {len(data):,} records from **{source_label}**. "
        "Use the sidebar to filter the dashboard."
    )

    high_risk_share = data[TARGET].eq("High").mean() * 100 if not data.empty else 0
    missing_cells = int(data.isna().sum().sum())
    students_with_missing = int(data.isna().any(axis=1).sum())
    metric_columns = st.columns(4)
    metric_columns[0].metric("Students in view", f"{len(data):,}")
    metric_columns[1].metric("Features", f"{len(data.columns) - 2}")
    metric_columns[2].metric("High-risk share", f"{high_risk_share:.1f}%")
    metric_columns[3].metric(
        "Rows with missing values", f"{students_with_missing:,}", help=f"{missing_cells:,} missing cells"
    )

    left, right = st.columns(2)
    with left:
        st.subheader("Risk group distribution")
        st.bar_chart(risk_counts(data), color="#6674f5", height=280)
    with right:
        st.subheader("Where values are missing")
        missing_by_column = data.isna().sum().sort_values(ascending=False)
        missing_by_column = missing_by_column[missing_by_column > 0]
        if missing_by_column.empty:
            st.success("No missing values in the current selection.")
        else:
            st.bar_chart(missing_by_column, color="#efaa66", height=280)

    st.subheader("Risk profile by student experience")
    factor = st.selectbox(
        "Compare risk across",
        ["Year_of_Study", "Physical_Activity", "Diet_Quality", "Part_Time_Job"],
        format_func=lambda value: value.replace("_", " "),
        key="overview_factor",
    )
    if data.empty:
        st.info("No records match the current sidebar filters.")
    else:
        risk_by_factor = pd.crosstab(
            data[factor].fillna("Missing"),
            data[TARGET],
            normalize="index",
        ).reindex(columns=RISK_ORDER, fill_value=0)
        risk_by_factor.index.name = factor.replace("_", " ")
        st.bar_chart(risk_by_factor, stack=True, height=320)
        st.caption("Bars show the share of each risk category within a factor group.")

    st.info(
        "Risk categories describe patterns in this dataset; they are not clinical "
        "assessments or diagnoses."
    )


def render_explorer(data: pd.DataFrame) -> None:
    st.title("Explore the dataset")
    st.caption("Filter records in the sidebar, inspect the table, and export the current view.")
    if data.empty:
        st.warning("No records match the current sidebar filters.")
        return

    search = st.text_input("Find a student ID", placeholder="For example, STU0001")
    visible = data
    if search.strip():
        visible = visible[
            visible["Student_ID"].astype(str).str.contains(search.strip(), case=False, na=False)
        ]

    st.caption(f"Showing {len(visible):,} of {len(data):,} filtered records.")
    st.dataframe(visible, width="stretch", hide_index=True)
    st.download_button(
        "Download this view as CSV",
        data=visible.to_csv(index=False).encode("utf-8"),
        file_name="mindscope_filtered_students.csv",
        mime="text/csv",
        width="content",
    )

    st.subheader("Summary statistics")
    numeric_features = [
        column
        for column in NUMERIC_COLUMNS
        if column in visible.columns and column != "Age"
    ]
    st.dataframe(visible[numeric_features].describe().T, width="stretch")


def render_insights(data: pd.DataFrame) -> None:
    st.title("Wellbeing insights")
    st.caption("Explore distributions and relationships in the selected records.")
    if data.empty:
        st.warning("No records match the current sidebar filters.")
        return

    categorical = st.selectbox(
        "Risk profile by factor",
        [
            "Year_of_Study",
            "Physical_Activity",
            "Diet_Quality",
            "Previous_Mental_Health_History",
            "Part_Time_Job",
        ],
        format_func=lambda value: value.replace("_", " "),
    )
    profile = pd.crosstab(
        data[categorical].fillna("Missing"),
        data[TARGET],
        normalize="index",
    ).reindex(columns=RISK_ORDER, fill_value=0)
    profile.index.name = categorical.replace("_", " ")
    st.bar_chart(profile, stack=True, height=320)
    st.caption("Each row is normalized to 100%, making group sizes comparable.")

    measure = st.selectbox(
        "Compare a numeric feature",
        [
            "Sleep_Hours",
            "Study_Hours_Per_Week",
            "GPA",
            "Social_Media_Hours",
            "Screen_Time_Hours",
            "Financial_Stress",
            "Family_Support",
            "Attendance_Rate",
        ],
        format_func=lambda value: value.replace("_", " "),
    )
    average_by_risk = (
        data.groupby(TARGET, observed=False)[measure]
        .mean()
        .reindex(RISK_ORDER)
        .dropna()
    )
    st.subheader(f"Average {measure.replace('_', ' ')} by risk category")
    st.bar_chart(average_by_risk, color="#6674f5", height=260)

    st.subheader("Numeric feature correlations")
    numeric_features = [
        column
        for column in NUMERIC_COLUMNS
        if column in data.columns and column not in {"Age", "Year_of_Study"}
    ]
    correlations = data[numeric_features].corr()
    figure, axis = plt.subplots(figsize=(10, 7))
    image = axis.imshow(correlations, cmap="coolwarm", vmin=-1, vmax=1)
    axis.set_xticks(range(len(numeric_features)), numeric_features, rotation=45, ha="right")
    axis.set_yticks(range(len(numeric_features)), numeric_features)
    axis.set_title("Pearson correlation")
    figure.colorbar(image, ax=axis, fraction=0.046, pad=0.04)
    figure.tight_layout()
    st.pyplot(figure, width="stretch")
    plt.close(figure)
    st.caption("Correlation is descriptive and does not imply causation.")


def model_metrics(
    target: pd.Series, predictions: np.ndarray
) -> dict[str, float]:
    return {
        "Accuracy": accuracy_score(target, predictions),
        "Macro precision": precision_score(
            target, predictions, average="macro", zero_division=0
        ),
        "Macro recall": recall_score(
            target, predictions, average="macro", zero_division=0
        ),
        "Macro F1": f1_score(target, predictions, average="macro", zero_division=0),
    }


def render_model_performance(data: pd.DataFrame) -> None:
    st.title("Model performance")
    st.caption(
        "Models use the project's shared preprocessing pipeline and a stratified "
        "80/20 holdout split (random state 42). Sidebar filters do not alter training."
    )
    selected_model = st.selectbox("Model", MODEL_NAMES)
    compare_models = st.button("Compare all models", type="secondary")

    try:
        model, test_features, test_target, predictions = evaluate_model(
            selected_model, data
        )
    except ValueError as error:
        st.error(f"Could not evaluate {selected_model}: {error}")
        return

    metrics = model_metrics(test_target, predictions)
    metric_columns = st.columns(len(metrics))
    for column, (name, value) in zip(metric_columns, metrics.items()):
        column.metric(name, f"{value:.1%}")

    report = classification_report(
        test_target,
        predictions,
        labels=RISK_ORDER,
        output_dict=True,
        zero_division=0,
    )
    left, right = st.columns(2)
    with left:
        st.subheader("Confusion matrix")
        matrix = confusion_matrix(test_target, predictions, labels=RISK_ORDER)
        st.dataframe(
            pd.DataFrame(
                matrix,
                index=[f"Actual {risk}" for risk in RISK_ORDER],
                columns=[f"Predicted {risk}" for risk in RISK_ORDER],
            ),
            width="stretch",
        )
    with right:
        st.subheader("Per-class report")
        report_frame = pd.DataFrame(report).T.reindex(RISK_ORDER)
        st.dataframe(
            report_frame[["precision", "recall", "f1-score", "support"]].round(3),
            width="stretch",
        )

    estimator = model.named_steps["model"]
    if hasattr(estimator, "feature_importances_") or hasattr(estimator, "coef_"):
        names = model.named_steps["preprocessor"].get_feature_names_out()
        if hasattr(estimator, "feature_importances_"):
            importance = estimator.feature_importances_
            explanation = "Random forest impurity-based importance"
        else:
            importance = np.abs(estimator.coef_).mean(axis=0)
            explanation = "Mean absolute logistic-regression coefficient"
        top_features = (
            pd.Series(importance, index=names)
            .sort_values(ascending=False)
            .head(10)
            .sort_values()
        )
        st.subheader("Most influential model features")
        st.bar_chart(top_features, color="#38a889", height=320)
        st.caption(f"{explanation}; this is model attribution, not causation.")

    prediction_export = pd.DataFrame(
        {
            "Actual": test_target.to_numpy(),
            "Predicted": predictions,
        },
        index=test_features.index,
    )
    st.download_button(
        "Download holdout predictions",
        data=prediction_export.to_csv(index=False).encode("utf-8"),
        file_name=f"mindscope_{selected_model.lower().replace(' ', '_')}_holdout.csv",
        mime="text/csv",
    )

    if compare_models:
        comparison_rows = []
        try:
            for model_name in MODEL_NAMES:
                _, _, model_target, model_predictions = evaluate_model(model_name, data)
                comparison_rows.append(
                    {"Model": model_name, **model_metrics(model_target, model_predictions)}
                )
        except ValueError as error:
            st.error(f"Could not compare models: {error}")
        else:
            st.subheader("Holdout comparison")
            comparison = pd.DataFrame(comparison_rows).set_index("Model")
            st.dataframe(
                comparison.style.format("{:.1%}"),
                width="stretch",
            )
            st.bar_chart(comparison[["Accuracy", "Macro F1"]], height=280)


def numeric_input(
    label: str, default: float, minimum: float, maximum: float, step: float
) -> float:
    minimum = float(minimum)
    maximum = float(maximum)
    step = float(step)
    return st.number_input(
        label,
        min_value=minimum,
        max_value=maximum,
        value=float(np.clip(default, minimum, maximum)),
        step=step,
    )


def render_risk_check(data: pd.DataFrame) -> None:
    st.title("Risk check")
    st.warning(
        "This research/demo model is not a diagnosis or substitute for professional "
        "care. Do not use its estimate to make decisions about an individual."
    )
    st.caption(
        "Enter the 13 features used by the project model. Age and gender are not "
        "included in its predictions."
    )

    form = st.form("risk_check_form")
    with form:
        first_row = st.columns(3)
        year = first_row[0].selectbox("Year of study", [1, 2, 3, 4, 5], index=1)
        physical_activity = first_row[1].selectbox(
            "Physical activity", ["Low", "Moderate", "High"], index=1
        )
        diet_quality = first_row[2].selectbox(
            "Diet quality", ["Poor", "Average", "Good"], index=1
        )

        sleep, study, gpa = st.columns(3)
        with sleep:
            sleep_hours = numeric_input("Sleep hours per day", 6.7, 0, 24, 0.1)
        with study:
            study_hours = numeric_input("Study hours per week", 20, 0, 100, 0.5)
        with gpa:
            grade = numeric_input("GPA", 2.56, 0, 4, 0.01)

        social, screen, financial = st.columns(3)
        with social:
            social_hours = numeric_input("Social media hours per day", 6, 0, 24, 0.1)
        with screen:
            screen_hours = numeric_input("Screen time hours per day", 8.5, 0, 24, 0.1)
        with financial:
            financial_stress = numeric_input("Financial stress (1–10)", 6, 0, 10, 0.1)

        support, attendance, history = st.columns(3)
        with support:
            family_support = numeric_input("Family support (1–10)", 6.5, 0, 10, 0.1)
        with attendance:
            attendance_rate = numeric_input("Attendance rate (%)", 85, 0, 100, 0.5)
        with history:
            previous_history = st.selectbox(
                "Previous mental health history", ["No", "Yes"]
            )

        job = st.selectbox("Part-time job", ["No", "Yes"])
        submitted = st.form_submit_button("Estimate risk category", type="primary")

    if not submitted:
        return

    input_features = pd.DataFrame(
        [
            {
                "Year_of_Study": year,
                "Sleep_Hours": sleep_hours,
                "Study_Hours_Per_Week": study_hours,
                "GPA": grade,
                "Social_Media_Hours": social_hours,
                "Screen_Time_Hours": screen_hours,
                "Physical_Activity": physical_activity,
                "Financial_Stress": financial_stress,
                "Family_Support": family_support,
                "Attendance_Rate": attendance_rate,
                "Part_Time_Job": job,
                "Diet_Quality": diet_quality,
                "Previous_Mental_Health_History": previous_history,
            }
        ]
    )

    try:
        model = fit_full_model("Logistic Regression", data)
    except ValueError as error:
        st.error(f"Could not fit the risk-check model: {error}")
        return

    prediction = str(model.predict(input_features)[0])
    probabilities = model.predict_proba(input_features)[0]
    classes = model.named_steps["model"].classes_
    probability_by_class = dict(zip(classes, probabilities))

    st.subheader("Model estimate")
    st.metric("Estimated category", prediction)
    probability_columns = st.columns(len(RISK_ORDER))
    for column, risk in zip(probability_columns, RISK_ORDER):
        probability = float(probability_by_class.get(risk, 0))
        column.metric(f"{risk} score", f"{probability:.1%}")
        column.progress(probability)
    st.caption(
        "Scores are model probabilities for this input, not calibrated clinical "
        "probabilities or an individual diagnosis."
    )


def main() -> None:
    st.markdown(
        """
        <style>
        .block-container {padding-top: 2rem; padding-bottom: 3rem; max-width: 1440px;}
        [data-testid="stMetric"] {
            background: linear-gradient(135deg, rgba(102,116,245,.10), rgba(56,168,137,.08));
            border: 1px solid rgba(120,130,180,.18);
            padding: 1rem 1.15rem; border-radius: 14px;
        }
        [data-testid="stSidebar"] {border-right: 1px solid rgba(120,130,180,.18);}
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.title("🧭 MindScope")
        st.caption("Student wellbeing analytics")
        source_options: dict[str, Path] = {}
        if RAW_DATA_PATH.exists():
            source_options["Raw dataset"] = RAW_DATA_PATH
        if CLEAN_DATA_PATH.exists():
            source_options["Cleaned dataset"] = CLEAN_DATA_PATH
        if source_options:
            default_source = (
                "Cleaned dataset" if "Cleaned dataset" in source_options else "Raw dataset"
            )
            selected_source = st.selectbox(
                "Dataset source",
                list(source_options),
                index=list(source_options).index(default_source),
            )
            source_path = str(source_options[selected_source])
        else:
            selected_source = None
            source_path = ""
        uploaded_file = st.file_uploader("Or upload a project CSV", type=["csv"])
        uploaded_bytes = uploaded_file.getvalue() if uploaded_file is not None else None
        source_label = (
            uploaded_file.name
            if uploaded_file is not None
            else selected_source or "project dataset"
        )

    if uploaded_bytes is None and not source_path:
        st.error("No project dataset found. Upload a CSV to continue.")
        st.stop()

    try:
        data = cached_dataset(uploaded_bytes, source_path)
    except (OSError, UnicodeDecodeError, pd.errors.ParserError, pd.errors.EmptyDataError) as error:
        st.error(f"Could not read the selected dataset: {error}")
        st.stop()

    problems = validate_dataset(data)
    if problems:
        st.error("The selected CSV does not match the MindScope data contract:")
        for problem in problems:
            st.write(f"- {problem}")
        st.stop()
    data = normalize_numeric_columns(data)

    with st.sidebar:
        st.divider()
        st.subheader("Dashboard filters")
        risk_options = [risk for risk in RISK_ORDER if risk in set(data[TARGET])]
        selected_risks = st.multiselect(
            "Risk category", risk_options, default=risk_options
        )
        years = sorted(data["Year_of_Study"].dropna().unique().tolist())
        selected_years = st.multiselect("Year of study", years, default=years)
        genders = sorted(data["Gender"].dropna().astype(str).unique().tolist())
        selected_genders = st.multiselect("Gender", genders, default=genders)
        st.caption("Filters affect dashboard charts and tables, not model training.")

    filtered_data = data[
        data[TARGET].isin(selected_risks)
        & data["Year_of_Study"].isin(selected_years)
        & data["Gender"].isin(selected_genders)
    ].copy()

    page = st.sidebar.radio(
        "Navigate",
        [
            "Overview",
            "Explore data",
            "Insights",
            "Model performance",
            "Risk check",
        ],
        label_visibility="collapsed",
    )

    if page == "Overview":
        render_overview(filtered_data, source_label)
    elif page == "Explore data":
        render_explorer(filtered_data)
    elif page == "Insights":
        render_insights(filtered_data)
    elif page == "Model performance":
        render_model_performance(data)
    else:
        render_risk_check(data)


if __name__ == "__main__":
    main()
