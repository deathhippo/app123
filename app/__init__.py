import os
from flask import Flask
from config import PLUGINS_DIR, DATABASE_PATH, UPLOAD_FOLDER, LAYOUT_JSON, SECRET_KEY

def create_app():
    # We rename 'app' to 'flask_app' here to avoid shadowing issues
    flask_app = Flask(__name__, template_folder="../", static_folder="../")
    
    flask_app.config["SECRET_KEY"] = SECRET_KEY
    flask_app.config["PLUGINS_DIR"] = PLUGINS_DIR
    flask_app.config["DATABASE_PATH"] = DATABASE_PATH
    flask_app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    flask_app.config["LAYOUT_JSON"] = LAYOUT_JSON
    
    # FIX: Define the PLUGINS_STATE_FILE path explicitly
    # This points to 'plugins_state.json' in the main folder (one level up from this file)
    flask_app.config["PLUGINS_STATE_FILE"] = os.path.join(os.path.dirname(os.path.dirname(__file__)), "plugins_state.json")

    # We import views here using the app context
    with flask_app.app_context():
        import app.views_core
        import app.views_layout
        import app.views_project
        import app.views_admin
        import app.views_plugins
        import app.views_plugins_ui
        import app.views_parts
        import app.views_timetable

    return flask_app