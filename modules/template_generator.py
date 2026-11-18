import io
import pandas as pd


def get_sample_templates() -> dict:
    """
    Generates standard, clean starter templates for various business and academic use cases.
    Returns a dictionary of {template_name: csv_string_or_bytes}.
    """
    templates = {}

    # 1. Tally & Financial Accounting Ledger Template
    tally_data = {
        "Voucher_No": ["TXN-001", "TXN-002", "TXN-003", "TXN-004", "TXN-005"],
        "Date": ["2024-01-15", "2024-01-18", "2024-02-05", "2024-02-20", "2024-03-01"],
        "Party_Name": ["Apex Infotech Pvt Ltd", "Balaji Steel Corp", "Chaitanya Logistics", "Delta Electronics", "Everest Enterprises"],
        "Voucher_Type": ["Sales", "Receipt", "Purchase", "Payment", "Sales"],
        "Group_Head": ["Sundry Debtors", "Bank Accounts", "Sundry Creditors", "Direct Expenses", "Sundry Debtors"],
        "Debit": [0.0, 0.0, 45000.0, 12000.0, 0.0],
        "Credit": [75000.0, 75000.0, 0.0, 0.0, 125000.0],
        "GST_Rate_%": [18, 0, 18, 12, 18],
        "Payment_Status": ["Cleared", "Paid", "Pending", "Paid", "Overdue"]
    }
    templates["tally_ledger"] = pd.DataFrame(tally_data).to_csv(index=False).encode("utf-8")

    # 2. Commercial Sales & BI Dashboard Template
    sales_data = {
        "Order_ID": ["ORD-1001", "ORD-1002", "ORD-1003", "ORD-1004", "ORD-1005"],
        "Order_Date": ["2024-01-10", "2024-01-14", "2024-01-22", "2024-02-03", "2024-02-15"],
        "Customer_Name": ["John Doe", "Jane Smith", "Acme Corp", "Tech Solutions", "Global Retail"],
        "Region": ["North", "South", "East", "West", "North"],
        "Category": ["Technology", "Furniture", "Office Supplies", "Technology", "Furniture"],
        "Sales": [1200.50, 450.00, 89.90, 2400.00, 780.25],
        "Quantity": [2, 1, 5, 3, 2],
        "Discount": [0.1, 0.0, 0.05, 0.15, 0.0],
        "Profit": [340.00, 120.50, 22.40, 680.00, 195.00]
    }
    templates["sales_bi"] = pd.DataFrame(sales_data).to_csv(index=False).encode("utf-8")

    # 3. Academic & Survey Research Template
    research_data = {
        "Participant_ID": ["SUBJ-001", "SUBJ-002", "SUBJ-003", "SUBJ-004", "SUBJ-005"],
        "Treatment_Group": ["Control", "Intervention A", "Intervention B", "Control", "Intervention A"],
        "Gender": ["Female", "Male", "Female", "Male", "Female"],
        "Study_Hours_Per_Week": [12.5, 18.0, 22.5, 8.0, 19.5],
        "Pre_Test_Score": [62.0, 65.5, 59.0, 55.0, 68.0],
        "Post_Test_Score": [64.0, 82.5, 88.0, 56.5, 85.0],
        "Satisfaction_Rating": [4, 5, 5, 3, 5]
    }
    templates["academic_research"] = pd.DataFrame(research_data).to_csv(index=False).encode("utf-8")

    return templates


def get_available_templates() -> dict:
    """Returns available starter templates."""
    return {
        "tally_ledger": "Tally & Financial Accounting Ledger",
        "sales_bi": "Commercial Sales & BI Dashboard",
        "academic_research": "Academic Survey & Scientific Research"
    }


def generate_template_data(template_name: str) -> pd.DataFrame:
    """Generates DataFrame for a selected starter template."""
    tmps = get_sample_templates()
    if template_name in tmps:
        return pd.read_csv(io.BytesIO(tmps[template_name]))
    return pd.read_csv(io.BytesIO(list(tmps.values())[0]))


