# RAG Application with Gemini 2.0 Flash and ChromaDB

This repository contains a Retrieval-Augmented Generation (RAG) application that leverages Google's Gemini 2.0 Flash LLM and ChromaDB as a vector database. The application is designed to be deployed on Azure.

## Overview

This RAG application enhances the capabilities of Gemini 2.0 Flash by providing it with relevant context from a knowledge base stored in ChromaDB. This approach enables more accurate and contextually appropriate responses. This is also a single page application and hence will be served directly via the API. It must be built before running though.

## Features

- **Gemini 2.0 Flash Integration**: Utilizes Google's powerful LLM for generating responses
- **ChromaDB Vector Database**: Stores and retrieves document embeddings efficiently
- **RAG Architecture**: Enhances LLM responses with relevant retrieved context
- **Google OAuth**: A fully functioning implementation of Google OAuth for security with refresh token system. 
- **Simple UI**: Basic interface for user interaction

## Getting Started

### Prerequisites

- Python 3.8+
- Google API key for Gemini access
- Azure account for deployment
- React-vite setup
- npm
- node

### Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/prajasnaik/wsp_rag_app.git
     cd wsp_rag_app
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up environment variables:
    ```bash
    export GOOGLE_API_KEY="your_gemini_api_key"
    ```

### Usage

1. Build the UI:
```
npm run build
```

1. Start the application:
    ```bash
    python app.py
    ```

2. Access the UI through your browser at `http://localhost:5000`

## Deployment to Azure

This application will add support for Azure Deployments in the future.

## Future Enhancements

- OAuth 2.0 authentication for secure access
- Enhanced UI with better visualization options
- Expanded document processing capabilities
- Performance optimizations for large document collections

## License

[MIT](LICENSE)

## Acknowledgements

- Google for Gemini 2.0 Flash
- ChromaDB team for the vector database
