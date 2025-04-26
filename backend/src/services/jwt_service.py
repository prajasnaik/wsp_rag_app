from datetime import datetime
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from cryptography.exceptions import InvalidSignature
import json
import base64
import os
import secrets
from .base_service import BaseService

class JWTService(BaseService):
    """Service for handling JWT token operations like signing and verification."""
    
    def __init__(self):
        """Initialize JWT service with private and public keys."""
        super().__init__()
        
        # Find base path for the keys
        base_path = os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(
                            os.path.abspath(__file__)
                        )
                    )
                )

        # Load the private and public keys
        with open(os.path.join(os.path.abspath(base_path), "private_key.pem"), "rb") as private_key_file:
            self.private_key = private_key_file.read()

        with open(os.path.join(os.path.abspath(base_path), "public_key.pem"), "rb") as public_key_file:
            self.public_key = public_key_file.read()
    
    def create_access_token(self, user_id: str, expires_at: datetime) -> str:
        """
        Create a JWT token including both payload and signature for later verification
        
        Args:
            user_id: The user ID to encode in the token
            expires_at: When the token should expire
            
        Returns:
            A base64 encoded token string
        """
        payload = {
            "name": user_id,
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
    
    def validate_token(self, token: str) -> str:
        """
        Validate a JWT token and return the user ID if valid
        
        Args:
            token: The token to validate
            
        Returns:
            The user ID if valid, empty string otherwise
        """
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
    
    def create_refresh_token(self) -> str:
        """
        Create a secure random refresh token
        
        Returns:
            A secure random token string
        """
        return secrets.token_urlsafe(64)