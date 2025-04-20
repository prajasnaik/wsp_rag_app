import os
import chromadb
import chromadb.errors
from config import Config
from models import Document
from .base_service import BaseService
from .pdf_parser import PDFParser
from werkzeug.datastructures import FileStorage
import uuid

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
        self.parser = PDFParser()
        # Create collection if it doesn't exist
        try:
            self.collection = self.client.get_or_create_collection("documents")
        except chromadb.errors.NotFoundError:
            self.collection = self.client.create_collection("documents")
    
    def add_document(
            self, 
            document: Document
        ) -> Document:
        """
        Add a document to the ChromaDB collection.
        """
        self.collection.add(
            ids=[document.id],
            documents=[document.text],
            metadatas=[document.metadata]
        )
        return document
    
    def get_document(
            self, 
            doc_id: str
        ) -> Document:
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
    
    def search_documents(
            self, 
            query: str, 
            limit: int=5
        ) -> list[Document]:
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
        
    def list_documents(
            self, 
            limit: int=100
        ):

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
        
    def delete_document(
            self, 
            doc_id: str
        ):
        """
        Delete a document from ChromaDB by ID.
        """
        try:
            self.collection.delete(ids=[doc_id])
            return True
        except Exception:
            return False
        
    def upload_document(
        self,
        file: FileStorage
    ):
        extracted_text = self.parser.parse(file)
        for metadata, extracted_chunks in extracted_text:
            for chunk_no, chunk in enumerate(extracted_chunks):
                metadata["page_no"] += 1
                metadata["chunk_no"] = chunk_no + 1
                id = str(uuid.uuid4())
                document = Document(chunk, metadata, id)
                self.add_document(document)
        
        