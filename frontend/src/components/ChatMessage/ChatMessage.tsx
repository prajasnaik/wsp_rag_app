import React, { useState } from 'react';
import { FiCopy, FiCheck } from 'react-icons/fi'; // Add FiCheck for feedback
import ReactMarkdown from 'react-markdown'; // Import ReactMarkdown
import { Message } from '../../types';

interface ChatMessageProps {
  message: Message;
  onCopy: (content: string) => void;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message, onCopy }) => {
  const [isCopied, setIsCopied] = useState(false);
  const isAssistant = message.role === 'model';

  const handleCopy = () => {
    onCopy(message.content);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 1500); // Reset after 1.5 seconds
  };

  return (
    <div className={`message ${message.role}`}>
      <div className="message-content">
        {/* Render markdown for assistant, plain text for user */}
        {isAssistant ? (
          <ReactMarkdown>{message.content}</ReactMarkdown>
        ) : (
          message.content
        )}
      </div>
      {isAssistant && message.content && (
        <button
          className={`copy-button ${isCopied ? 'copied' : ''}`}
          onClick={handleCopy}
          title={isCopied ? "Copied!" : "Copy response"}
          disabled={isCopied} // Disable briefly after copying
        >
          {isCopied ? <FiCheck /> : <FiCopy />} {/* Show checkmark when copied */}
        </button>
      )}
    </div>
  );
};

export default ChatMessage;
