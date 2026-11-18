import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, confusion_matrix,
    r2_score, mean_absolute_error, mean_squared_error
)


def detect_task_type(series_or_df, target_col: str = None):
    """
    Determines whether target variable is 'classification' or 'regression'.
    Accepts either a pd.Series or (pd.DataFrame, target_col).
    """
    if isinstance(series_or_df, pd.DataFrame):
        if target_col is None:
            raise ValueError("target_col is required when passing a DataFrame")
        series = series_or_df[target_col]
    else:
        series = series_or_df

    if pd.api.types.is_numeric_dtype(series):
        unique_cnt = series.nunique()
        if unique_cnt <= 8 and (series.dropna() % 1 == 0).all():
            return "classification"
        return "regression"
    else:
        return "classification"


def prepare_ml_data(df: pd.DataFrame, target_col: str, feature_cols: list = None):
    """
    Cleans, imputes, and encodes features for model training.
    """
    if feature_cols is None:
        feature_cols = [c for c in df.columns if c != target_col]
    elif isinstance(feature_cols, str):
        feature_cols = [feature_cols]

    df_clean = df[[target_col] + feature_cols].dropna(subset=[target_col]).copy()
    y_raw = df_clean[target_col]
    X_raw = df_clean[feature_cols].copy()

    task_type = detect_task_type(y_raw)
    target_encoder = None

    if task_type == "classification":
        target_encoder = LabelEncoder()
        y = target_encoder.fit_transform(y_raw.astype(str))
    else:
        y = pd.to_numeric(y_raw, errors="coerce").fillna(y_raw.median()).values

    # Preprocess features
    encoders = {}
    X = pd.DataFrame(index=X_raw.index)

    for col in feature_cols:
        if pd.api.types.is_numeric_dtype(X_raw[col]):
            col_series = pd.to_numeric(X_raw[col], errors="coerce")
            med = col_series.median() if not np.isnan(col_series.median()) else 0.0
            X[col] = col_series.fillna(med)
        else:
            # Check if column is actually numerical but loaded as object due to spaces (e.g. TotalCharges)
            converted = pd.to_numeric(X_raw[col], errors="coerce")
            if converted.notnull().sum() / max(len(converted), 1) > 0.8:
                med = converted.median() if not np.isnan(converted.median()) else 0.0
                X[col] = converted.fillna(med)
            else:
                mode_val = X_raw[col].mode().iloc[0] if not X_raw[col].mode().empty else "Unknown"
                filled_col = X_raw[col].fillna(mode_val).astype(str)
                le = LabelEncoder()
                X[col] = le.fit_transform(filled_col)
                encoders[col] = le

    return X, y, task_type, target_encoder, encoders


def train_and_evaluate_models(X: pd.DataFrame, y: np.ndarray, task_type: str):
    """
    Trains multiple ML models and benchmarks their performance on a holdout test set.
    """
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    results = []
    trained_models = {}

    if task_type == "classification":
        models = {
            "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42),
            "Gradient Boosting": GradientBoostingClassifier(n_estimators=80, random_state=42),
            "Decision Tree": DecisionTreeClassifier(max_depth=6, random_state=42),
            "Logistic Regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, random_state=42))
        }

        for name, model in models.items():
            try:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)

                acc = accuracy_score(y_test, y_pred)
                prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
                rec = recall_score(y_test, y_pred, average="weighted", zero_division=0)
                f1 = f1_score(y_test, y_pred, average="weighted", zero_division=0)

                results.append({
                    "Model": name,
                    "Accuracy": round(acc * 100, 2),
                    "Precision": round(prec * 100, 2),
                    "Recall": round(rec * 100, 2),
                    "F1-Score": round(f1 * 100, 2)
                })
                trained_models[name] = model
            except Exception:
                continue

        results_df = pd.DataFrame(results).sort_values(by="F1-Score", ascending=False)
        best_model_name = results_df.iloc[0]["Model"] if not results_df.empty else None

        # Confusion Matrix for best model
        cm_fig = None
        if best_model_name and best_model_name in trained_models:
            best_model = trained_models[best_model_name]
            y_pred_best = best_model.predict(X_test)
            cm = confusion_matrix(y_test, y_pred_best)
            cm_fig = px.imshow(
                cm,
                text_auto=True,
                color_continuous_scale="Viridis",
                title=f"Confusion Matrix ({best_model_name})",
                labels=dict(x="Predicted Class", y="Actual Class")
            )
            cm_fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")

        # Feature Importance
        feat_fig = None
        if best_model_name and best_model_name in trained_models:
            model_obj = trained_models[best_model_name]
            if hasattr(model_obj, "named_steps"):
                model_obj = list(model_obj.named_steps.values())[-1]
            importances = None
            if hasattr(model_obj, "feature_importances_"):
                importances = model_obj.feature_importances_
            elif hasattr(model_obj, "coef_"):
                raw_coef = np.abs(model_obj.coef_)
                importances = raw_coef.mean(axis=0) if raw_coef.ndim > 1 else raw_coef

            if importances is not None and len(importances) == len(X.columns):
                imp_df = pd.DataFrame({"Feature": X.columns, "Importance": importances}).sort_values(by="Importance", ascending=True)
                feat_fig = px.bar(
                    imp_df,
                    x="Importance",
                    y="Feature",
                    orientation="h",
                    color="Importance",
                    color_continuous_scale="Teal",
                    title=f"Feature Importances / Weights ({best_model_name})"
                )
                feat_fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")

        return results_df, trained_models, best_model_name, cm_fig, feat_fig, (X_test, y_test)

    else:
        # Regression
        models = {
            "Random Forest Regressor": RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42),
            "Gradient Boosting Regressor": GradientBoostingRegressor(n_estimators=80, random_state=42),
            "Linear Regression": make_pipeline(StandardScaler(), LinearRegression()),
            "Ridge Regression": make_pipeline(StandardScaler(), Ridge(alpha=1.0))
        }

        for name, model in models.items():
            try:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)

                r2 = r2_score(y_test, y_pred)
                mae = mean_absolute_error(y_test, y_pred)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))

                results.append({
                    "Model": name,
                    "R² Score": round(r2, 4),
                    "MAE": round(mae, 2),
                    "RMSE": round(rmse, 2)
                })
                trained_models[name] = model
            except Exception:
                continue

        results_df = pd.DataFrame(results).sort_values(by="R² Score", ascending=False)
        best_model_name = results_df.iloc[0]["Model"] if not results_df.empty else None

        # Actual vs Predicted Scatter
        act_pred_fig = None
        if best_model_name and best_model_name in trained_models:
            best_model = trained_models[best_model_name]
            y_pred_best = best_model.predict(X_test)
            plot_df = pd.DataFrame({"Actual": y_test, "Predicted": y_pred_best})
            act_pred_fig = px.scatter(
                plot_df,
                x="Actual",
                y="Predicted",
                trendline="ols",
                color_discrete_sequence=["#38bdf8"],
                title=f"Actual vs. Predicted Values ({best_model_name})"
            )
            act_pred_fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")

        # Feature Importance
        feat_fig = None
        if best_model_name and best_model_name in trained_models:
            model_obj = trained_models[best_model_name]
            if hasattr(model_obj, "named_steps"):
                model_obj = list(model_obj.named_steps.values())[-1]
            importances = None
            if hasattr(model_obj, "feature_importances_"):
                importances = model_obj.feature_importances_
            elif hasattr(model_obj, "coef_"):
                raw_coef = np.abs(model_obj.coef_)
                importances = raw_coef.mean(axis=0) if raw_coef.ndim > 1 else raw_coef

            if importances is not None and len(importances) == len(X.columns):
                imp_df = pd.DataFrame({"Feature": X.columns, "Importance": importances}).sort_values(by="Importance", ascending=True)
                feat_fig = px.bar(
                    imp_df,
                    x="Importance",
                    y="Feature",
                    orientation="h",
                    color="Importance",
                    color_continuous_scale="Purples",
                    title=f"Feature Importances / Weights ({best_model_name})"
                )
                feat_fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")

        return results_df, trained_models, best_model_name, act_pred_fig, feat_fig, (X_test, y_test)
