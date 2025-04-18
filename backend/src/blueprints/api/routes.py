from flask import Blueprint
from .controllers.document_controller import (
    get_documents, get_document, create_document, 
    delete_document, query_rag
)

# Create the Blueprint for API routes
api_bp = Blueprint('api', __name__)

# Document routes
api_bp.route('/documents', methods=['GET'])(get_documents)
api_bp.route('/documents/<string:doc_id>', methods=['GET'])(get_document)
api_bp.route('/documents', methods=['POST'])(create_document)
api_bp.route('/documents/<string:doc_id>', methods=['DELETE'])(delete_document)

# RAG routes
api_bp.route('/rag/query', methods=['POST'])(query_rag)

# Health check route
@api_bp.route('/health', methods=['GET'])
def health_check():
    return {"status": "ok"}, 200