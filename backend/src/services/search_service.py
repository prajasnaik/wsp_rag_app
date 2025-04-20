from models.document import Document
from .base_service import BaseService
import chromadb
from config import Config



class SearchService(BaseService):
    def __init__(self):
        super().__init__()
        self.client = chromadb.PersistentClient(Config.CHROMA_PERSIST_DIRECTORY)
        try:
            self.collection = self.client.get_or_create_collection("documents")
        except chromadb.errors.NotFoundError:
            self.collection = self.client.create_collection("documents")

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
