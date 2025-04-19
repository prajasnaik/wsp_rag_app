from .approach import Approach
from services.document_service import DocumentService
from services.llm_service import LLMService
from typing import Generator, Any


import json

class ChatApproach(Approach):
    def __init__(
            self, 
            search_service: DocumentService, 
            llm_service: LLMService
        ):
        super().__init__(
            search_service, 
            llm_service
        )

    def run_with_streaming(
            self, 
            query_text: str, 
            top: int = 5, 
            history: list[dict[str, str]]=None
        ) -> Generator[str, None, str]:
        
        # First, get search results from the search service
        search_results = self.search(query_text, top)

        # Use the LLM service to get a streaming response
        for chunk in self.llm_service.query(query_text, search_results, history):
            # Yield each chunk as it comes in
            yield f"{json.dumps({'text': chunk})}\n\n"