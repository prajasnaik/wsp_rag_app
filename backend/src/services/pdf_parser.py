from werkzeug.datastructures import FileStorage
from PyPDF2 import PdfReader

class PDFParser:
    def parse(
        self,
        file: FileStorage
    ) -> list[tuple[dict[str, str], list[str]]]:
        pdf_reader = PdfReader(file)
        extracted_chunks = []
        for page_number, page in enumerate(pdf_reader.pages):
            metadata = {
                "name" : file.filename,
                "page_no" : page_number
            }

            text = page.extract_text()
            page_chunks = self.chunk_text(text)
            extracted_chunks.append((metadata, page_chunks))
        
        return extracted_chunks

    
    def chunk_text(
            self,
            text: str, 
            chunk_size: int = 200,
            overlap: int = 80
        ) -> list[str]:

        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        return chunks
        
        