import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, OrdinalEncoder

def split_features_target(df):
    X = df.drop(columns=["Student_ID", "Mental_Health_Risk"])
    y = df["Mental_Health_Risk"]

    return X, y

def build_preprocessor(X):

    num_cols = X.select_dtypes(include="number").columns.to_list()

    ord_cols = [
        "Year_of_Study",
        "Physical_Activity",
        "Diet_Quality"
    ]

    nom_cols = [
        "Gender",
        "Part_Time_Job",
        "Previous_Mental_Health_History"
    ]

    num_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    ord_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OrdinalEncoder(categories=[
            [1, 2, 3, 4, 5],
            ["Low", "Moderate", "High"],
            ["Poor", "Average", "Good"]
        ]))
    ])

    nom_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore"))
    ])

    col_transform = ColumnTransformer([
        ("num", num_pipeline, num_cols),
        ("ord", ord_pipeline, ord_cols),
        ("nom", nom_pipeline, nom_cols)
    ])

    return col_transform