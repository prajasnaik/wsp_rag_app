import { useState, useCallback } from 'react';
import { Message } from '../types'; // Import Message type

// --- Constants ---
const API_BASE_URL = import.meta.env.VITE_API_URL || ''; // Get API URL from .env
const API_ENDPOINT = `${API_BASE_URL}/rag/query`; // Specific endpoint

export const useChat = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleInputChange = useCallback((event: React.ChangeEvent<HTMLTextAreaElement>) => {
        setInput(event.target.value);
    }, []);

    const handleSendMessage = useCallback(async () => {
        const trimmedInput = input.trim();
        if (!trimmedInput || isLoading) return;

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

        try {
            // Prepare the history of messages excluding the current user input
            const history = messages.map(({ role, content }) => ({ role, text: content }));
            setMessages((prevMessages) => [...prevMessages, newUserMessage])
            console.log("Sending request")
            const response = await fetch(API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: trimmedInput,
                    history: history, // Include the history in the request
                }),
            });

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
    }, [input, isLoading, messages]); // Dependencies for useCallback

    const handleKeyDown = useCallback((event: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            handleSendMessage();
        }
    }, [handleSendMessage]); // Dependency

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
        handleInputChange,
        handleSendMessage,
        handleKeyDown,
        handleCopyClick,
        handleUploadClick,
        setError // Expose setError if needed externally, e.g., to clear errors
    };
};
