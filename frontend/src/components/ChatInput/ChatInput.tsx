import React, { useRef, useEffect } from 'react';
import { FiSend, FiUpload, FiLoader } from 'react-icons/fi';

interface ChatInputProps {
  input: string;
  onInputChange: (event: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onSendMessage: () => void;
  onKeyDown: (event: React.KeyboardEvent<HTMLTextAreaElement>) => void;
  onFileSelect: (file: File) => void;
  isLoading: boolean;
  isUploading: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({
  input,
  onInputChange,
  onSendMessage,
  onKeyDown,
  onFileSelect,
  isLoading,
  isUploading,
}) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Adjust textarea height dynamically
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  }, [input]);

  const handleUploadButtonClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      onFileSelect(file);
      event.target.value = '';
    }
  };

  return (
    <div className="input-area">
      <input
        type="file"
        ref={fileInputRef}
        style={{ display: 'none' }}
        accept=".pdf"
        onChange={handleFileChange}
      />
      <button
        onClick={handleUploadButtonClick}
        title={isUploading ? "Uploading..." : "Upload PDF"}
        disabled={isLoading || isUploading}
        className={`upload-button ${isUploading ? 'uploading' : ''}`}
      >
        {isUploading ? <FiLoader className="spinner" /> : <FiUpload />}
      </button>
      <textarea
        ref={textareaRef}
        value={input}
        onChange={onInputChange}
        onKeyDown={onKeyDown}
        placeholder="Type your message..."
        rows={1}
        disabled={isLoading || isUploading}
      />
      <button
        onClick={onSendMessage}
        disabled={isLoading || isUploading || !input.trim()}
        title="Send Message"
      >
        <FiSend />
      </button>
    </div>
  );
};

export default ChatInput;
