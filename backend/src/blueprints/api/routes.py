from flask import Blueprint, request, current_app, jsonify, stream_with_context, Response

from services.document_service import DocumentService, Document
from services.llm_service import LLMService

from approaches.chatapproach import ChatApproach
from config import Config


from google.genai import Client

# Create the Blueprint for API routes
api_bp = Blueprint('api', __name__)

# Document routes
api_bp.route('/documents', methods=['GET'])
def get_documents():
    """
    Get all documents or search for documents.
    """
    query = request.args.get('query')
    document_service: DocumentService = current_app.config["DOCUMENT_SERVICE"]
    if query:
        # Search documents by query
        documents = document_service.search_documents(query)
    else:
        # Get all documents
        documents = document_service.list_documents()
        
    return jsonify({
        "documents": [doc.to_dict() for doc in documents]
    }), 200


api_bp.route('/documents/<string:doc_id>', methods=['GET'])
def get_document(doc_id):
    """
    Get a specific document by ID.
    """
    document_service: DocumentService = current_app.config["DOCUMENT_SERVICE"]
    document = document_service.get_document(doc_id)

    
    if not document:
        return jsonify({"error": "Document not found"}), 404
        
    return jsonify(document.to_dict()), 200

api_bp.route('/documents', methods=['POST'])
def create_document():
    """
    Create a new document.
    """
    data = request.get_json()

    document_service: DocumentService = current_app.config["DOCUMENT_SERVICE"]


    if not data or 'text' not in data:
        return jsonify({"error": "Text is required"}), 400
        
    document = Document(
        text=data['text'],
        metadata=data.get('metadata', {})
    )
    
    document = document_service.add_document(document)
    return jsonify(document.to_dict()), 201    

api_bp.route('/documents/<string:doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """
    Delete a document by ID.
    """
    document_service: DocumentService = current_app.config["DOCUMENT_SERVICE"]


    success = document_service.delete_document(doc_id)
    
    if not success:
        return jsonify({"error": "Document not found or could not be deleted"}), 404
        
    return jsonify({"message": f"Document {doc_id} deleted successfully"}), 200

# RAG routes
@api_bp.route('/rag/query', methods=['POST'])
async def generate_llm_response():
    query = request.json.get("query")
    if not query:
        return jsonify({"error": "query is required"}), 400
    
    chat_approach: ChatApproach = current_app.config["CHAT_APPROACH"]
    
    def generate():
        for chunk in chat_approach.run_with_streaming(query):
            yield chunk

    return Response(generate(), content_type='text/event-stream')

# Health check route
@api_bp.route('/health', methods=['GET'])
def health_check():
    return {"status": "ok"}, 200

def setup_application():
    initialize_google_client()
    search_service = DocumentService()
    llm_service = LLMService(current_app.config["GOOGLE_CLIENT"], current_app.config["CONFIG"].MODEL, current_app.config["CONFIG"].SYSTEM_PROMPT)
    chat_approach = ChatApproach(search_service, llm_service)
    current_app.config["CHAT_APPROACH"] = chat_approach
    current_app.config["DOCUMENT_SERVICE"] = search_service

def initialize_google_client():
    config = Config()
    client = Client(api_key=config.GOOGLE_API_KEY)
    current_app.config["GOOGLE_CLIENT"] = client
    current_app.config["CONFIG"] = config

    