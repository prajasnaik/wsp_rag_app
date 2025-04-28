from flask import Blueprint, request, current_app, jsonify, stream_with_context, Response
from decorators.decorators import validate_auth_token
from services.document_service import DocumentService
from models import Document
from services.llm_service import LLMService
from services.search_service import SearchService

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
def get_document(doc_id: str):
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
def delete_document(doc_id: str):
    """
    Delete a document by ID.
    """
    document_service: DocumentService = current_app.config["DOCUMENT_SERVICE"]


    success = document_service.delete_document(doc_id)
    
    if not success:
        return jsonify({"error": "Document not found or could not be deleted"}), 404
        
    return jsonify({"message": f"Document {doc_id} deleted successfully"}), 200


@api_bp.route("/document/upload", methods=["POST"])
@validate_auth_token
def upload_file(): # Removed async as Flask doesn't need it here for standard requests
    if "file" not in request.files:
        return jsonify({"message": "No file part in the request", "status": "failed"}), 400

    file = request.files.get("file") # Use .get() for single file
    if not file or not file.filename:
        return jsonify({"message": "No selected file", "status": "failed"}), 400

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"message" : "File uploaded must be a PDF"}), 400
    
    # Correctly get the service from app config
    document_service: DocumentService = current_app.config["DOCUMENT_SERVICE"] 
    try:
        # Pass the file object to the service method
        document_service.upload_document(file)
    except Exception as e:
        current_app.logger.error(f"Error uploading document: {e}", exc_info=True)
        return jsonify({"message" : "Some error occurred while parsing or saving the PDF"}), 500

    return jsonify({"message": f"Successfully processed PDF: {file.filename}"}), 200 # Use 200 for success


@api_bp.route('/rag/query', methods=['POST'])
@validate_auth_token
async def generate_llm_response():
    query = request.json.get("query")
    history = request.json.get("history")

    if not isinstance(history, list):
        return jsonify({"error" : "history must be a list of messages"})
    if not query:
        return jsonify({"error": "query is required"}), 400
    
    chat_approach: ChatApproach = current_app.config["CHAT_APPROACH"]
    
    def generate():
        for chunk in chat_approach.run_with_streaming(query, history=history):
            yield chunk

    return Response(generate(), content_type='text/event-stream')

# Health check route
@api_bp.route('/health', methods=['GET'])
def health_check():
    return {"status": "ok"}, 200

def setup_application() -> None:
    initialize_google_client()
    document_service = DocumentService()
    search_service = SearchService()
    llm_service = LLMService(current_app.config["GOOGLE_CLIENT"], current_app.config["CONFIG"].MODEL, current_app.config["CONFIG"].SYSTEM_PROMPT)
    chat_approach = ChatApproach(search_service, llm_service)
    current_app.config["CHAT_APPROACH"] = chat_approach
    current_app.config["DOCUMENT_SERVICE"] = document_service
    current_app.config["SEARCH_SERVICE"] = search_service

def initialize_google_client() -> None:
    config = Config()
    client = Client(api_key=config.GOOGLE_API_KEY)
    current_app.config["GOOGLE_CLIENT"] = client
    current_app.config["CONFIG"] = config

