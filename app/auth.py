import os
import sqlite3
from flask import (
    Blueprint, jsonify, request, session, redirect, url_for, current_app
)
from functools import wraps
from werkzeug.security import check_password_hash
from .db import get_db_connection

bp = Blueprint('auth', __name__, url_prefix='/api')

# --- Decorators ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            # Allow login + public planning endpoints without session
            if request.path.startswith('/api/login') or request.path == '/planning' or request.path == '/api/planning_data':
                return f(*args, **kwargs)
            if request.path.startswith('/api/'):
                return jsonify({"error": "Authentication required"}), 401
            return redirect(url_for('core.serve_app'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return jsonify({"error": "Authentication required"}), 401
        if session.get('role') != 'admin':
            return jsonify({"error": "Admin privileges required"}), 403
        return f(*args, **kwargs)
    return decorated_function

# --- Auth Routes ---
@bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('core.serve_app'))

@bp.route('/login', methods=['POST'])
def web_app_login():
    data = request.json or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''
    if not username or not password:
        return jsonify({"status": "error", "message": "Missing credentials"}), 400

    conn = None
    try:
        db_path = current_app.config['VELIKA_MONTAZA_DB_PATH']
        conn = get_db_connection(db_path)
        if conn is None:
            raise sqlite3.OperationalError(f"Could not connect to '{os.path.basename(db_path)}' for login.")

        user_row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user_row and check_password_hash(user_row['password_hash'], password):
            session['logged_in'] = True
            session['username'] = user_row['username']
            session['role'] = user_row['role']
            return jsonify({"status": "success", "role": user_row['role'], "username": user_row['username']})
        return jsonify({"status": "error", "message": "Invalid Credentials."}), 401
    except Exception:
        return jsonify({"status": "error", "message": "Server error during login."}), 500
    finally:
        if conn:
            conn.close()
