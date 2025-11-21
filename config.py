import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATABASE_PATH = os.path.join(BASE_DIR, "master_unified.db")
PLUGINS_DIR = os.path.join(BASE_DIR, "plugins")
LAYOUT_JSON = os.path.join(BASE_DIR, "layout_data.json")

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

SECRET_KEY = "super-secret-key-change-this"
