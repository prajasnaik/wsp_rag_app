from flask import Blueprint, send_from_directory, current_app
import os

# Create the Blueprint for main routes
main_bp = Blueprint('main', __name__)

# Serve static files (JS, CSS, assets) from the frontend build directory
@main_bp.route('/<path:path>')
def static_proxy(path):
    frontend_dir = current_app.config['FRONTEND_BUILD_DIR']
    file_path = os.path.join(frontend_dir, path)
    if os.path.isfile(file_path):
        return send_from_directory(frontend_dir, path)
    # Fallback to index.html for client-side routing
    return send_from_directory(frontend_dir, 'index.html')

# Catch-all route for the root and any other path
@main_bp.route('/', defaults={'path': ''})
@main_bp.route('/<path:path>')
def index(path):
    frontend_dir = current_app.config['FRONTEND_BUILD_DIR']
    return send_from_directory(frontend_dir, 'index.html')