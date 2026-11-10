
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration
DATA_PATH = "data/raw/student_mental_health.csv"
TARGET = "Mental_Health_Risk"
ID = "Student_ID"

sns.set_theme(style="whitegrid")

# Load dataset
df = pd.read_csv(DATA_PATH)

numerical = df.select_dtypes(include="number").columns.tolist()

categorical = df.select_dtypes(include=["object", "category"]).columns.drop(
    [ID, TARGET], errors="ignore"
).tolist()

ordinal = ["Year_of_Study", "Physical_Activity", "Diet_Quality"]

print("Dataset shape:", df.shape)
print("\nDataset preview:")
print(df.head())

# 1. Data quality analysis
def data_quality(df):
    print("\n--- DATA QUALITY ---")

    print("\nData types:")
    print(df.dtypes)

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nMissing percentages:")
    print((df.isnull().mean() * 100).round(2))

    print("\nDuplicate rows:", df.duplicated().sum())

    if ID in df.columns:
        print("Duplicate IDs:", df[ID].duplicated().sum())
        print("Missing IDs:", df[ID].isnull().sum())

    # Missing values visualization
    plt.figure(figsize=(12, 5))
    sns.heatmap(df.isnull(), cbar=False, yticklabels=False)
    plt.title("Missing Values Matrix")
    plt.tight_layout()
    plt.show()

    # Missing percentage per column
    missing = df.isnull().mean().mul(100)
    missing = missing[missing > 0].sort_values(ascending=False)

    if not missing.empty:
        missing.plot(kind="bar", figsize=(10, 5))
        plt.title("Missing Values per Feature (%)")
        plt.ylabel("Missing Percentage")
        plt.tight_layout()
        plt.show()


# 2. Descriptive statistics
def descriptive_statistics(df):
    print("\n--- DESCRIPTIVE STATISTICS ---")

    print("\nNumerical features:")
    print(df.describe().T)

    print("\nCategorical features:")
    print(df.describe(include=["object", "category"]).T)


# 3. Univariate analysis
def numerical_distributions(df, columns):
    print("\n--- NUMERICAL DISTRIBUTIONS ---")

    for col in columns:
        fig, axes = plt.subplots(1, 2, figsize=(11, 4))

        sns.histplot(df[col].dropna(), kde=True, ax=axes[0])
        axes[0].set_title(f"Distribution of {col}")

        sns.boxplot(x=df[col], ax=axes[1])
        axes[1].set_title(f"Boxplot of {col}")

        plt.tight_layout()
        plt.show()


def categorical_distributions(df, columns):
    print("\n--- CATEGORICAL DISTRIBUTIONS ---")

    for col in columns:
        plt.figure(figsize=(7, 4))
        sns.countplot(data=df, x=col, order=df[col].value_counts().index)
        plt.title(f"Distribution of {col}")
        plt.xticks(rotation=30)
        plt.tight_layout()
        plt.show()


# 4. Target analysis
def target_distribution(df):
    print("\n--- TARGET DISTRIBUTION ---")

    print(df[TARGET].value_counts())
    print("\nPercentages:")
    print(df[TARGET].value_counts(normalize=True).mul(100).round(2))

    plt.figure(figsize=(7, 4))
    sns.countplot(data=df, x=TARGET, order=["Low", "Medium", "High"])
    plt.title("Mental Health Risk Distribution")
    plt.tight_layout()
    plt.show()


# 5. Outlier detection using IQR
def detect_outliers(df, columns):
    print("\n--- OUTLIER DETECTION ---")

    for col in columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outliers = df[col][(df[col] < lower) | (df[col] > upper)]

        print(f"{col}: {len(outliers)} potential outliers")

        plt.figure(figsize=(7, 3))
        sns.boxplot(x=df[col])
        plt.title(f"Outliers in {col}")
        plt.tight_layout()
        plt.show()


# 6. Correlation analysis
def correlation_analysis(df, columns):
    print("\n--- CORRELATION ANALYSIS ---")

    corr = df[columns].corr()

    plt.figure(figsize=(11, 8))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Numerical Feature Correlation Matrix")
    plt.tight_layout()
    plt.show()


# 7. Numerical features vs target
def numerical_vs_target(df, columns):
    print("\n--- NUMERICAL FEATURES VS TARGET ---")

    for col in columns:
        plt.figure(figsize=(7, 4))
        sns.boxplot(data=df, x=TARGET, y=col,
                    order=["Low", "Medium", "High"])
        plt.title(f"{col} vs {TARGET}")
        plt.tight_layout()
        plt.show()


# 8. Categorical features vs target
def categorical_vs_target(df, columns):
    print("\n--- CATEGORICAL FEATURES VS TARGET ---")

    for col in columns:
        table = pd.crosstab(
            df[col], df[TARGET], normalize="index"
        ) * 100

        print(f"\n{col} vs {TARGET}:")
        print(table.round(2))

        table.plot(kind="bar", stacked=True, figsize=(8, 4))
        plt.title(f"{col} vs {TARGET}")
        plt.ylabel("Percentage")
        plt.tight_layout()
        plt.show()


# 9. Run complete EDA
def run_eda(df):
    data_quality(df)
    descriptive_statistics(df)
    numerical_distributions(df, numerical)
    categorical_distributions(df, categorical + ordinal)
    target_distribution(df)
    detect_outliers(df, numerical)
    correlation_analysis(df, numerical)
    numerical_vs_target(df, numerical)
    categorical_vs_target(df, categorical + ordinal)

    print("\nEDA COMPLETED.")


if __name__ == "__main__":
    run_eda(df)
