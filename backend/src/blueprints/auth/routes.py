from flask import Blueprint, request, current_app, jsonify
from config import Config
from services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/auth/google/callback", methods=["POST"])
def auth_callback():
    """Handle Google OAuth callback and create user session"""
    # Extract data from request
    authorization_code = request.json.get("code", "")
    redirect_uri = request.json.get("redirect_uri", "")
    
    # Validate request data
    if not authorization_code or not redirect_uri:
        return jsonify({"error": "Authorization code or Redirect URI not found"}), 400

    # Get database session
    LocalSession = current_app.config.get("SESSION_LOCAL")
    if not LocalSession:
        return jsonify({"error": "Database session not initialized"}), 500
    
    # Get config
    config: Config = current_app.config.get("CONFIG")
    
    # Create auth service
    auth_service = AuthService(LocalSession())
    
    try:
        # Authenticate with Google
        user_id, success, error_message = auth_service.authenticate_with_google(
            authorization_code, 
            redirect_uri,
            config.GOOGLE_OAUTH_CLIENT_ID
        )
        
        if not success:
            return jsonify({"error": error_message}), 401
        
        # Create tokens
        access_token, refresh_token, expires_at = auth_service.create_auth_tokens(user_id)
        
        # Create response
        response = jsonify({
            "access_token": access_token,
            "expires_in": 300  # 5 minutes in seconds
        })
        
        # Set cookies
        response.set_cookie("access_token", access_token, httponly=True, max_age=300)  # 5 minutes
        response.set_cookie("refresh_token", refresh_token, httponly=True, max_age=604800)  # 7 days
        
        return response, 200
        
    except Exception as e:
        print(f"Error in auth callback: {e}")
        return jsonify({"error": "Authentication failed"}), 500

@auth_bp.route("/auth/refresh", methods=["POST"])
def refresh_token():
    """Refresh an access token using the refresh token in cookies"""
    # Get refresh token from cookies
    refresh_token = request.cookies.get("refresh_token", "")
    if not refresh_token:
        return jsonify({"error": "Refresh token not found"}), 401

    # Get database session
    LocalSession = current_app.config.get("SESSION_LOCAL")
    if not LocalSession:
        return jsonify({"error": "Database session not initialized"}), 500
    
    # Create auth service
    auth_service = AuthService(LocalSession())
    
    # Refresh the token
    access_token, refresh_token, expires_at, success, error_message = auth_service.refresh_auth_token(refresh_token)
    
    if not success:
        return jsonify({"error": error_message}), 401
    
    # Create response
    response = jsonify({
        "access_token": access_token,
        "expires_in": 300  # 5 minutes in seconds
    })
    
    # Set new access token cookie
    response.set_cookie("access_token", access_token, httponly=True, max_age=300)  # 5 minutes
    response.set_cookie("refresh_token", refresh_token, httponly=True, max_age=604800)
    return response, 200

@auth_bp.route("/auth/status", methods=["GET"])
def auth_status():
    """Check the authentication status of the user"""
    # Get access token from cookies
    access_token = request.cookies.get("access_token", "")
    
    if not access_token:
        return jsonify({
            "is_authenticated": False,
            "access_token": None
        }), 200
    
    # Get database session
    LocalSession = current_app.config.get("SESSION_LOCAL")
    if not LocalSession:
        return jsonify({"error": "Database session not initialized"}), 500
    
    # Create auth service
    auth_service = AuthService(LocalSession())
    
    # Validate the token
    user_id, is_valid = auth_service.validate_access_token(access_token)
    
    if is_valid:
        return jsonify({
            "is_authenticated": True,
            "access_token": access_token,
            "user_id": user_id
        }), 200
    
    # If access token is invalid, try to auto-refresh using refresh token
    refresh_token = request.cookies.get("refresh_token", "")
    if not refresh_token:
        return jsonify({
            "is_authenticated": False,
            "access_token": None
        }), 200
    
    # Try to refresh the token
    access_token, expires_at, success, _ = auth_service.refresh_auth_token(refresh_token)
    
    if success:
        response = jsonify({
            "is_authenticated": True,
            "access_token": access_token,
            "user_id": user_id
        })
        response.set_cookie("access_token", access_token, httponly=True, max_age=300)  # 5 minutes
        return response, 200
    
    # If refresh fails, user is not authenticated
    return jsonify({
        "is_authenticated": False,
        "access_token": None
    }), 200

@auth_bp.route("/auth/logout", methods=["POST"])
def logout():
    """Log out the user by invalidating their refresh token"""
    # Get refresh token from cookies
    refresh_token = request.cookies.get("refresh_token", "")
    
    if refresh_token:
        # Get database session
        LocalSession = current_app.config.get("SESSION_LOCAL")
        if LocalSession:
            # Create auth service
            auth_service = AuthService(LocalSession())
            
            # Revoke the session
            auth_service.logout(refresh_token)
    
    # Clear cookies regardless of whether the token was found
    response = jsonify({"message": "Logged out successfully"})
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    
    return response, 200


