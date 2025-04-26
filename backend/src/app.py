from flask import Flask
from flask_cors import CORS

from blueprints.api.routes import api_bp, setup_application  # Assuming you have a blueprint in routes.py
from blueprints.main import main_bp
from blueprints.auth.routes import auth_bp
from models.base_model import Base, init_db
from models.user_session import UserSession

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes

    # Set the directory for the built frontend (React) app
    import os
    frontend_build_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../frontend/dist'))
    app.config['FRONTEND_BUILD_DIR'] = frontend_build_dir

    # Register blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    
    # Set up the application context
    with app.app_context():
        setup_application()
        init_db(Base)
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)