from .extensions import db
from .models import WorkOrder, ProjectNote

# --- 1. GLOBAL STATUS FETCH (Fixes Core Page Crash) ---
def get_project_statuses_from_db():
    """
    Fetches statuses for ALL projects. Used by the Home Page.
    """
    try:
        # Get unique project IDs from the WorkOrder table
        projects = db.session.query(WorkOrder.project_task_no).distinct().all()
        
        statuses = {}
        for proj in projects:
            p_id = proj[0] # Extract string from tuple
            if p_id:
                statuses[p_id] = get_project_inventory_status(p_id)
        return statuses
    except Exception as e:
        print(f"⚠️ Error fetching global statuses: {e}")
        return {}

# --- 2. SINGLE PROJECT STATUS (Fixes Layout Page) ---
def get_project_inventory_status(project_id):
    """
    Calculates % complete for a single project.
    """
    try:
        # Query using the SQLAlchemy Model
        orders = WorkOrder.query.filter_by(project_task_no=project_id).all()
        
        total = len(orders)
        if total == 0:
            # Check if it's in notes even if no work orders exist
            note = ProjectNote.query.get(project_id)
            status_text = note.status if note and note.status else "No Data"
            return {"status": status_text, "percentage": 0, "total": 0, "completed": 0}

        completed = 0
        for wo in orders:
            # Check for various completion keywords (Slovenian & English)
            s = str(wo.status).lower() if wo.status else ""
            if s in ['zaključeno', 'completed', 'finished', 'izdano', 'closed', 'potrjeno']:
                completed += 1
        
        percent = (completed / total) * 100
        
        # Logic for text status
        if percent == 100: status_text = "Finished"
        elif percent > 0: status_text = "In Progress"
        else: status_text = "Planned"
        
        return {
            "status": status_text,
            "percentage": round(percent, 1),
            "total": total,
            "completed": completed
        }

    except Exception as e:
        print(f"⚠️ Helper Error for {project_id}: {e}")
        return {"status": "Error", "percentage": 0, "error": str(e)}

# --- 3. PERMISSIONS ---
def check_layout_item_ownership(item_id, layout_data, username):
    return None, None 

# --- 4. UPDATES ---
def update_project_status(project_id, field, value):
    try:
        note = ProjectNote.query.get(project_id)
        if not note:
            note = ProjectNote(project_task_no=project_id)
            db.session.add(note)
        
        if field == 'priority': note.priority = value
        elif field == 'pause_status': note.status = value
            
        db.session.commit()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500