from flask import Flask
from flask_cors import CORS

from blueprints.api.routes import api_bp, setup_application  # Assuming you have a blueprint in routes.py
from blueprints.main import main_bp

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    
    # Register blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(main_bp)
    
    # Set up the application context
    with app.app_context():
        setup_application()
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)