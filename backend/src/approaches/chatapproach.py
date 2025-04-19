from .approach import Approach
import json

class ChatApproach(Approach):
    def __init__(
            self, 
            search_service, 
            llm_service
        ):
        super().__init__(
            search_service, 
            llm_service
        )

    def run_with_streaming(self, query_text, top=5):
        # First, get search results from the search service
        search_results = self.search(query_text, top)

        # If we got some search results, use them as context
        if search_results:
            context = "\n".join([result.content for result in search_results])
            prompt = f"Given the following information:\n{context}\n\nRespond to: {query_text}"
        else:
            # If no search results, just respond to the query directly
            prompt = query_text

        # Use the LLM service to get a streaming response
        for chunk in self.llm_service.query(prompt, search_results):
            # Yield each chunk as it comes in
            yield f"{json.dumps({'text': chunk})}\n\n"