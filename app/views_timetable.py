from flask import Blueprint, render_template, jsonify, request
from . import time_calculator # <--- FIX: Added dot for relative import
from .extensions import db

bp = Blueprint('timetable', __name__)

@bp.route('/planning')
def planning():
    return render_template('planning.html')

@bp.route('/api/planning_data')
def get_planning_data():
    try:
        # This uses the logic from your time_calculator.py
        data = time_calculator.get_planning_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500