import React, { useRef, useEffect } from 'react';
import { FiSend, FiUpload } from 'react-icons/fi';

interface ChatInputProps {
  input: string;
  onInputChange: (event: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onSendMessage: () => void;
  onKeyDown: (event: React.KeyboardEvent<HTMLTextAreaElement>) => void;
  onUploadClick: () => void;
  isLoading: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({
  input,
  onInputChange,
  onSendMessage,
  onKeyDown,
  onUploadClick,
  isLoading,
}) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Adjust textarea height dynamically
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto'; // Reset height
      textarea.style.height = `${textarea.scrollHeight}px`; // Set to scroll height
    }
  }, [input]);

  return (
    <div className="input-area">
      <button onClick={onUploadClick} title="Upload File (Not Implemented)" disabled={isLoading}>
        <FiUpload />
      </button>
      <textarea
        ref={textareaRef}
        value={input}
        onChange={onInputChange}
        onKeyDown={onKeyDown}
        placeholder="Type your message..."
        rows={1} // Start with one row
        disabled={isLoading}
      />
      <button onClick={onSendMessage} disabled={isLoading || !input.trim()} title="Send Message">
        <FiSend />
      </button>
    </div>
  );
};

export default ChatInput;
