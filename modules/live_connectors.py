import re
import urllib.request
import sqlite3
import pandas as pd
from typing import Tuple, Optional


def load_google_sheet_by_url(url: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Ingests a Google Sheets document directly via public or shareable link.
    Automatically converts edit/view URLs into direct CSV export endpoints.
    """
    if not url or "google.com" not in url:
        return None, "Please provide a valid Google Sheets URL."

    # Extract Sheet ID
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
    if not match:
        return None, "Could not extract Google Sheet ID from URL."

    sheet_id = match.group(1)

    # Extract gid (sheet tab) if present
    gid_match = re.search(r"[#&?]gid=([0-9]+)", url)
    gid = gid_match.group(1) if gid_match else "0"

    export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

    try:
        req = urllib.request.Request(
            export_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            df = pd.read_csv(resp)
            return df, None
    except Exception as e:
        return None, f"Failed to connect to Google Sheet: {e}. Ensure sharing is set to 'Anyone with the link can view'."


def query_sqlite_database(db_path: str, sql_query: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Executes a direct SQL query against a local SQLite database file.
    """
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(sql_query, conn)
        conn.close()
        return df, None
    except Exception as e:
        return None, f"Database query error: {str(e)}"


def probe_local_tally_endpoint(host: str = "http://localhost:9000") -> Tuple[bool, str]:
    """
    Probes if Tally Prime or Tally.ERP 9 is running locally and accepting XML requests.
    """
    try:
        req = urllib.request.Request(
            host,
            headers={"User-Agent": "Autonomous-DA-Connector"},
            method="GET"
        )
        with urllib.request.urlopen(req, timeout=2) as resp:
            return True, f"Connected to live Tally instance on {host} (Status: {resp.getcode()})."
    except Exception:
        return False, f"Tally is not responding on {host}. To enable: In Tally Prime, press F1 -> Settings -> Connectivity -> Set 'TallyPrime act as Both (Server/Client)' to Yes."


def load_remote_rest_api(api_url: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Ingests live JSON data directly from any REST API endpoint or remote URL.
    Auto-flattens nested JSON payloads into a clean tabular DataFrame.
    """
    if not api_url or not api_url.startswith(("http://", "https://")):
        return None, "Please provide a valid HTTP or HTTPS API endpoint URL."

    try:
        req = urllib.request.Request(
            api_url,
            headers={"User-Agent": "Autonomous-DA-Intelligence/1.0", "Accept": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            import json
            raw_data = json.loads(resp.read().decode("utf-8"))

            if isinstance(raw_data, list):
                df = pd.json_normalize(raw_data)
            elif isinstance(raw_data, dict):
                # Search for any list inside the dictionary
                list_keys = [k for k, v in raw_data.items() if isinstance(v, list)]
                if list_keys:
                    df = pd.json_normalize(raw_data[list_keys[0]])
                else:
                    df = pd.json_normalize([raw_data])
            else:
                return None, "API returned an unsupported primitive format."

            if df.empty:
                return None, "REST API returned an empty dataset."

            return df, None
    except Exception as e:
        return None, f"Failed to connect to REST API: {str(e)}"


