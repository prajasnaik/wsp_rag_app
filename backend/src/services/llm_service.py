from .base_service import BaseService
from google.genai import Client
from google.genai import types
from .document_service import Document
from typing import Generator

class LLMService(BaseService):
    def __init__(
        self, 
        google_client: Client,
        model: str,
        system_prompt="",
        few_shot_examples: list[dict[str, str]]=None
    ):
        super().__init__()
        self.google_client = google_client
        self.model = model
        self.system_prompt = system_prompt
        self.few_shot_examples = few_shot_examples or []
    
    def set_system_prompt(
        self, 
        prompt: str
    ):
        self.system_prompt = prompt
    
    def add_few_shot_example(
            self, 
            user_input: str, 
            assistant_response: str
        ):
        self.few_shot_examples.append({
            "user": user_input,
            "model": assistant_response
        })
    
    def query(
            self, 
            query_text: str, 
            documents: list[Document] = [], 
            history: list[dict[str, str]] = None
        ) -> Generator[str, None, str]:
        contents = []            
        
        for example in self.few_shot_examples:
            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=example["user"])]
                )
            )
            contents.append(
                types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=example["model"])]
                )
            )

        if documents:
            for document in documents:
                contents.append(
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=document.text)]
                    )
                )
        
        if history:
            for message in history:
                contents.append(
                    types.Content(
                        role=message["role"],
                        parts=[types.Part.from_text(text=message["text"])]
                    )
                )

        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=query_text)]
            )
        )
        
        generate_content_config = types.GenerateContentConfig(
            response_mime_type="text/plain",
            system_instruction= self.system_prompt
        )

        for chunk in self.google_client.models.generate_content_stream(
            model=self.model,
            contents=contents,
            config=generate_content_config,
        ):
            yield chunk.text
