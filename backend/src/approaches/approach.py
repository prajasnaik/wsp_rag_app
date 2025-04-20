from models import Document
from abc import ABC
from services.search_service import SearchService
from typing import List, AsyncGenerator, Any
from services.llm_service import LLMService

class Approach(ABC):

    def __init__(
        self,
        search_service: SearchService,
        llm_service: LLMService,
    ):
        self.search_service = search_service
        self.llm_service = llm_service
    
    def search(
        self, 
        text: str, 
        top: int,
        history: dict[str, str] = None
    ) -> List[Document]:
        result = self.search_service.search_documents(text, top if top else 5)
        return result
    
    async def run_with_streaming(
        self,
        query_text: str,
        history: list[dict[str, str]]
    ) -> AsyncGenerator[str, None]:
        raise NotImplementedError
    
