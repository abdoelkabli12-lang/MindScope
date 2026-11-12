
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

DATA_PATH = "data/raw/student_mental_health.csv"
TARGET = "Mental_Health_Risk"

sns.set_theme(style="whitegrid")

df = pd.read_csv(DATA_PATH)



numerical = df.select_dtypes(include="number").columns.tolist()
cetgorical = ['Gender', "Physical_activity", "Diet_Quality"]

# 1. Dataset overview
def dataset_overview(df):
    print("Shape:", df.shape)
    print("\nData types:\n", df.dtypes)
    print("\nMissing values:\n", df.isnull().sum())
    print("\nDuplicate rows:", df.duplicated().sum())
    print("\nStatistics:\n", df.describe())



# 2. Missing values visualization
def missing_values(df):
    missing = df.isnull().sum().sort_values(ascending=False)
    missing = missing[missing > 0]

    missing.plot(kind="bar", figsize=(9, 4))
    plt.title("Missing Values per Feature")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.show()


# 3. Feature distributions
def feature_distributions(df):
    _, axes = plt.subplots(1, 2, figsize=(11, 4))

    sns.histplot(df["Sleep_Hours"].dropna(), kde=True, ax=axes[0])
    axes[0].set_title("Sleep Hours Distribution")

    sns.countplot(data=df, x="Physical_Activity", ax=axes[1])
    axes[1].set_title("Physical Activity Distribution")

    plt.tight_layout()
    plt.show()


# 4. Target distribution
def target_analysis(df):
    print("\nTarget distribution:")
    print(df[TARGET].value_counts(normalize=True).mul(100).round(2))

    sns.countplot(data=df, x=TARGET, order=["Low", "Medium", "High"])
    plt.title("Mental Health Risk Distribution")
    plt.tight_layout()
    plt.show()


# 5. Feature relationships
def feature_relationships(df):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    sns.boxplot(data=df, x=TARGET, y="Sleep_Hours",
                order=["Low", "Medium", "High"], ax=axes[0])
    axes[0].set_title("Sleep Hours vs Mental Health Risk")

    sns.heatmap(df[numerical].corr(), annot=True,
                cmap="coolwarm", fmt=".2f", ax=axes[1])
    axes[1].set_title("Feature Correlations")

    plt.tight_layout()
    plt.show()


# Run EDA
dataset_overview(df)
missing_values(df)
feature_distributions(df)
target_analysis(df)
feature_relationships(df)

print("\nEDA completed.")



