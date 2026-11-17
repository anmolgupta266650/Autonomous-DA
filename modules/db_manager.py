import os
import io
import json
import sqlite3
import datetime
import hashlib
import pandas as pd
from typing import List, Dict, Tuple, Optional

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "projects.db")


def get_db_connection():
    """Initializes and returns a connection to the SQLite persistent database."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    """Secure SHA-256 password hashing."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verifies a plain password against stored hash."""
    return hash_password(password) == hashed


def seed_default_users():
    """Initializes standard enterprise demo credentials across all functional roles."""
    defaults = [
        ("admin", "admin123", "System Administrator", "admin"),
        ("cfo_accountant", "tally123", "Chief Financial Officer", "accountant"),
        ("researcher", "science123", "Lead Research Scientist", "researcher"),
        ("executive", "exec123", "Executive Board Member", "viewer")
    ]
    conn = get_db_connection()
    cursor = conn.cursor()
    for username, pwd, full_name, role in defaults:
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
                (username, hash_password(pwd), full_name, role)
            )
    conn.commit()
    conn.close()


def init_db():
    """Creates the necessary relational tables if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Projects Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            current_stage TEXT DEFAULT 'Raw Upload'
        )
    """)

    # Checkpoints / Datasets Table (holds data for multi-stage pipeline)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checkpoints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,
            stage_name TEXT NOT NULL,
            description TEXT,
            data_json TEXT NOT NULL,
            row_count INTEGER,
            col_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)

    # Audit Logs Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,
            action TEXT NOT NULL,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)

    # Research Papers Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,
            title TEXT NOT NULL,
            paper_content TEXT NOT NULL,
            statistical_summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        )
    """)

    # Users Table for RBAC Authentication
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    seed_default_users()


init_db()


def list_projects() -> List[Dict]:
    """Retrieves all active projects ordered by latest update."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects ORDER BY updated_at DESC")
    rows = cursor.fetchall()
    projects = [dict(row) for row in rows]
    conn.close()
    return projects


def create_project(project_id: str, name: str, description: str = "") -> bool:
    """Creates a new project in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute(
            "INSERT INTO projects (id, name, description, created_at, updated_at, current_stage) VALUES (?, ?, ?, ?, ?, ?)",
            (project_id, name, description, now, now, "Raw Upload")
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def save_checkpoint(project_id: str, stage_name: str, df: pd.DataFrame, description: str = "") -> int:
    """
    Saves a DataFrame as a persistent checkpoint in the database.
    Stores the serialized JSON table so it can be restored on demand.
    """
    if df is None:
        return -1

    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Serialize dataframe to json (orient='split' preserves index and column data types)
    data_json = df.to_json(orient="split", date_format="iso")
    row_count, col_count = df.shape

    cursor.execute(
        """
        INSERT INTO checkpoints (project_id, stage_name, description, data_json, row_count, col_count, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (project_id, stage_name, description, data_json, row_count, col_count, now)
    )
    checkpoint_id = cursor.lastrowid

    # Update project current_stage and updated_at
    cursor.execute(
        "UPDATE projects SET current_stage = ?, updated_at = ? WHERE id = ?",
        (stage_name, now, project_id)
    )

    # Log action
    cursor.execute(
        "INSERT INTO audit_logs (project_id, action, details, created_at) VALUES (?, ?, ?, ?)",
        (project_id, f"Saved Checkpoint: {stage_name}", description or f"Shape: {row_count}x{col_count}", now)
    )

    conn.commit()
    conn.close()
    return checkpoint_id


def list_checkpoints(project_id: str) -> List[Dict]:
    """Retrieves all checkpoints saved for a specific project."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, project_id, stage_name, description, row_count, col_count, created_at FROM checkpoints WHERE project_id = ? ORDER BY id ASC",
        (project_id,)
    )
    rows = cursor.fetchall()
    checkpoints = [dict(row) for row in rows]
    conn.close()
    return checkpoints


def load_checkpoint(checkpoint_id: int) -> Optional[Tuple[pd.DataFrame, Dict]]:
    """Loads a specific checkpoint DataFrame and its metadata from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM checkpoints WHERE id = ?",
        (checkpoint_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    meta = dict(row)
    data_json = meta.pop("data_json")
    try:
        df = pd.read_json(io.StringIO(data_json), orient="split")
        return df, meta
    except Exception as e:
        print(f"Error loading checkpoint {checkpoint_id}: {e}")
        return None


def get_latest_checkpoint(project_id: str) -> Optional[Tuple[pd.DataFrame, Dict]]:
    """Retrieves the most recent checkpoint for a given project."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM checkpoints WHERE project_id = ? ORDER BY id DESC LIMIT 1",
        (project_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    meta = dict(row)
    data_json = meta.pop("data_json")
    try:
        df = pd.read_json(io.StringIO(data_json), orient="split")
        return df, meta
    except Exception:
        return None


def delete_project(project_id: str) -> bool:
    """Deletes a project and cascades deletion to checkpoints, logs, and papers."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    cursor.execute("DELETE FROM checkpoints WHERE project_id = ?", (project_id,))
    cursor.execute("DELETE FROM audit_logs WHERE project_id = ?", (project_id,))
    cursor.execute("DELETE FROM research_papers WHERE project_id = ?", (project_id,))
    conn.commit()
    conn.close()
    return True


def save_research_paper(project_id: str, title: str, content: str, stat_summary: dict = None) -> int:
    """Stores an auto-generated research paper in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    stat_json = json.dumps(stat_summary or {})
    cursor.execute(
        "INSERT INTO research_papers (project_id, title, paper_content, statistical_summary) VALUES (?, ?, ?, ?)",
        (project_id, title, content, stat_json)
    )
    paper_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return paper_id


def list_research_papers(project_id: str) -> List[Dict]:
    """Retrieves all generated research papers for a project."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, project_id, title, paper_content, statistical_summary, created_at FROM research_papers WHERE project_id = ? ORDER BY id DESC",
        (project_id,)
    )
    rows = cursor.fetchall()
    papers = [dict(row) for row in rows]
    conn.close()
    return papers


# ==============================================================
# ENTERPRISE RBAC & AUTHENTICATION SUBSYSTEM
# ==============================================================

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """Authenticates credentials against database and returns user profile if valid."""
    if not username or not password:
        return None
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, password_hash, full_name, role FROM users WHERE username = ?",
        (username.strip().lower(),)
    )
    row = cursor.fetchone()
    conn.close()
    if row and verify_password(password, row["password_hash"]):
        u_dict = dict(row)
        u_dict.pop("password_hash")
        return u_dict
    return None


def create_user(username: str, password: str, full_name: str, role: str) -> bool:
    """Creates a new user profile with specified role."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
            (username.strip().lower(), hash_password(password), full_name.strip(), role)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def list_users() -> List[Dict]:
    """Lists all registered users in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, full_name, role, created_at FROM users ORDER BY id ASC")
    rows = cursor.fetchall()
    users = [dict(row) for row in rows]
    conn.close()
    return users
