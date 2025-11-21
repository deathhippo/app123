from flask import Blueprint, jsonify, current_app, request
import json
import os
from .helpers import get_project_inventory_status

bp = Blueprint('layout', __name__)

@bp.route('/api/layout')
def get_layout():
    layout_data = {}
    try:
        path = current_app.config['LAYOUT_DATA_FILE_PATH']
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                layout_data = json.load(f)
        
        # Link Layout Items to Database Status
        for key, item in layout_data.items():
            if item.get('type') == 'project':
                pid = item.get('id')
                # Calculate status on the fly
                status = get_project_inventory_status(pid)
                item['db_status'] = status
                
        return jsonify(layout_data)

    except Exception as e:
        print(f"CRITICAL LAYOUT ERROR: {e}")
        # Return whatever data we managed to load, preventing the gray screen
        return jsonify(layout_data)

@bp.route('/api/save_layout', methods=['POST'])
def save_layout():
    # Simple save functionality
    try:
        new_data = request.json
        path = current_app.config['LAYOUT_DATA_FILE_PATH']
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500