import os
from flask import Blueprint, render_template, current_app, send_from_directory
from .helpers import get_project_statuses_from_db

bp = Blueprint('core', __name__)

@bp.route('/')
def serve_app():
    # Serve the main mobile app HTML
    # We use current_app.config['APP_ROOT'] which we restored in config.py
    return send_from_directory(current_app.config['APP_ROOT'], 'mobile_app.html')

@bp.route('/api/project_statuses')
def get_project_statuses():
    # Fetch statuses for the home page dashboard
    return get_project_statuses_from_db()

@bp.route('/<path:filename>')
def serve_static_files(filename):
    # Serve CSS/JS/HTML files from the root folder
    return send_from_directory(current_app.config['APP_ROOT'], filename)