"""
Streaming Ingestion & Real-Time Telemetry Engine (Phase 2 Component)
Demonstrates sliding-window analytics, real-time event ingestion, and threshold breach detection.
"""

import time
import numpy as np
import pandas as pd


def simulate_iot_financial_stream(n_events: int = 60, seed: int = 42) -> pd.DataFrame:
    """
    Simulates a high-frequency real-time event stream (e.g., e-commerce orders, server telemetry).
    """
    np.random.seed(seed)
    now = pd.Timestamp.now()
    
    timestamps = [now - pd.Timedelta(seconds=(n_events - i) * 2) for i in range(n_events)]
    base_values = np.random.normal(loc=250.0, scale=40.0, size=n_events)
    
    # Inject intentional sudden anomaly spikes
    if n_events > 5:
        base_values[min(15, n_events // 3)] = 890.0  # Spike 1
    if n_events > 10:
        base_values[min(42, int(n_events * 0.7))] = 1250.0 # Spike 2 (Fraud candidate)
    
    latencies = np.random.exponential(scale=18.0, size=n_events) + 5.0
    services = np.random.choice(["checkout_api", "payment_gateway", "auth_service", "inventory_db"], size=n_events)
    status_codes = np.random.choice([200, 200, 200, 201, 400, 500], p=[0.70, 0.15, 0.05, 0.05, 0.03, 0.02], size=n_events)

    df_stream = pd.DataFrame({
        "timestamp": timestamps,
        "event_id": [f"EVT-{10000 + i}" for i in range(n_events)],
        "service": services,
        "amount_usd": np.round(np.maximum(base_values, 10.0), 2),
        "latency_ms": np.round(latencies, 1),
        "status_code": status_codes
    })
    return df_stream


def compute_sliding_window_metrics(stream_df: pd.DataFrame, window_size: int = 10) -> pd.DataFrame:
    """
    Computes rolling metrics across a sliding window of events.
    """
    if stream_df.empty or "amount_usd" not in stream_df.columns:
        return stream_df

    df = stream_df.copy()
    df["rolling_mean"] = df["amount_usd"].rolling(window=window_size, min_periods=1).mean().round(2)
    df["rolling_std"] = df["amount_usd"].rolling(window=window_size, min_periods=1).std().fillna(0).round(2)
    df["rolling_volume"] = df["amount_usd"].cumsum().round(2)
    
    # Calculate rolling Z-Score
    std_safe = df["rolling_std"].replace(0, 1.0)
    df["z_score"] = ((df["amount_usd"] - df["rolling_mean"]) / std_safe).abs().round(2)
    return df


def detect_streaming_anomalies(stream_df: pd.DataFrame, threshold_z: float = 2.5) -> dict:
    """
    Detects threshold breaches and anomalous spikes in streaming events.
    """
    if stream_df.empty:
        return {"anomaly_count": 0, "anomalies": [], "stream_health": "UNKNOWN"}

    df = compute_sliding_window_metrics(stream_df)
    breaches = df[df["z_score"] >= threshold_z]
    
    anomalies_list = []
    for _, row in breaches.iterrows():
        anomalies_list.append({
            "event_id": row["event_id"],
            "timestamp": str(row["timestamp"]),
            "amount_usd": float(row["amount_usd"]),
            "z_score": float(row["z_score"]),
            "service": row["service"],
            "status_code": int(row["status_code"])
        })
        
    health = "CRITICAL" if len(anomalies_list) >= 3 else ("WARNING" if len(anomalies_list) > 0 else "HEALTHY")
    
    return {
        "total_events_processed": len(df),
        "anomaly_count": len(anomalies_list),
        "stream_health": health,
        "max_z_score": float(df["z_score"].max()) if not df.empty else 0.0,
        "anomalies": anomalies_list
    }
