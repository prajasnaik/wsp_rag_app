from .base_service import BaseService
from google.genai import Client
from google.genai import types
from .document_service import Document

class LLMService(BaseService):
    def __init__(
        self, 
        google_client: Client,
        model,
        system_prompt="",
        few_shot_examples=None
    ):
        super().__init__()
        self.google_client = google_client
        self.model = model
        self.system_prompt = system_prompt
        self.few_shot_examples = few_shot_examples or []
    
    def set_system_prompt(self, prompt):
        self.system_prompt = prompt
    
    def add_few_shot_example(self, user_input, assistant_response):
        self.few_shot_examples.append({
            "user": user_input,
            "model": assistant_response
        })
    
    def query(self, query_text, documents: list[Document] = []):
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
