from flask import Blueprint, jsonify, current_app
from .auth import admin_required
# NOTE: we DO NOT import reload_plugins here to avoid registering blueprints after first request.
from .plugin_system import get_installed_plugins, set_plugin_enabled

bp = Blueprint('plugins_api', __name__, url_prefix='/api/plugins')

@bp.route('', methods=['GET'])
@admin_required
def list_plugins():
    return jsonify(get_installed_plugins(current_app))

@bp.route('/<name>/enable', methods=['POST'])
@admin_required
def enable_plugin(name):
    state = set_plugin_enabled(current_app, name, True)
    # Do NOT call reload here; Flask 3.x forbids registering blueprints after the first request.
    # Changes take effect on next server restart.
    return jsonify({
        "status": "ok",
        "plugin": name,
        "enabled": state.get("enabled", False),
        "message": "Enabled in state file. Please restart the server to apply."
    })

@bp.route('/<name>/disable', methods=['POST'])
@admin_required
def disable_plugin(name):
    state = set_plugin_enabled(current_app, name, False)
    return jsonify({
        "status": "ok",
        "plugin": name,
        "enabled": state.get("enabled", False),
        "message": "Disabled in state file. Fully unloads on next restart."
    })

@bp.route('/reload', methods=['POST'])
@admin_required
def reload_all():
    # Hot reloading is intentionally disabled to avoid Flask 3.x runtime error:
    # "register_blueprint can no longer be called after the first request"
    return jsonify({
        "status": "noop",
        "message": "Hot reload disabled. Restart the server to apply plugin changes."
    }), 200
