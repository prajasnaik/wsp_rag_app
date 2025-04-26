import { useState, useCallback } from 'react';
import { Message } from '../types'; // Import Message type
import { useAuth } from './AuthContext';

// --- Constants ---
const API_BASE_URL = import.meta.env.VITE_API_URL || ''; // Get API URL from .env
    const CHAT_API_ENDPOINT = `${API_BASE_URL}/rag/query`; // Specific endpoint
const UPLOAD_API_ENDPOINT = `${API_BASE_URL}/document/upload`; // Upload endpoint

export const useChat = () => {
    const {refresh } = useAuth();
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [isUploading, setIsUploading] = useState(false); // Uploading state
    const [uploadError, setUploadError] = useState<string | null>(null); // Upload error state
    const [uploadSuccessMessage, setUploadSuccessMessage] = useState<string | null>(null); // Upload success state

    const handleInputChange = useCallback((event: React.ChangeEvent<HTMLTextAreaElement>) => {
        setInput(event.target.value);
        // Clear errors/success messages on new input
        if (error) setError(null);
        if (uploadError) setUploadError(null);
        if (uploadSuccessMessage) setUploadSuccessMessage(null);
    }, [error, uploadError, uploadSuccessMessage]); // Add dependencies

    const handleSendMessage = useCallback(async () => {
        const trimmedInput = input.trim();
        if (!trimmedInput || isLoading || isUploading) return;

        if (!API_BASE_URL) {
            setError("API URL is not configured. Please set VITE_API_URL in your .env file.");
            return;
        }

        const newUserMessage: Message = {
            id: Date.now().toString() + '-user',
            role: 'user',
            content: trimmedInput,
        };

        // Add user message
        setInput('');
        setIsLoading(true);
        setError(null);
        setUploadError(null); // Clear upload errors when sending message
        setUploadSuccessMessage(null);

        try {
            // Prepare the history of messages excluding the current user input
            const history = messages.map(({ role, content }) => ({ role, text: content }));
            setMessages((prevMessages) => [...prevMessages, newUserMessage])
            console.log("Sending request")
            let response = await fetch(CHAT_API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: trimmedInput,
                    history: history, // Include the history in the request
                }),
            });

            if (response.status === 401 || response.status === 403) {
                // Try to refresh the token and retry
                await refresh();
                response = await fetch(CHAT_API_ENDPOINT, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        query: trimmedInput,
                        history: history,
                    }),
                });
            }

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: 'Failed to parse error response' }));
                throw new Error(`API Error (${response.status}): ${errorData.error || response.statusText}`);
            }

            if (!response.body) {
                throw new Error('Response body is null');
            }

            // Add an empty assistant message bubble only when streaming starts
            setMessages((prevMessages) => [
                ...prevMessages,
                { id: Date.now().toString() + '-model', role: 'model', content: '' },
            ]);

            // Process the stream
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let assistantMessageContent = '';
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const parts = buffer.split('\n\n');
                buffer = parts.pop() || ''; // Keep incomplete part

                for (const part of parts) {
                    if (part.trim()) {
                        try {
                            const chunkData = JSON.parse(part.trim());
                            if (chunkData.text) {
                                assistantMessageContent += chunkData.text;
                                setMessages((prevMessages) => {
                                    const updatedMessages = [...prevMessages];
                                    const lastMessageIndex = updatedMessages.length - 1;
                                    if (lastMessageIndex >= 0 && updatedMessages[lastMessageIndex].role === 'model') {
                                        updatedMessages[lastMessageIndex].content = assistantMessageContent;
                                    }
                                    return updatedMessages;
                                });
                            }
                        } catch (e) {
                            console.error('Failed to parse stream chunk:', part, e);
                        }
                    }
                }
            }

            // Handle final buffer chunk
            if (buffer.trim()) {
                try {
                    const chunkData = JSON.parse(buffer.trim());
                    if (chunkData.text) {
                        assistantMessageContent += chunkData.text;
                        setMessages((prevMessages) => {
                            const updatedMessages = [...prevMessages];
                            const lastMessageIndex = updatedMessages.length - 1;
                            if (lastMessageIndex >= 0 && updatedMessages[lastMessageIndex].role === 'model') {
                                updatedMessages[lastMessageIndex].content = assistantMessageContent;
                            }
                            return updatedMessages;
                        });
                    }
                } catch (e) {
                    console.error('Failed to parse final buffer chunk:', buffer, e);
                }
            }
        } catch (err: any) {
            console.error('Error sending message:', err);
            setError(err.message || 'An unexpected error occurred.');
            // Remove the placeholder assistant message on error
            setMessages((prevMessages) => {
                const lastMessage = prevMessages[prevMessages.length - 1];
                if (lastMessage && lastMessage.role === 'model' && lastMessage.content === '') {
                    return prevMessages.slice(0, -1);
                }
                return prevMessages;
            });
        } finally {
            setIsLoading(false);
        }
    }, [input, isLoading, isUploading, messages, refresh]); // Add refresh to dependencies

    const handleKeyDown = useCallback((event: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (event.key === 'Enter' && !event.shiftKey && !isUploading) { // Prevent send while uploading
            event.preventDefault();
            handleSendMessage();
        }
    }, [handleSendMessage, isUploading]); // Dependency

    const handleCopyClick = useCallback((content: string) => {
        navigator.clipboard.writeText(content)
            .then(() => {
                console.log('Copied to clipboard!');
                // Optional: Add temporary visual feedback here
            })
            .catch(err => {
                console.error('Failed to copy text: ', err);
                setError('Failed to copy text to clipboard.'); // Show error feedback
            });
    }, []);

    const handleFileSelect = useCallback(async (file: File) => {
        if (!file || isUploading || isLoading) return;

        if (!API_BASE_URL) {
            setUploadError("API URL is not configured. Please set VITE_API_URL in your .env file.");
            return;
        }

        if (file.type !== 'application/pdf') {
            setUploadError('Invalid file type. Please upload a PDF.');
            return;
        }

        setIsUploading(true);
        setUploadError(null);
        setError(null); // Clear chat errors
        setUploadSuccessMessage(null);

        const formData = new FormData();
        formData.append('file', file); // Key must match backend ('file')

        try {
            const response = await fetch(UPLOAD_API_ENDPOINT, {
                method: 'POST',
                body: formData,
                // Note: Don't set Content-Type header manually for FormData,
                // the browser will set it correctly with the boundary.
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.message || `Upload failed with status: ${response.status}`);
            }

            console.log('Upload successful:', result);
            setUploadSuccessMessage(result.message || 'File uploaded successfully!');
            // Optionally add a message to the chat confirming upload?
            // setMessages(prev => [...prev, { id: Date.now().toString(), role: 'system', content: `Uploaded: ${file.name}` }]);

        } catch (err: any) {
            console.error('Error uploading file:', err);
            setUploadError(err.message || 'An unexpected error occurred during upload.');
        } finally {
            setIsUploading(false);
        }
    }, [isLoading, isUploading]); // Add dependencies

    const handleUploadClick = useCallback(() => {
        // Placeholder for upload functionality
        alert('Upload functionality not implemented yet.');
        // In a real app, you might trigger a file input click here
    }, []);

    return {
        messages,
        input,
        isLoading,
        error,
        isUploading, // Expose uploading state
        uploadError, // Expose upload error
        uploadSuccessMessage, // Expose upload success
        handleInputChange,
        handleSendMessage,
        handleKeyDown,
        handleCopyClick,
        handleUploadClick,
        handleFileSelect, // Expose file select handler
        setError, // Expose setError if needed externally, e.g., to clear errors
        setUploadError, // Expose setters if needed
        setUploadSuccessMessage
    };
};
