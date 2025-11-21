from app import create_app
from app.plugin_system import load_plugins

app = create_app()

with app.app_context():
    load_plugins(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
