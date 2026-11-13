import pandas as pd
import joblib
from pathlib import Path


from sklearn.model_selection import train_test_split
from src.preprocessing.pipeline import (
    split_features_target,
    build_preprocessor
)
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, roc_auc_score, recall_score, classification_report
from sklearn.model_selection import cross_validate, GridSearchCV, RandomizedSearchCV, StratifiedKFold


def prepare_training_data():
    df = pd.read_csv("data/processed/cleaned_dataset.csv")

    X, y = split_features_target(df)

    x_train, x_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        shuffle=True,
        stratify=y,
        random_state=42
    )

    nb_preprocessor = build_preprocessor(X)
    lgr_preprocessor = build_preprocessor(X)
    rf_preprocessor = build_preprocessor(X)

    return x_train, x_test, y_train, y_test, nb_preprocessor, lgr_preprocessor, rf_preprocessor

x_train, x_test, y_train, y_test, nb_preprocessor, lgr_preprocessor, rf_preprocessor = prepare_training_data()


gaussianNB_pipeline = Pipeline([
  ("preprocessor", nb_preprocessor),
  ("model", GaussianNB(
  ))
])

lgr_pipeline = Pipeline([
  ("preprocessor", lgr_preprocessor),
  ("model", LogisticRegression(
    random_state=42,
    max_iter=400,
  ))
])

rf_pipeline = Pipeline([
  ("preprocessor", rf_preprocessor),
  ("model", RandomForestClassifier(
    criterion="entropy",
    bootstrap=True,
    max_depth=2,
    min_samples_leaf=2,
    min_samples_split=4,
    max_features=6,
    random_state=42,
  ))
])

gaussianNB = gaussianNB_pipeline.fit(x_train, y_train)
lgr = lgr_pipeline.fit(x_train, y_train)
rf = rf_pipeline.fit(x_train, y_train)

y_pred_nb = gaussianNB_pipeline.predict(x_test)

y_pred_lr = lgr_pipeline.predict(x_test)

y_pred_rf = rf_pipeline.predict(x_test)

print("\n==================")
print("Gaussian Bayes   ")
print("==================")
print("Accuracy: ", accuracy_score(y_test, y_pred_nb))
print("F1 score: ", f1_score(y_test, y_pred_nb, average="macro"))
print("Precision: ", precision_score(y_test, y_pred_nb, average="macro"))
print("Recall: ", recall_score(y_test, y_pred_nb, average="macro"))

print("\n==================")
print("Logistic Regression   ")
print("==================")
print("Accuracy: ", accuracy_score(y_test, y_pred_lr))
print("F1 score: ", f1_score(y_test, y_pred_lr, average="macro"))
print("Precision: ", precision_score(y_test, y_pred_lr, average="macro"))
print("Recall: ", recall_score(y_test, y_pred_lr, average="macro"))

print("\n==================")
print("Random Forest   ")
print("==================")
print("Accuracy: ",accuracy_score(y_test, y_pred_rf))
print("F1 score: ", f1_score(y_test, y_pred_rf, average="macro"))
print("Precision: ", precision_score(y_test, y_pred_rf, average="macro"))
print("Recall: ", recall_score(y_test, y_pred_rf, average="macro"))


stratified_Kfolds = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

nb_cv = cross_validate(gaussianNB_pipeline, x_train, y_train, cv=stratified_Kfolds, scoring=["accuracy", "f1_macro", "precision_macro", "recall_macro"])
lr_cv = cross_validate(lgr_pipeline, x_train, y_train, cv=stratified_Kfolds, scoring=["accuracy", "f1_macro", "precision_macro", "recall_macro"])
rf_cv = cross_validate(rf_pipeline, x_train, y_train, cv=stratified_Kfolds, scoring=["accuracy", "f1_macro", "precision_macro", "recall_macro"])

metrics = ["accuracy", "f1_macro", "precision_macro", "recall_macro"]

cv_results = {
    "Gaussian Naive Bayes": nb_cv,
    "Logistic Regression": lr_cv,
    "Random Forest": rf_cv
}

for model_name, results in cv_results.items():
    print(f"\n========== {model_name} ==========")

    for metric in metrics:
        scores = results[f"test_{metric}"]

        print(f"\n{metric}:")
        print("Scores:", scores)
        print("Mean:", scores.mean())
        print("Standard deviation:", scores.std())


print("\n========== LOGISTIC REGRESSION CLASSIFICATION REPORT ==========")
print(classification_report(y_test, y_pred_lr))


# GRID SEARCH IMPLEMENTATION!!

# param_grid = {
#     "model__C": [0.01, 0.1, 0.2, 0.5, 1, 2, 5, 10]
# }

# grid_search = GridSearchCV(
#     estimator=lgr_pipeline,
#     param_grid=param_grid,
#     scoring="f1_macro",
#     cv=stratified_Kfolds,
#     n_jobs=-1,
#     verbose=1
# )

# grid_search.fit(x_train, y_train)

# best_lr_model = grid_search.best_estimator_

# print("\n========== LOGISTIC REGRESSION GRID SEARCH ==========")
# print("Best parameters:", grid_search.best_params_)
# print("Best CV macro F1:", grid_search.best_score_)

# RANDOM SEARCH IMPLEMENTATION!!!

param_distributions = {
  "model__C" : [0.001, 0.01, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100]
}

rand_search = RandomizedSearchCV(
  estimator=lgr_pipeline,
  param_distributions=param_distributions,
  n_iter=12,
  scoring="f1_macro",
  n_jobs=-1,
  cv=stratified_Kfolds,
  random_state=42,
  verbose=1
)

rand_search.fit(x_train, y_train)

best_lr_model = rand_search.best_estimator_

print("\n========== LOGISTIC REGRESSION RANDOMIZED SEARCH ==========")
print("Best parameters:", rand_search.best_params_)
print("Best CV macro F1:", rand_search.best_score_)


y_pred_optimized = best_lr_model.predict(x_test)

baseline_metrics = {
    "Accuracy": accuracy_score(y_test, y_pred_lr),
    "Macro F1": f1_score(y_test, y_pred_lr, average="macro"),
    "Macro Precision": precision_score(y_test, y_pred_lr, average="macro"),
    "Macro Recall": recall_score(y_test, y_pred_lr, average="macro")
}

optimized_metrics = {
    "Accuracy": accuracy_score(y_test, y_pred_optimized),
    "Macro F1": f1_score(y_test, y_pred_optimized, average="macro"),
    "Macro Precision": precision_score(y_test, y_pred_optimized, average="macro"),
    "Macro Recall": recall_score(y_test, y_pred_optimized, average="macro")
}

comparison_df = pd.DataFrame({
    "Baseline Logistic Regression": baseline_metrics,
    "Optimized Logistic Regression": optimized_metrics
})

comparison_df["Improvement"] = (
    comparison_df["Optimized Logistic Regression"]
    - comparison_df["Baseline Logistic Regression"]
)

print("\n========== BASELINE VS OPTIMIZED ==========")
print(comparison_df.round(4))

print("\n========== OPTIMIZED CLASSIFICATION REPORT ==========")
print(classification_report(y_test, y_pred_optimized))

MODEL_PATH = Path("../MindScope/models/mindscope_best_model.pkl")

MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

joblib.dump(best_lr_model, MODEL_PATH)

print(f"Best model saved to: {MODEL_PATH}")