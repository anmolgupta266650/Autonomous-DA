import pandas as pd
import numpy as np


def create_math_column(df: pd.DataFrame, new_col_name: str, col1: str, operator: str, col2_or_scalar, is_scalar: bool = False):
    """
    Creates a new calculated column via mathematical operations.
    operator: '+', '-', '*', '/', '%', 'power'
    """
    df = df.copy()
    if not new_col_name or new_col_name.strip() == "":
        return df, "New column name cannot be empty."

    new_name = new_col_name.strip()
    try:
        s1 = pd.to_numeric(df[col1], errors="coerce")
        if is_scalar:
            val2 = float(col2_or_scalar)
            s2 = val2
        else:
            s2 = pd.to_numeric(df[col2_or_scalar], errors="coerce")

        if operator == "+":
            df[new_name] = s1 + s2
        elif operator == "-":
            df[new_name] = s1 - s2
        elif operator == "*":
            df[new_name] = s1 * s2
        elif operator == "/":
            df[new_name] = s1 / s2
        elif operator == "%":
            df[new_name] = s1 % s2
        elif operator == "power":
            df[new_name] = s1 ** s2
        else:
            return df, f"Unsupported operator: {operator}"

        return df, f"Calculated column '{new_name}' created successfully."
    except Exception as e:
        return df, f"Calculation error: {str(e)}"


def apply_transform(df: pd.DataFrame, new_col_name: str, col: str = None, transform_type: str = "log"):
    """
    Applies mathematical transform to a single numeric column.
    transform_type: 'log', 'log1p', 'sqrt', 'abs', 'square', 'round'
    """
    df = df.copy()
    # Flexible argument parsing if called as apply_transform(df, col, transform_type)
    if col in ["log", "log1p", "sqrt", "abs", "square", "round"]:
        transform_type = col
        col = new_col_name
        new_col_name = f"{col}_{transform_type}"
    elif col is None:
        col = new_col_name
        new_col_name = f"{col}_{transform_type}"

    new_name = new_col_name.strip() if new_col_name else f"{col}_{transform_type}"
    try:
        series = pd.to_numeric(df[col], errors="coerce")
        if transform_type == "log":
            # Avoid negative or zero log
            df[new_name] = np.log(series.clip(lower=1e-9))
        elif transform_type == "log1p":
            df[new_name] = np.log1p(series.clip(lower=0))
        elif transform_type == "sqrt":
            df[new_name] = np.sqrt(series.clip(lower=0))
        elif transform_type == "abs":
            df[new_name] = np.abs(series)
        elif transform_type == "square":
            df[new_name] = np.square(series)
        elif transform_type == "round":
            df[new_name] = np.round(series, 2)
        return df, f"Transform '{transform_type}' applied as column '{new_name}'."
    except Exception as e:
        return df, f"Transform error: {str(e)}"


def extract_date_features(df: pd.DataFrame, date_col: str, features_to_extract: list):
    """
    Extracts time components (Year, Month, Quarter, Day of Week, Is_Weekend, Hour) from date column.
    """
    df = df.copy()
    try:
        dt_series = pd.to_datetime(df[date_col], errors="coerce")
        created = []

        if "Year" in features_to_extract:
            col_name = f"{date_col}_Year"
            df[col_name] = dt_series.dt.year
            created.append(col_name)

        if "Month" in features_to_extract:
            col_name = f"{date_col}_Month"
            df[col_name] = dt_series.dt.month
            created.append(col_name)

        if "Month Name" in features_to_extract:
            col_name = f"{date_col}_MonthName"
            df[col_name] = dt_series.dt.strftime("%b")
            created.append(col_name)

        if "Quarter" in features_to_extract:
            col_name = f"{date_col}_Quarter"
            df[col_name] = dt_series.dt.quarter
            created.append(col_name)

        if "Day of Week" in features_to_extract:
            col_name = f"{date_col}_DayOfWeek"
            df[col_name] = dt_series.dt.day_name()
            created.append(col_name)

        if "Day of Month" in features_to_extract:
            col_name = f"{date_col}_Day"
            df[col_name] = dt_series.dt.day
            created.append(col_name)

        if "Is Weekend" in features_to_extract:
            col_name = f"{date_col}_IsWeekend"
            df[col_name] = dt_series.dt.dayofweek.isin([5, 6]).astype(int)
            created.append(col_name)

        return df, f"Extracted {len(created)} date features: {', '.join(created)}"
    except Exception as e:
        return df, f"Date extraction error: {str(e)}"


def create_binned_column(df: pd.DataFrame, new_col_name: str, col: str = None, n_bins: int = 3, labels=None, bins: int = None):
    """
    Bins a continuous numeric column into discrete quantile or equal-width buckets.
    """
    df = df.copy()
    if bins is not None:
        n_bins = bins

    # Flexible argument parsing if called as create_binned_column(df, col, n_bins=4)
    if col is None or isinstance(col, int):
        if isinstance(col, int):
            n_bins = col
        col = new_col_name
        new_col_name = f"{col}_Binned"

    new_name = new_col_name.strip() if new_col_name else f"{col}_Binned"
    try:
        series = pd.to_numeric(df[col], errors="coerce")
        if labels and len(labels) == n_bins:
            df[new_name] = pd.qcut(series, q=n_bins, labels=labels, duplicates="drop")
        else:
            df[new_name] = pd.qcut(series, q=n_bins, duplicates="drop").astype(str)
        return df, f"Binned column '{new_name}' created with {n_bins} categories."
    except Exception as e:
        # Fallback to cut if qcut fails due to duplicate quantiles
        try:
            df[new_name] = pd.cut(series, bins=n_bins).astype(str)
            return df, f"Binned column '{new_name}' created using equal-interval cuts."
        except Exception as e2:
            return df, f"Binning error: {str(e2)}"


def create_conditional_flag(df: pd.DataFrame, new_col_name: str, col: str, operator: str, threshold: float, true_val="High", false_val="Low"):
    """
    Creates a conditional label column based on a numeric threshold.
    """
    df = df.copy()
    new_name = new_col_name.strip() if new_col_name else f"{col}_Flag"
    try:
        series = pd.to_numeric(df[col], errors="coerce")
        if operator == ">":
            mask = series > threshold
        elif operator == ">=":
            mask = series >= threshold
        elif operator == "<":
            mask = series < threshold
        elif operator == "<=":
            mask = series <= threshold
        elif operator == "==":
            mask = series == threshold
        else:
            mask = series != threshold

        df[new_name] = np.where(mask, true_val, false_val)
        return df, f"Conditional column '{new_name}' created based on condition ({col} {operator} {threshold})."
    except Exception as e:
        return df, f"Error creating condition: {str(e)}"
