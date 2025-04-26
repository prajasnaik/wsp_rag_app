from flask import Blueprint, request, current_app, jsonify
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from config import Config
from services.auth_service import AuthService
import os
from datetime import datetime, timedelta
from sqlalchemy import select

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/auth/google/callback", methods=["POST"])
def auth_callback():
    authorization_code = request.json.get("code", "")
    redirect_url = request.json.get("redirect_uri", "")
    if not authorization_code or not redirect_url:
        return jsonify({"error" : "Authorization code or Redirect URI not found"}, 400)

    client_secrets_path = os.path.join(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__))))),
        "client_secret.json"
    )
    flow = Flow.from_client_secrets_file(
        client_secrets_path,
        scopes=['https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email' ,'openid'],
        redirect_uri=redirect_url
    )

    try:
        flow.fetch_token(code=authorization_code)
        credentials = flow.credentials
    except Exception as e:
        print(f"Error fetching token: {e}")
        return jsonify({"error": "Failed to fetch token. Please check the redirect URI and authorization code."}), 400
    
    user_id = credentials.id_token

    config: Config = current_app.config.get("CONFIG")

    idinfo = id_token.verify_oauth2_token(user_id, google_requests.Request(), config.GOOGLE_OAUTH_CLIENT_ID)

    user_id = idinfo.get("sub", "")
    if not user_id:
        return jsonify({"error" : "Invalid authorization code"}), 401

    LocalSession = current_app.config.get("SESSION_LOCAL", "")
    if not LocalSession:
        return jsonify({"error" : "Some error occurred"}), 500
    
    auth_service = AuthService(LocalSession())
    try:
        access_token, refresh_token = auth_service.store_token(user_id)
        if not access_token or not refresh_token:
            return jsonify({"error", "Some error occurred"}), 500
        
        response = jsonify(
            {
            "access_token": access_token,
            "expires_in": 60 * 5
            },
        )
        response.set_cookie("access_token", access_token, httponly=True, max_age=60 * 5)
        response.set_cookie("refresh_token", refresh_token, httponly=True, max_age=60 * 60 * 24 * 7)
        return response, 200

    except Exception as e:
        print(e)
        return jsonify({"error" : "Some error occurred"}), 500

@auth_bp.route("/auth/refresh", methods=["POST"])
def refresh_token():
    """Refresh an access token using the refresh token in the cookies"""
    refresh_token = request.cookies.get("refresh_token", "")
    if not refresh_token:
        return jsonify({"error": "Refresh token not found"}), 401

    LocalSession = current_app.config.get("SESSION_LOCAL", "")
    if not LocalSession:
        return jsonify({"error": "Database session not initialized"}), 500
    
    db_session = LocalSession()
    
    from models.user_session import UserSession
    
    # Find the user session with the provided refresh token
    stmt = select(UserSession).where(
        UserSession.refresh_token == refresh_token,
        UserSession.revoked == False,
        UserSession.expires_at > datetime.now()
    )
    
    result = db_session.execute(stmt).first()
    if not result:
        return jsonify({"error": "Invalid or expired refresh token"}), 401
    
    user_session = result[0]
    
    # Create a new access token
    auth_service = AuthService(db_session)
    expires_at = datetime.now() + timedelta(minutes=30)
    access_token = auth_service.create_user_jwt(user_session.name, expires_at)
    
    # Update the expiry time of the session
    user_session.expires_at = expires_at
    db_session.commit()
    
    response = jsonify({
        "access_token": access_token,
        "expires_in": 60 * 5
    })
    
    # Set the new access token as a cookie
    response.set_cookie("access_token", access_token, httponly=True, max_age=60 * 5)
    
    return response, 200

@auth_bp.route("/auth/status", methods=["GET"])
def auth_status():
    """Check the authentication status of the user"""
    access_token = request.cookies.get("access_token", "")
    if not access_token:
        return jsonify({
            "is_authenticated": False,
            "access_token": None
        }), 200
    
    LocalSession = current_app.config.get("SESSION_LOCAL", "")
    if not LocalSession:
        return jsonify({"error": "Database session not initialized"}), 500
    
    auth_service = AuthService(LocalSession())
    user_id = auth_service.validate_user_jwt(access_token)
    
    if user_id:
        return jsonify({
            "is_authenticated": True,
            "access_token": access_token,
            "user_id": user_id
        }), 200
    
    # Try to refresh the token
    refresh_token = request.cookies.get("refresh_token", "")
    if not refresh_token:
        return jsonify({
            "is_authenticated": False,
            "access_token": None
        }), 200
    
    # Attempt token refresh logic
    # For now, we'll just return not authenticated
    return jsonify({
        "is_authenticated": False,
        "access_token": None
    }), 200

@auth_bp.route("/auth/logout", methods=["POST"])
def logout():
    """Log out the user by invalidating their refresh token"""
    refresh_token = request.cookies.get("refresh_token", "")
    
    if refresh_token:
        LocalSession = current_app.config.get("SESSION_LOCAL", "")
        if LocalSession:
            db_session = LocalSession()
            from models.user_session import UserSession
            
            # Find and revoke the session
            stmt = select(UserSession).where(UserSession.refresh_token == refresh_token)
            result = db_session.execute(stmt).first()
            
            if result:
                user_session = result[0]
                user_session.revoked = True
                db_session.commit()
    
    # Clear cookies regardless of whether the token was found
    response = jsonify({"message": "Logged out successfully"})
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    
    return response, 200


