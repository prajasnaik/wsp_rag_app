from datetime import datetime, timedelta
from .base_service import BaseService
from .jwt_service import JWTService
from .user_session_service import UserSessionService
from google.oauth2 import id_token
from google.auth.transport import requests
from google_auth_oauthlib.flow import Flow
import os

class AuthService(BaseService):
    """Service for handling authentication logic."""

    def __init__(self, db_session):
        """Initialize the auth service with necessary dependencies."""
        super().__init__()
        self.user_session_service = UserSessionService(db_session)
        self.jwt_service = JWTService()
        self.db_session = db_session

    def authenticate_with_google(self, authorization_code: str, redirect_uri: str, client_id: str) -> tuple[str, bool, str]:
        """
        Authenticate a user with Google OAuth.
        
        Args:
            authorization_code: The authorization code from OAuth flow
            redirect_uri: The redirect URI used in the OAuth flow
            client_id: The Google OAuth client ID
            
        Returns:
            Tuple of (user_id, success, error_message)
        """
        try:
            # Find path to client_secret.json
            base_path = os.path.dirname(
                os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__))
                )
            )
            client_secrets_path = os.path.join(base_path, "client_secret.json")
            
            # Create OAuth flow and exchange code for token
            flow = Flow.from_client_secrets_file(
                client_secrets_path,
                scopes=['https://www.googleapis.com/auth/userinfo.profile', 
                        'https://www.googleapis.com/auth/userinfo.email', 
                        'openid'],
                redirect_uri=redirect_uri
            )
            
            flow.fetch_token(code=authorization_code)
            credentials = flow.credentials
            
            # Verify ID token
            id_info = id_token.verify_oauth2_token(
                credentials.id_token, 
                requests.Request(), 
                client_id
            )
            
            # Extract user ID from token
            user_id = id_info.get("sub")
            if not user_id:
                return "", False, "Invalid authorization code"
            
            return user_id, True, ""
            
        except Exception as e:
            return "", False, str(e)
            
    def create_auth_tokens(self, user_id: str) -> tuple[str, str, datetime]:
        """
        Create access and refresh tokens for a user.
        
        Args:
            user_id: The user ID to create tokens for
            
        Returns:
            Tuple of (access_token, refresh_token, expires_at)
        """
        # Create expiry time for tokens
        expires_at = datetime.now() + timedelta(minutes=30)
        
        # Generate a refresh token
        refresh_token = self.jwt_service.create_refresh_token()
        
        # Create access token
        access_token = self.jwt_service.create_access_token(user_id, expires_at)
        
        # Store the refresh token in the database
        self.user_session_service.create_session(user_id, refresh_token, expires_at)
        
        return access_token, refresh_token, expires_at
    
    def refresh_auth_token(self, refresh_token: str) -> tuple[str, datetime, bool, str]:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: The refresh token to use
            
        Returns:
            Tuple of (access_token, expires_at, success, error_message)
        """
        # Find the user session
        session = self.user_session_service.find_session_by_refresh_token(refresh_token)
        if not session:
            return "", datetime.now(), False, "Invalid or expired refresh token"
        
        # Create new expiry time
        expires_at = datetime.now() + timedelta(minutes=30)
        
        # Generate new access token
        access_token = self.jwt_service.create_access_token(session.name, expires_at)
        
        # Update the session expiry
        self.user_session_service.update_session_expiry(refresh_token, expires_at)
        
        return access_token, expires_at, True, ""
    
    def validate_access_token(self, access_token: str) -> tuple[str, bool]:
        """
        Validate an access token.
        
        Args:
            access_token: The token to validate
            
        Returns:
            Tuple of (user_id, is_valid)
        """
        user_id = self.jwt_service.validate_token(access_token)
        return user_id, bool(user_id)
    
    def logout(self, refresh_token: str) -> bool:
        """
        Log out a user by revoking their refresh token.
        
        Args:
            refresh_token: The refresh token to revoke
            
        Returns:
            True if session was revoked, False otherwise
        """
        return self.user_session_service.revoke_session(refresh_token)
    
    def logout_all_sessions(self, user_id: str) -> int:
        """
        Log out all sessions for a user.
        
        Args:
            user_id: The user ID to log out
            
        Returns:
            Number of sessions revoked
        """
        return self.user_session_service.revoke_all_sessions_for_user(user_id)


