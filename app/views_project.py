import os
from flask import Blueprint, jsonify, request
from .extensions import db, cache
from .models import WorkOrder, Component, TimeEntry, ProjectNote

bp = Blueprint('project', __name__, url_prefix='/api')

@bp.route('/project/<project_id>/work_orders')
@cache.cached(timeout=60, query_string=True)
def get_project_work_orders(project_id):
    try:
        orders = WorkOrder.query.filter_by(project_task_no=project_id).all()
        result = []
        for wo in orders:
            is_completed = wo.status in ['Zaključeno', 'Completed', 'Finished']
            result.append({
                "work_order_no": wo.work_order_no,
                "description": wo.description,
                "status": wo.status,
                "quantity": wo.quantity,
                "is_completed": is_completed,
                "completion_source": "auto" if is_completed else "none"
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/project/<project_id>/detailed_missing_parts')
def get_project_detailed_missing_parts(project_id):
    try:
        # Logic: Remaining > 0 AND Inventory <= 0
        components = Component.query.filter_by(project_task_no=project_id).all()
        missing = []
        for comp in components:
            if (comp.quantity_remaining or 0) > 0 and (comp.inventory_stock or 0) <= 0:
                missing.append({
                    "item_no": comp.item_no,
                    "description": comp.description,
                    "sifra_regala": comp.shelf_code or "N/A", # FIX: Maps to frontend key
                    "quantity_needed": comp.quantity_remaining
                })
        return jsonify(missing)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/project/<project_id>/detailed_arrived_parts')
def get_project_detailed_arrived_parts(project_id):
    try:
        # Logic: Inventory > 0
        components = Component.query.filter_by(project_task_no=project_id).all()
        arrived = []
        for comp in components:
            if (comp.inventory_stock or 0) > 0:
                arrived.append({
                    "item_no": comp.item_no,
                    "description": comp.description,
                    "sifra_regala": comp.shelf_code or "N/A", # FIX: Maps to frontend key
                    "quantity_needed": comp.quantity_remaining
                })
        return jsonify(arrived)
    except Exception as e:
        return jsonify({"error": str(e)}), 500