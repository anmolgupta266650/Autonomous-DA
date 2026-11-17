import os
import io
import json
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np


def load_file(uploaded_file, sheet_name=None):
    """
    Load an uploaded file (CSV, Excel, JSON) into a pandas DataFrame.
    Returns (DataFrame, error_message)
    """
    if uploaded_file is None:
        return None, "No file provided"

    filename = uploaded_file.name.lower()
    try:
        if filename.endswith(".csv"):
            # Try utf-8 first, fallback to latin-1
            try:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding="utf-8")
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding="latin-1")
            return df, None

        elif filename.endswith((".xlsx", ".xls")):
            uploaded_file.seek(0)
            if sheet_name:
                df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
            else:
                df = pd.read_excel(uploaded_file)
            return df, None

        elif filename.endswith(".json"):
            uploaded_file.seek(0)
            try:
                df = pd.read_json(uploaded_file)
            except ValueError:
                uploaded_file.seek(0)
                data = json.load(uploaded_file)
                df = pd.json_normalize(data)
            return df, None

        elif filename.endswith(".xml"):
            uploaded_file.seek(0)
            try:
                df = pd.read_xml(uploaded_file)
                return df, None
            except Exception:
                uploaded_file.seek(0)
                import xml.etree.ElementTree as ET
                tree = ET.parse(uploaded_file)
                root = tree.getroot()
                rows = []
                for child in root:
                    row_dict = {elem.tag: elem.text for elem in child}
                    if row_dict:
                        rows.append(row_dict)
                if rows:
                    return pd.DataFrame(rows), None
                return None, "Could not extract tabular records from XML."

        else:
            return None, f"Unsupported file format: {uploaded_file.name}. Please upload CSV, Excel, JSON, or XML."

    except Exception as e:
        return None, f"Failed to load file: {str(e)}"


def get_excel_sheet_names(uploaded_file):
    """Returns a list of sheet names from an uploaded Excel file."""
    try:
        uploaded_file.seek(0)
        xl = pd.ExcelFile(uploaded_file)
        return xl.sheet_names
    except Exception:
        return []


def get_dataset_metadata(df: pd.DataFrame):
    """
    Computes comprehensive structural and quality metadata for a DataFrame.
    """
    if df is None or df.empty:
        return {}

    total_rows, total_cols = df.shape
    total_cells = total_rows * total_cols
    missing_cells = int(df.isnull().sum().sum())
    missing_percentage = (missing_cells / total_cells * 100) if total_cells > 0 else 0
    duplicate_rows = int(df.duplicated().sum())
    duplicate_percentage = (duplicate_rows / total_rows * 100) if total_rows > 0 else 0

    memory_bytes = df.memory_usage(deep=True).sum()
    if memory_bytes > 1024 * 1024:
        memory_str = f"{memory_bytes / (1024 * 1024):.2f} MB"
    else:
        memory_str = f"{memory_bytes / 1024:.2f} KB"

    # Count column data types
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category", "string"]).columns.tolist()
    date_cols = df.select_dtypes(include=["datetime", "datetime64"]).columns.tolist()
    bool_cols = df.select_dtypes(include=["bool"]).columns.tolist()

    # Column breakdown
    col_summary = []
    for col in df.columns:
        null_count = int(df[col].isnull().sum())
        null_pct = (null_count / total_rows * 100) if total_rows > 0 else 0
        unique_count = int(df[col].nunique())
        dtype_str = str(df[col].dtype)
        col_summary.append({
            "Column": col,
            "Type": dtype_str,
            "Null Count": null_count,
            "Null %": round(null_pct, 2),
            "Unique Values": unique_count,
            "Sample Value": str(df[col].dropna().iloc[0]) if not df[col].dropna().empty else "N/A"
        })

    # Data health index score (0 - 100)
    health_score = 100.0
    health_score -= min(missing_percentage * 1.5, 40)
    health_score -= min(duplicate_percentage * 2.0, 30)
    health_score = max(round(health_score, 1), 0.0)

    return {
        "rows": total_rows,
        "cols": total_cols,
        "missing_cells": missing_cells,
        "missing_pct": round(missing_percentage, 2),
        "duplicates": duplicate_rows,
        "duplicate_pct": round(duplicate_percentage, 2),
        "memory": memory_str,
        "numeric_cols": num_cols,
        "categorical_cols": cat_cols,
        "date_cols": date_cols,
        "bool_cols": bool_cols,
        "col_summary": pd.DataFrame(col_summary),
        "health_score": health_score
    }


def get_available_real_datasets():
    """
    Returns a dictionary of human-readable dataset names and their corresponding local filepaths.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    
    datasets = {
        "💼 SME Accounting & Ledger (Tally-Style)": os.path.join(data_dir, "sme_tally_financial_ledger.csv"),
        "🎓 College Students & Admissions (1,200 applicants)": os.path.join(data_dir, "college_university_admissions.csv"),
        "🛒 Global Superstore Sales (1,200 transactions)": os.path.join(data_dir, "global_superstore_2024.csv"),
        "📡 IBM Telco Customer Churn (1,200 subscribers)": os.path.join(data_dir, "telco_customer_churn_real.csv"),
        "🏡 California Housing Economics (1,500 Census records)": os.path.join(data_dir, "california_housing_real.csv"),
        "🔬 Healthcare Clinical Diagnostics (569 biopsy records)": os.path.join(data_dir, "healthcare_clinical_diagnostics.csv")
    }
    return datasets


def load_real_dataset(display_name: str) -> pd.DataFrame:
    """
    Loads one of the real benchmark datasets directly from the data/ folder.
    """
    datasets = get_available_real_datasets()
    filepath = datasets.get(display_name)
    if filepath and os.path.exists(filepath):
        try:
            return pd.read_csv(filepath)
        except Exception:
            pass
    
    # Fallback to generator if file not found
    if "College" in display_name or "Admission" in display_name or "Student" in display_name or "University" in display_name:
        return generate_sample_dataset("college")
    elif "Superstore" in display_name or "Sales" in display_name:
        return generate_sample_dataset("sales")
    elif "Churn" in display_name or "Telco" in display_name:
        return generate_sample_dataset("churn")
    else:
        return generate_sample_dataset("healthcare")


def generate_sample_dataset(dataset_type="sales"):
    """
    Generates realistic, industry-standard sample datasets for immediate testing and demonstration.
    Options: 'sales', 'churn', 'healthcare'
    """
    np.random.seed(42)
    random.seed(42)

    if dataset_type == "sales":
        # Global Superstore Sales dataset (Retail / BI)
        n_rows = 350
        categories = {
            "Technology": ["Laptops", "Smartphones", "Accessories", "Printers", "Monitors"],
            "Furniture": ["Chairs", "Bookcases", "Tables", "Furnishings"],
            "Office Supplies": ["Paper", "Binders", "Storage", "Appliances", "Envelopes"]
        }
        regions = ["North America", "Europe", "Asia-Pacific", "Latin America", "Middle East"]
        segments = ["Consumer", "Corporate", "Home Office"]
        ship_modes = ["Standard Class", "Second Class", "First Class", "Same Day"]

        start_date = datetime(2023, 1, 1)
        data = []

        for i in range(1, n_rows + 1):
            category = random.choice(list(categories.keys()))
            sub_cat = random.choice(categories[category])
            order_date = start_date + timedelta(days=random.randint(0, 700))
            region = random.choice(regions)
            segment = random.choice(segments)
            ship_mode = random.choice(ship_modes)

            if category == "Technology":
                sales = round(random.uniform(150, 2400), 2)
            elif category == "Furniture":
                sales = round(random.uniform(80, 1200), 2)
            else:
                sales = round(random.uniform(10, 350), 2)

            quantity = random.randint(1, 10)
            discount = random.choice([0.0, 0.0, 0.1, 0.15, 0.2, 0.3])
            # Profit formula with realistic variance
            cost = sales * random.uniform(0.55, 0.85)
            profit = round((sales * (1 - discount)) - cost, 2)
            customer_rating = random.choice([3, 4, 4, 5, 5, random.choice([1, 2])])
            returned = "Yes" if random.random() < 0.08 else "No"

            data.append({
                "Order_ID": f"ORD-{2023 + order_date.year % 2}-{1000 + i}",
                "Order_Date": order_date.strftime("%Y-%m-%d"),
                "Region": region,
                "Customer_Segment": segment,
                "Product_Category": category,
                "Sub_Category": sub_cat,
                "Shipping_Mode": ship_mode,
                "Sales_Amount": sales,
                "Quantity": quantity,
                "Discount_Rate": discount,
                "Net_Profit": profit,
                "Customer_Rating": customer_rating,
                "Returned": returned
            })

        df = pd.DataFrame(data)
        # Introduce a few realistic missing values (to showcase data cleaner)
        mask_discount = np.random.rand(len(df)) < 0.04
        df.loc[mask_discount, "Discount_Rate"] = np.nan
        mask_rating = np.random.rand(len(df)) < 0.03
        df.loc[mask_rating, "Customer_Rating"] = np.nan
        return df

    elif dataset_type == "churn":
        # Telecom / SaaS Customer Churn Dataset
        n_rows = 300
        contract_types = ["Month-to-month", "One year", "Two year"]
        payment_methods = ["Electronic check", "Mailed check", "Bank transfer", "Credit card"]
        internet_services = ["DSL", "Fiber optic", "No"]

        data = []
        for i in range(1, n_rows + 1):
            gender = random.choice(["Male", "Female"])
            senior = 1 if random.random() < 0.18 else 0
            tenure = random.randint(1, 72)
            contract = random.choice(contract_types)
            internet = random.choice(internet_services)
            monthly_charges = round(random.uniform(20.0, 118.0), 2)
            total_charges = round(monthly_charges * tenure * random.uniform(0.95, 1.05), 2)
            payment = random.choice(payment_methods)
            support = "Yes" if random.random() > 0.45 else "No"
            satisfaction = random.randint(1, 5)

            # Churn probability higher if short tenure, month-to-month, low satisfaction
            churn_score = (72 - tenure) / 72 * 0.4 + (1 if contract == "Month-to-month" else 0) * 0.3 + (5 - satisfaction) / 5 * 0.3
            churn = "Yes" if (churn_score + random.uniform(-0.15, 0.15)) > 0.55 else "No"

            data.append({
                "Customer_ID": f"CUST-{5000 + i}",
                "Gender": gender,
                "Senior_Citizen": senior,
                "Tenure_Months": tenure,
                "Internet_Service": internet,
                "Contract_Type": contract,
                "Payment_Method": payment,
                "Tech_Support": support,
                "Monthly_Charges": monthly_charges,
                "Total_Charges": total_charges,
                "Satisfaction_Score": satisfaction,
                "Churn": churn
            })

        df = pd.DataFrame(data)
        mask_support = np.random.rand(len(df)) < 0.04
        df.loc[mask_support, "Tech_Support"] = np.nan
        return df

    elif dataset_type == "healthcare":
        # Healthcare Patient Hospitalization Dataset
        n_rows = 300
        diagnoses = ["Cardiovascular", "Type 2 Diabetes", "Respiratory Infection", "Hypertension", "Orthopedic Injury"]
        admission_types = ["Emergency", "Elective", "Urgent"]
        genders = ["Male", "Female"]

        data = []
        for i in range(1, n_rows + 1):
            age = random.randint(18, 88)
            gender = random.choice(genders)
            diag = random.choice(diagnoses)
            adm = random.choice(admission_types)
            bp_sys = random.randint(95, 175)
            chol = random.randint(130, 290)
            sugar = random.randint(75, 230)
            los = random.randint(1, 14)
            cost = round(los * random.uniform(800, 2200) + random.uniform(500, 5000), 2)

            # Readmission logic
            risk = (age / 100) * 0.3 + (1 if diag == "Cardiovascular" else 0) * 0.3 + (los / 14) * 0.3 + random.uniform(-0.1, 0.1)
            readmitted = "Yes" if risk > 0.5 else "No"

            data.append({
                "Patient_ID": f"PAT-{8000 + i}",
                "Age": age,
                "Gender": gender,
                "Admission_Type": adm,
                "Primary_Diagnosis": diag,
                "Systolic_BP": bp_sys,
                "Cholesterol_Level": chol,
                "Blood_Sugar_mg_dL": sugar,
                "Length_of_Stay_Days": los,
                "Total_Treatment_Cost": cost,
                "Readmitted_30Days": readmitted
            })

        df = pd.DataFrame(data)
        mask_chol = np.random.rand(len(df)) < 0.04
        df.loc[mask_chol, "Cholesterol_Level"] = np.nan
        return df

    elif dataset_type in ["college", "university", "admission"]:
        # University Student & College Admissions Benchmark
        n_rows = 1200
        depts = {
            "Engineering & Computing": ["Computer Science", "Data Science", "Biomedical Engineering", "Mechanical Engineering", "Electrical Engineering"],
            "Business & Economics": ["Finance", "Business Administration", "Marketing Analytics", "Economics"],
            "Health Sciences": ["Nursing", "Pre-Medicine", "Public Health", "Pharmacy"],
            "Arts & Humanities": ["Psychology", "Communications", "Political Science", "English Literature"]
        }
        tiers = ["Tier 1 (Ivy / R1 Elite)", "Tier 2 (National Flagship)", "Tier 3 (Regional College)"]
        residencies = ["In-State", "Out-of-State", "International"]
        genders = ["Female", "Male", "Non-Binary"]
        start_date = datetime(2023, 9, 1)

        records = []
        for i in range(n_rows):
            dept = np.random.choice(list(depts.keys()), p=[0.38, 0.28, 0.22, 0.12])
            major = np.random.choice(depts[dept])
            tier = np.random.choice(tiers, p=[0.25, 0.45, 0.30])
            residency = np.random.choice(residencies, p=[0.55, 0.32, 0.13])
            gender = np.random.choice(genders, p=[0.51, 0.46, 0.03])
            age = int(np.random.choice([17, 18, 19, 20, 21, 22, 23], p=[0.10, 0.60, 0.16, 0.06, 0.04, 0.02, 0.02]))
            app_date = start_date + timedelta(days=int(np.random.randint(0, 180)))

            gpa = round(float(np.clip(np.random.normal(3.55, 0.32), 2.10, 4.00)), 2)
            sat = int(np.clip(int(np.random.normal(1280 + (gpa - 3.5) * 180, 110)), 920, 1600))
            act = int(np.clip(int(14 + (sat / 1600) * 22 + np.random.normal(0, 1.2)), 18, 36))
            class_rank_pct = int(np.clip(int(50 + (gpa - 2.5) * 32 + np.random.normal(0, 5)), 50, 99))
            ap_courses = int(np.clip(int(np.random.poisson(lam=max(0.5, (gpa - 2.8) * 3))), 0, 10))

            extracurricular = int(np.random.choice([1, 2, 3, 4, 5], p=[0.10, 0.20, 0.35, 0.23, 0.12]))
            research_exp = "Yes" if (np.random.rand() < (0.15 + (1 if "Science" in major or "Engineering" in major else 0) * 0.20)) else "No"
            rec_score = int(np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.15, 0.40, 0.28, 0.12]))
            sop_score = int(np.random.choice([1, 2, 3, 4, 5], p=[0.08, 0.18, 0.38, 0.24, 0.12]))

            base_tuition = 52000 if "Tier 1" in tier else (28000 if residency == "In-State" else 41000)
            tuition = round(float(base_tuition + np.random.normal(0, 2200)), 2)
            scholarship_prob = 0.65 if gpa > 3.6 or sat > 1350 else 0.25
            scholarship = round(float(np.random.uniform(4000, 24000) if np.random.rand() < scholarship_prob else 0.0), 2)

            tier_pen = 0.25 if "Tier 1" in tier else (0.10 if "Tier 2" in tier else 0.0)
            gpa_norm = (gpa - 2.1) / 1.9
            sat_norm = (sat - 920) / 680
            holistic_norm = (extracurricular + rec_score + sop_score + (1 if research_exp == "Yes" else 0)) / 16.0

            z = (0.35 * gpa_norm + 0.25 * sat_norm + 0.25 * holistic_norm - tier_pen) + np.random.normal(0, 0.08)
            chance = float(np.clip(1.0 / (1.0 + np.exp(-4.5 * (z - 0.42))), 0.05, 0.98))

            if chance >= 0.65:
                status = "Admitted"
            elif chance >= 0.40:
                status = "Waitlisted"
            else:
                status = "Rejected"

            records.append({
                "Student_ID": f"STU-2024-{1000 + i}",
                "Application_Date": app_date.strftime("%Y-%m-%d"),
                "Age": age,
                "Gender": gender,
                "Residency_Status": residency,
                "Department": dept,
                "Intended_Major": major,
                "University_Tier": tier,
                "High_School_GPA": gpa,
                "SAT_Score": sat,
                "ACT_Score": act,
                "AP_Courses_Completed": ap_courses,
                "Class_Rank_Percentile": class_rank_pct,
                "Extracurricular_Rating": extracurricular,
                "Research_Experience": research_exp,
                "Recommendation_Score": rec_score,
                "Statement_of_Purpose_Score": sop_score,
                "Annual_Tuition_USD": tuition,
                "Scholarship_Award_USD": scholarship,
                "Admission_Chance": round(chance, 3),
                "Admission_Status": status
            })

        df_col = pd.DataFrame(records)
        df_col.loc[np.random.choice(df_col.index, 32, replace=False), "SAT_Score"] = np.nan
        df_col.loc[np.random.choice(df_col.index, 20, replace=False), "Scholarship_Award_USD"] = np.nan
        return df_col

    return pd.DataFrame()
