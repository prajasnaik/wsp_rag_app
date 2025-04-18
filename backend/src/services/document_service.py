import os
import chromadb
from ..config import Config
from ..models import Document
from .base_service import BaseService

class DocumentService(BaseService):
    """
    Service for handling document operations using ChromaDB.
    """
    def __init__(self):
        """
        Initialize the document service with ChromaDB connection.
        """
        super().__init__()
        self.client = chromadb.PersistentClient(path=Config.CHROMA_PERSIST_DIRECTORY)
        
        # Create collection if it doesn't exist
        try:
            self.collection = self.client.get_collection("documents")
        except ValueError:
            self.collection = self.client.create_collection("documents")
    
    def add_document(self, document):
        """
        Add a document to the ChromaDB collection.
        """
        self.collection.add(
            ids=[document.id],
            documents=[document.text],
            metadatas=[document.metadata]
        )
        return document
    
    def get_document(self, doc_id):
        """
        Get a document from ChromaDB by ID.
        """
        result = self.collection.get(ids=[doc_id])
        if not result["ids"]:
            return None
            
        doc_data = {
            "id": result["ids"][0],
            "text": result["documents"][0],
            "metadata": result["metadatas"][0],
        }
        return Document.from_dict(doc_data)
    
    def search_documents(self, query, limit=5):
        """
        Search for documents based on a query string.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=limit
        )
        
        documents = []
        if results["ids"]:
            for i in range(len(results["ids"][0])):
                doc_data = {
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i]
                }
                documents.append(Document.from_dict(doc_data))
                
        return documents
        
    def list_documents(self, limit=100):
        """
        List all documents in the collection.
        """
        results = self.collection.get(limit=limit)
        
        documents = []
        if results["ids"]:
            for i in range(len(results["ids"])):
                doc_data = {
                    "id": results["ids"][i],
                    "text": results["documents"][i],
                    "metadata": results["metadatas"][i]
                }
                documents.append(Document.from_dict(doc_data))
                
        return documents
        
    def delete_document(self, doc_id):
        """
        Delete a document from ChromaDB by ID.
        """
        try:
            self.collection.delete(ids=[doc_id])
            return True
        except Exception:
            return False