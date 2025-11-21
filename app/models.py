from .extensions import db
from flask_login import UserMixin

# --- 1. WORK ORDERS ---
class WorkOrder(db.Model):
    __tablename__ = 'work_orders'
    # We map the internal 'rowid' to 'id' for Flask
    rowid = db.Column('rowid', db.Integer, primary_key=True)
    
    # MAPPING: Python Name = db.Column('EXACT DATABASE NAME', Type)
    work_order_no = db.Column('Št.', db.String, index=True)
    project_no = db.Column('Št.Projekta', db.String, index=True)
    project_task_no = db.Column('Št.Projektne naloge', db.String, index=True)
    description = db.Column('Opis', db.String)
    status = db.Column('Stanje', db.String)
    quantity = db.Column('Količina', db.Float)
    work_center = db.Column('Upravljalni center', db.Float)

# --- 2. COMPONENTS ---
class Component(db.Model):
    __tablename__ = 'components'
    rowid = db.Column('rowid', db.Integer, primary_key=True)
    
    item_no = db.Column('Št. Artikla', db.Float, index=True)
    description = db.Column('Opis', db.String)
    work_order_no = db.Column('DNI', db.String, index=True) # Link to WorkOrder
    quantity_needed = db.Column('Pričakovana količina', db.Float)
    quantity_remaining = db.Column('Preostala količina', db.Float)
    inventory_stock = db.Column('Zaloga', db.Float)
    shelf_code = db.Column('Šifra regala', db.String)

# --- 3. TIME ENTRIES ---
class TimeEntry(db.Model):
    __tablename__ = 'time_entries'
    rowid = db.Column('rowid', db.Integer, primary_key=True)
    
    worker_id = db.Column('Št. delavca', db.Integer)
    worker_name = db.Column('Ime delavca', db.String)
    date = db.Column('Datum knjiženja', db.String)
    work_order_no = db.Column('DNI', db.String)

# --- 4. ADMIN & NOTES (Rescued Tables) ---
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150))
    password_hash = db.Column(db.String(200))
    role = db.Column(db.String(50))

class ProjectNote(db.Model):
    __tablename__ = 'project_notes'
    # This table came from the old DB, so it might use English names
    project_task_no = db.Column(db.String, primary_key=True)
    notes = db.Column(db.Text)
    priority = db.Column(db.String)
    status = db.Column(db.String)