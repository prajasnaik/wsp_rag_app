from sqlalchemy import create_engine
from models.user_session import UserSession
from sqlalchemy.orm import declarative_base
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
import json
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.exceptions import InvalidSignature
import secrets
import os
import base64

class AuthService:
    def __init__(self, db_session):
        self.db_session = db_session

        base_path = os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(
                            os.path.abspath(__file__)
                        )
                    )
                )

        with open(os.path.join(os.path.abspath(base_path), "private_key.pem"), "rb") as private_key_file:
            self.private_key = private_key_file.read()

        with open(os.path.join(os.path.abspath(base_path), "public_key.pem"), "rb") as public_key_file:
            self.public_key = public_key_file.read()
        
    def store_token(
        self,
        name: str,
    ) -> tuple[str, str]:
        expires_at = datetime.now() + timedelta(minutes=30)
        refresh_token = self.create_refresh_token()

        access_token = self.create_user_jwt(name, expires_at)

        new_token = UserSession(
            name=name,
            refresh_token=refresh_token,
            expires_at=expires_at
        )
        self.db_session.add(new_token)
        self.db_session.commit()

        return access_token, refresh_token
    
    def create_user_jwt(
        self,
        name: str,
        expires_at: datetime,
    ) -> str:
        """Create a JWT token including both payload and signature for later verification"""
        payload = {
            "name": name,
            "iss": "AuthService",
            "exp": expires_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        payload_json = json.dumps(payload)
        
        private_key = load_pem_private_key(self.private_key, password=None)
        # Sign the payload
        signature = private_key.sign(
            payload_json.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Create token with both payload and signature
        token_parts = {
            "payload": payload,
            "signature": base64.b64encode(signature).decode()
        }
        
        # Encode the complete token
        token = base64.b64encode(json.dumps(token_parts).encode()).decode()
        return token
    
    def validate_user_jwt(self, token: str) -> str:
        """Validate a JWT token and return the user ID if valid"""
        try:
            # Decode the token to get the parts
            token_data = json.loads(base64.b64decode(token).decode())
            
            # Extract payload and signature
            payload = token_data.get("payload")
            signature_b64 = token_data.get("signature")
            
            if not payload or not signature_b64:
                return ""
                
            # Convert payload to string for verification
            payload_str = json.dumps(payload)
            signature = base64.b64decode(signature_b64)
            
            # Check expiration
            try:
                expiry_str = payload.get("exp")
                if expiry_str:
                    expiry_time = datetime.strptime(expiry_str, '%Y-%m-%d %H:%M:%S')
                    if expiry_time < datetime.now():
                        return ""  # Token expired
            except (ValueError, TypeError):
                return ""  # Invalid date format
            
            # Verify signature
            public_key = load_pem_public_key(self.public_key)
            public_key.verify(
                signature,
                payload_str.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # If we get here, signature is valid - return the user ID
            return payload.get("name", "")
            
        except (InvalidSignature, ValueError, KeyError, base64.binascii.Error, json.JSONDecodeError) as e:
            print(f"Token validation error: {e}")
            return ""
        
    def create_refresh_token(self):
        """Create a secure random refresh token"""
        return secrets.token_urlsafe(64)


