from sqlalchemy import select
from datetime import datetime, timedelta
from models.user_session import UserSession
from .base_service import BaseService

class UserSessionService(BaseService):
    """Service for handling database operations related to user sessions."""
    
    def __init__(self, db_session):
        """Initialize with a database session."""
        super().__init__()
        self.db_session = db_session
    
    def create_session(self, user_id: str, refresh_token: str, expires_at: datetime) -> UserSession:
        """
        Create a new user session in the database.
        
        Args:
            user_id: The user ID for the session
            refresh_token: The refresh token for this session
            expires_at: When the session expires
            
        Returns:
            The created UserSession object
        """
        new_session = UserSession(
            name=user_id,
            refresh_token=refresh_token,
            expires_at=expires_at
        )
        self.db_session.add(new_session)
        self.db_session.commit()
        return new_session
    
    def find_session_by_refresh_token(self, refresh_token: str) -> UserSession:
        """
        Find a user session by refresh token.
        
        Args:
            refresh_token: The refresh token to look up
            
        Returns:
            The UserSession if found and valid, None otherwise
        """
        stmt = select(UserSession).where(
            UserSession.refresh_token == refresh_token,
            UserSession.revoked == False,
            UserSession.expires_at > datetime.now()
        )
        
        result = self.db_session.execute(stmt).first()
        return result[0] if result else None
    
    def find_all_sessions_by_user_id(self, user_id: str) -> list[UserSession]:
        """
        Find all sessions for a user.
        
        Args:
            user_id: The user ID to look up
            
        Returns:
            List of UserSession objects
        """
        stmt = select(UserSession).where(
            UserSession.name == user_id,
            UserSession.revoked == False,
            UserSession.expires_at > datetime.now()
        )
        
        result = self.db_session.execute(stmt).all()
        return [row[0] for row in result] if result else []
    
    def revoke_session(self, refresh_token: str) -> bool:
        """
        Revoke a session by its refresh token.
        
        Args:
            refresh_token: The refresh token to revoke
            
        Returns:
            True if session was found and revoked, False otherwise
        """
        stmt = select(UserSession).where(UserSession.refresh_token == refresh_token)
        result = self.db_session.execute(stmt).first()
        
        if not result:
            return False
            
        session = result[0]
        session.revoked = True
        self.db_session.commit()
        return True
    
    def revoke_all_sessions_for_user(self, user_id: str) -> int:
        """
        Revoke all sessions for a user.
        
        Args:
            user_id: The user ID to revoke sessions for
            
        Returns:
            Number of sessions revoked
        """
        sessions = self.find_all_sessions_by_user_id(user_id)
        count = 0
        
        for session in sessions:
            session.revoked = True
            count += 1
            
        if count > 0:
            self.db_session.commit()
            
        return count
    
    def update_session(
            self, 
            refresh_token: str, 
            new_access_token: str, 
            new_expires_at: datetime
        ) -> bool:
        """
        Update the expiry time of a session.
        
        Args:
            refresh_token: The refresh token of the session to update
            new_expires_at: The new expiration time
            
        Returns:
            True if session was found and updated, False otherwise
        """
        session = self.find_session_by_refresh_token(refresh_token)
        if not session:
            return False
            
        session.revoked = True
        self.db_session.commit()
        return True