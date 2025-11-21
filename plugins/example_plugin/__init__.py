PLUGIN_META={
    "name":"Example Plugin",
    "title":"Example Plugin",
    "description":"Demo plugin",
    "version":"1.0"
}

def register(app):
    from flask import Blueprint, jsonify
    bp=Blueprint("example_plugin_bp",__name__,url_prefix="/example_plugin")
    @bp.route("/hello")
    def hello():
        return jsonify({"message":"Hello from Example Plugin!"})
    app.register_blueprint(bp)
