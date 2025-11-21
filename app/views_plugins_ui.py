from flask import Blueprint, send_from_directory, current_app
from .auth import login_required, admin_required

bp = Blueprint('plugins_ui', __name__)

@bp.route('/plugins')
@login_required
@admin_required
def serve_plugins_page():
    return send_from_directory(current_app.config['APP_ROOT'], 'plugin_manager.html')
