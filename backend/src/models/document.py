from datetime import datetime
from uuid import uuid4
from typing import Any  

class Document:
    """
    Model representing a document in the system.
    """
    def __init__(self, text, metadata=None, id=None):
        self.id = id or str(uuid4())
        self.text = text
        self.metadata = metadata or {}
        self.created_at = datetime.now().isoformat()
        
    def to_dict(self):
        """
        Convert the document to a dictionary.
        """
        return {
            'id': self.id,
            'text': self.text,
            'metadata': self.metadata,
            'created_at': self.created_at
        }
        
    @classmethod
    def from_dict(
        cls, 
        data: dict[str, Any]
    ):
        """
        Create a Document instance from a dictionary.
        """
        doc = cls(
            text=data.get('text', ''),
            metadata=data.get('metadata', {}),
            id=data.get('id')
        )
        doc.created_at = data.get('created_at', doc.created_at)
        return doc