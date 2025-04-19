import React from 'react';
import { FiCopy } from 'react-icons/fi';
import { Message } from '../../types'; // Import Message type

interface ChatMessageProps {
  message: Message;
  onCopy: (content: string) => void;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message, onCopy }) => {
  const isAssistant = message.role === 'assistant';

  return (
    <div className={`message ${message.role}`}>
      <div className="message-content">{message.content}</div>
      {isAssistant && message.content && (
        <button
          className="copy-button"
          onClick={() => onCopy(message.content)}
          title="Copy response"
        >
          <FiCopy />
        </button>
      )}
    </div>
  );
};

export default ChatMessage;
