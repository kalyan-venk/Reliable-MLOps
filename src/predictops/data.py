from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "raw" / "telco_customer_churn.csv"
TARGET_COL = "target"
ID_COL = "customerID"


def load_dataset(path: Path = DATA_PATH) -> pd.DataFrame:
    """Load the raw dataset and normalize it to a generic (features..., target) shape."""
    df = pd.read_csv(path)
    df = df.drop(columns=[ID_COL])
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df[TARGET_COL] = (df["Churn"] == "Yes").astype(int)
    df = df.drop(columns=["Churn"])
    return df
