from functools import wraps
from flask import request, jsonify, current_app
from services.auth_service import AuthService
import asyncio
from functools import wraps
from flask import request, jsonify, current_app

def validate_auth_token(func):
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        auth_token = request.cookies.get('access_token')
        if not auth_token:
            return jsonify({"error": "Authentication token is missing"}), 401
        
        # Get database session
        LocalSession = current_app.config.get("SESSION_LOCAL")
        if not LocalSession:
            return jsonify({"error": "Database session not initialized"}), 500
        
        auth_service = AuthService(LocalSession())

        if not auth_service.validate_access_token(auth_token)[1]:
            return jsonify({"error": "Invalid or expired authentication token"}), 401
        
        return await func(*args, **kwargs)

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        auth_token = request.cookies.get('auth_token')
        if not auth_token:
            return jsonify({"error": "Authentication token is missing"}), 401
        
        LocalSession = current_app.config.get("SESSION_LOCAL")
        if not LocalSession:
            return jsonify({"error": "Database session not initialized"}), 500
        
        auth_service = AuthService(LocalSession())

        if not auth_service.validate_access_token(auth_token)[1]:
            return jsonify({"error": "Invalid or expired authentication token"}), 401
        
        return func(*args, **kwargs)

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
