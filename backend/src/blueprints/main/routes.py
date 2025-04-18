from flask import Blueprint, send_from_directory, current_app

# Create the Blueprint for main routes
main_bp = Blueprint('main', __name__)

@main_bp.route('/', defaults={'path': ''})
@main_bp.route('/<path:path>')
def catch_all(path):
    """
    Serve the frontend React SPA.
    This route will catch all paths and serve the React app's index.html,
    allowing React Router to handle client-side routing.
    """
    try:
        # Try to serve the requested file from the frontend build directory
        return send_from_directory(current_app.config['FRONTEND_BUILD_DIR'], path)
    except:
        # If file not found, serve index.html for client-side routing
        return send_from_directory(current_app.config['FRONTEND_BUILD_DIR'], 'index.html')