import sqlite3
import os
from flask import current_app

def get_db_connection(db_file_path):
    if not os.path.exists(db_file_path):
        print(f"ERROR: Database file not found at '{db_file_path}'.")
        if db_file_path == current_app.config['CAS_DATABASE_FILE_PATH']:
            print(f"Warning: '{os.path.basename(db_file_path)}' not found. Worker names cannot be fetched.")
            return None
        if db_file_path == current_app.config.get('CAS_RAZPOREDJEN_DB_PATH'):
            print(f"Warning: '{os.path.basename(db_file_path)}' not found. Planned times cannot be fetched.")
            return None
        raise FileNotFoundError(f"Database file not found at '{db_file_path}'.")
    try:
        conn = sqlite3.connect(
            db_file_path,
            check_same_thread=False,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.OperationalError as e:
        print(f"ERROR: Could not connect to database '{db_file_path}': {e}")
        if db_file_path == current_app.config['CAS_DATABASE_FILE_PATH']:
            print("Warning: Could not connect. Worker names cannot be fetched.")
            return None
        if db_file_path == current_app.config.get('CAS_RAZPOREDJEN_DB_PATH'):
            print("Warning: Could not connect. Planned times cannot be fetched.")
            return None
        raise e

def init_velika_montaza_db():
    """Initializes/updates schema for velika_montaza.db if tables/columns are missing."""
    conn = None
    try:
        db_path = current_app.config['VELIKA_MONTAZA_DB_PATH']
        # Create file if it doesn't exist
        if not os.path.exists(db_path):
            open(db_path, 'a').close()
        conn = get_db_connection(db_path)
        if conn is None:
            print(f"ERROR: Cannot initialize '{os.path.basename(db_path)}' as it could not be connected to.")
            return

        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_notes (
                project_task_no TEXT PRIMARY KEY,
                notes TEXT,
                electrification_notes TEXT,
                control_notes TEXT,
                electrification_status TEXT,
                control_status TEXT,
                electrification_completed_at TEXT,
                control_completed_at TEXT,
                packaging_status TEXT,
                priority TEXT,
                pause_status TEXT,
                last_note_updated_at TEXT,
                last_dni_updated_at TEXT
            )
        """)
        # backfill new columns if older DBs are present
        for col in ("priority TEXT", "pause_status TEXT", "last_note_updated_at TEXT", "last_dni_updated_at TEXT"):
            name = col.split()[0]
            try:
                cursor.execute(f"SELECT {name} FROM project_notes LIMIT 1")
            except sqlite3.OperationalError:
                cursor.execute(f"ALTER TABLE project_notes ADD COLUMN {col}")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dni_status (
                work_order_no TEXT PRIMARY KEY,
                project_task_no TEXT NOT NULL,
                description TEXT,
                is_completed BOOLEAN NOT NULL CHECK (is_completed IN (0, 1))
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_task_no TEXT NOT NULL,
                filename TEXT NOT NULL,
                uploaded_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('admin', 'viewer'))
            )
        """)

        conn.commit()
        print("Velika Montaza database schema is verified.")
    except sqlite3.OperationalError as e:
        print(f"ERROR initializing Velika Montaza database: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during Velika Montaza DB initialization: {e}")
    finally:
        if conn:
            conn.close()
