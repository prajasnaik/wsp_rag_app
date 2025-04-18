from flask import request, jsonify
from ....models import Document
from ....services import DocumentService, RAGService

document_service = DocumentService()
rag_service = RAGService()

def get_documents():
    """
    Get all documents or search for documents.
    """
    query = request.args.get('query')
    
    if query:
        # Search documents by query
        documents = document_service.search_documents(query)
    else:
        # Get all documents
        documents = document_service.list_documents()
        
    return jsonify({
        "documents": [doc.to_dict() for doc in documents]
    }), 200

def get_document(doc_id):
    """
    Get a specific document by ID.
    """
    document = document_service.get_document(doc_id)
    
    if not document:
        return jsonify({"error": "Document not found"}), 404
        
    return jsonify(document.to_dict()), 200

def create_document():
    """
    Create a new document.
    """
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({"error": "Text is required"}), 400
        
    document = Document(
        text=data['text'],
        metadata=data.get('metadata', {})
    )
    
    document = document_service.add_document(document)
    return jsonify(document.to_dict()), 201

def delete_document(doc_id):
    """
    Delete a document by ID.
    """
    success = document_service.delete_document(doc_id)
    
    if not success:
        return jsonify({"error": "Document not found or could not be deleted"}), 404
        
    return jsonify({"message": f"Document {doc_id} deleted successfully"}), 200

def query_rag():
    """
    Query the RAG system with a prompt.
    """
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({"error": "Query is required"}), 400
        
    max_documents = data.get('max_documents', 3)
    
    result = rag_service.query(data['query'], max_documents=max_documents)
    return jsonify(result), 200