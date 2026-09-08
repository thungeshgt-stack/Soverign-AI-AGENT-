"""
CSV loading and sensor-data analysis tools using pandas/numpy.
"""
import pandas as pd
from config.settings import SENSOR_THRESHOLDS


def read_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    return df


def analyze_sensor_data(df: pd.DataFrame) -> dict:
    """
    Automatically profile numeric columns, compute basic stats, and flag
    threshold exceedances / possible anomalies using conservative language.
    """
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    missing = df.isna().sum().to_dict()
    fields = {}

    for col in numeric_cols:
        series = df[col].dropna()
        if series.empty:
            continue
        stats = {
            "mean": round(float(series.mean()), 2),
            "min": round(float(series.min()), 2),
            "max": round(float(series.max()), 2),
            "std": round(float(series.std() or 0), 2),
        }
        threshold_cfg = SENSOR_THRESHOLDS.get(col)
        if threshold_cfg:
            stats["threshold"] = threshold_cfg["max"]
            stats["unit"] = threshold_cfg["unit"]
            stats["status"] = "ABOVE_THRESHOLD" if stats["max"] > threshold_cfg["max"] else "WITHIN_RANGE"
            stats["exceedance_count"] = int((series > threshold_cfg["max"]).sum())
        else:
            stats["threshold"] = None
            stats["status"] = "NO_THRESHOLD_CONFIGURED"
            stats["exceedance_count"] = 0
        fields[col] = stats

    return {
        "row_count": int(len(df)),
        "columns": df.columns.tolist(),
        "missing_values": {k: int(v) for k, v in missing.items()},
        "fields": fields,
    }


def detect_anomaly(df: pd.DataFrame, field: str, z_thresh: float = 2.5) -> dict:
    """Simple z-score based anomaly flagging — described as 'possible anomaly', not certainty."""
    if field not in df.columns:
        return {"field": field, "anomalies_detected": 0, "note": "field not found"}
    series = df[field].dropna()
    if series.std() == 0 or series.empty:
        return {"field": field, "anomalies_detected": 0}
    z = (series - series.mean()) / series.std()
    anomaly_idx = series[abs(z) > z_thresh].index.tolist()
    return {
        "field": field,
        "anomalies_detected": len(anomaly_idx),
        "row_indices": anomaly_idx[:10],
        "note": "Flagged via statistical deviation (possible anomaly) — requires human review.",
    }
