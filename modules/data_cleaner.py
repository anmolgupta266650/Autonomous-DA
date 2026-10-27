import pandas as pd
import numpy as np


def clean_missing_values(df: pd.DataFrame, column: str, strategy: str, custom_value=None):
    """
    Cleans missing values in a specific column or all columns.
    Strategy: 'mean', 'median', 'mode', 'zero', 'custom', 'drop_rows', 'drop_col', 'ffill', 'bfill'
    """
    df = df.copy()
    if df.empty:
        return df, "DataFrame is empty."

    cols_to_process = [column] if column != "All Columns" else df.columns.tolist()
    modified_count = 0

    for col in cols_to_process:
        null_count = df[col].isnull().sum()
        if null_count == 0:
            continue

        if strategy == "mean" and pd.api.types.is_numeric_dtype(df[col]):
            mean_val = df[col].mean()
            df[col] = df[col].fillna(mean_val)
            modified_count += null_count

        elif strategy == "median" and pd.api.types.is_numeric_dtype(df[col]):
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            modified_count += null_count

        elif strategy == "mode":
            mode_val = df[col].mode()
            if not mode_val.empty:
                df[col] = df[col].fillna(mode_val[0])
                modified_count += null_count

        elif strategy == "zero" and pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(0)
            modified_count += null_count

        elif strategy == "custom" and custom_value is not None:
            df[col] = df[col].fillna(custom_value)
            modified_count += null_count

        elif strategy == "ffill":
            df[col] = df[col].ffill()
            modified_count += null_count

        elif strategy == "bfill":
            df[col] = df[col].bfill()
            modified_count += null_count

        elif strategy == "drop_rows":
            before = len(df)
            df = df.dropna(subset=[col])
            modified_count += (before - len(df))

        elif strategy == "drop_col":
            df = df.drop(columns=[col])
            modified_count += 1

    msg = f"Processed {modified_count} missing value entries using strategy '{strategy}'."
    return df, msg


def remove_duplicates(df: pd.DataFrame, subset_cols=None, keep="first"):
    """
    Removes duplicate rows based on subset of columns or entire row.
    keep: 'first', 'last', or False (drop all duplicates).
    """
    df = df.copy()
    before = len(df)
    cols = subset_cols if subset_cols and len(subset_cols) > 0 else None
    df = df.drop_duplicates(subset=cols, keep=keep)
    after = len(df)
    removed = before - after
    return df, f"Successfully removed {removed} duplicate rows."


def cast_column_type(df: pd.DataFrame, column: str, target_type: str):
    """
    Converts a column to a specified data type.
    target_type: 'int', 'float', 'str', 'datetime', 'category', 'bool'
    """
    df = df.copy()
    if column not in df.columns:
        return df, f"Column '{column}' not found."

    try:
        if target_type == "int":
            df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0).astype(int)
        elif target_type == "float":
            df[column] = pd.to_numeric(df[column], errors="coerce")
        elif target_type == "str":
            df[column] = df[column].astype(str)
        elif target_type == "datetime":
            df[column] = pd.to_datetime(df[column], errors="coerce")
        elif target_type == "category":
            df[column] = df[column].astype("category")
        elif target_type == "bool":
            df[column] = df[column].astype(bool)
        return df, f"Column '{column}' converted to '{target_type}' successfully."
    except Exception as e:
        return df, f"Conversion error: {str(e)}"


def detect_and_handle_outliers(df: pd.DataFrame, column: str, method="iqr", action="clamp"):
    """
    Detects and handles outliers using IQR or Z-score method.
    action: 'clamp' (Winsorize to upper/lower bound) or 'drop' (remove rows).
    """
    df = df.copy()
    if column not in df.columns or not pd.api.types.is_numeric_dtype(df[column]):
        return df, f"Column '{column}' is not numeric.", 0

    series = df[column].dropna()
    if len(series) == 0:
        return df, "Column is empty.", 0

    if method == "iqr":
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
    elif method == "zscore":
        mean = series.mean()
        std = series.std()
        if std == 0:
            return df, "Standard deviation is zero; no outliers detected.", 0
        lower_bound = mean - 3 * std
        upper_bound = mean + 3 * std
    else:
        return df, f"Unknown method '{method}'", 0

    outlier_mask = (df[column] < lower_bound) | (df[column] > upper_bound)
    outlier_count = int(outlier_mask.sum())

    if outlier_count == 0:
        return df, f"No outliers found in '{column}' using {method.upper()} threshold.", 0

    if action == "clamp":
        df[column] = df[column].clip(lower=lower_bound, upper=upper_bound)
        msg = f"Clamped {outlier_count} outliers in '{column}' to range [{lower_bound:.2f}, {upper_bound:.2f}]."
    elif action == "drop":
        df = df[~outlier_mask].reset_index(drop=True)
        msg = f"Dropped {outlier_count} outlier rows from '{column}' outside range [{lower_bound:.2f}, {upper_bound:.2f}]."

    return df, msg, outlier_count


def drop_selected_columns(df: pd.DataFrame, columns_to_drop: list):
    """Drops one or more columns from the DataFrame."""
    df = df.copy()
    valid_cols = [c for c in columns_to_drop if c in df.columns]
    df = df.drop(columns=valid_cols)
    return df, f"Dropped {len(valid_cols)} columns: {', '.join(valid_cols)}"


def rename_column(df: pd.DataFrame, old_name: str, new_name: str):
    """Renames a single column."""
    df = df.copy()
    if not new_name or new_name.strip() == "":
        return df, "New column name cannot be empty."
    if old_name not in df.columns:
        return df, f"Column '{old_name}' not found."
    df = df.rename(columns={old_name: new_name.strip()})
    return df, f"Renamed column '{old_name}' to '{new_name.strip()}'."


def filter_dataset(df: pd.DataFrame, column: str, operator: str, value: str):
    """
    Applies custom row filter.
    Operators: '==', '!=', '>', '<', '>=', '<=', 'contains'
    """
    df = df.copy()
    if column not in df.columns:
        return df, f"Column '{column}' not found."

    before_len = len(df)
    try:
        if pd.api.types.is_numeric_dtype(df[column]):
            num_val = float(value)
            if operator == "==":
                df = df[df[column] == num_val]
            elif operator == "!=":
                df = df[df[column] != num_val]
            elif operator == ">":
                df = df[df[column] > num_val]
            elif operator == "<":
                df = df[df[column] < num_val]
            elif operator == ">=":
                df = df[df[column] >= num_val]
            elif operator == "<=":
                df = df[df[column] <= num_val]
        else:
            str_val = str(value).lower()
            series_str = df[column].astype(str).str.lower()
            if operator == "==":
                df = df[series_str == str_val]
            elif operator == "!=":
                df = df[series_str != str_val]
            elif operator == "contains":
                df = df[series_str.str.contains(str_val, na=False)]

        after_len = len(df)
        filtered_out = before_len - after_len
        return df.reset_index(drop=True), f"Filter applied. Retained {after_len} rows ({filtered_out} rows filtered out)."
    except Exception as e:
        return df, f"Filter error: {str(e)}"
