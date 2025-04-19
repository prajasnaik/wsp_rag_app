import React, { useRef, useEffect } from 'react';
import ChatMessage from '../ChatMessage/ChatMessage';
import { Message } from '../../types'; // Import Message type

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  onCopy: (content: string) => void;
}

const MessageList: React.FC<MessageListProps> = ({ messages, isLoading, error, onCopy }) => {
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="chat-container" ref={chatContainerRef}>
      {messages.map((msg) => (
        <ChatMessage key={msg.id} message={msg} onCopy={onCopy} />
      ))}
      {isLoading && messages[messages.length - 1]?.role === 'assistant' && messages[messages.length - 1]?.content === '' && (
        <div className="loading-indicator">Assistant is thinking...</div>
      )}
      {/* Display error inline if it occurs after messages have started */}
      {error && !isLoading && (
         <div className="message assistant error-message" style={{ backgroundColor: '#5a2a2a' }}>
           Error: {error}
         </div>
      )}
    </div>
  );
};

export default MessageList;
