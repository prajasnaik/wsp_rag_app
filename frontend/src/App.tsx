import './App.css';
import ChatInput from './components/ChatInput/ChatInput';
import MessageList from './components/MessageList/MessageList';
import { useChat } from './hooks/useChat';
import { TbHexagonLetterA } from "react-icons/tb";

function App() {
  const {
    messages,
    input,
    isLoading,
    error,
    isUploading,
    uploadError,
    uploadSuccessMessage,
    handleInputChange,
    handleSendMessage,
    handleKeyDown,
    handleCopyClick,
    handleFileSelect,
    setError,
    setUploadError,
    setUploadSuccessMessage
  } = useChat();

  const hasStartedChat = messages.length > 0;

  // Clear errors/messages when user starts typing
  const handleInputChangeWrapper = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    if (error) setError(null);
    if (uploadError) setUploadError(null);
    if (uploadSuccessMessage) setUploadSuccessMessage(null);
    handleInputChange(e);
  }

  return (
    <div className={`app-container ${hasStartedChat ? 'chat-active' : 'initial-state'}`}>
      {!hasStartedChat && (
        <div className="initial-view">
          <TbHexagonLetterA className="ai-icon" />
          <h1>What can I help with?</h1>
          {/* Display config error in initial state */}
          {error && error.includes("API URL is not configured") && (
            <div className="message assistant error-message" style={{ margin: '1rem 0' }}>
              Error: {error}
            </div>
          )}
          {/* Display upload status in initial state */}
          {uploadError && (
            <div className="message assistant error-message" style={{ margin: '1rem 0' }}>
              Upload Error: {uploadError}
            </div>
          )}
          {uploadSuccessMessage && (
            <div className="message assistant success-message" style={{ margin: '1rem 0' }}>
              {uploadSuccessMessage}
            </div>
          )}
        </div>
      )}

      <div className={`message-list-wrapper ${hasStartedChat ? 'visible' : 'hidden'}`}>
        <MessageList
          messages={messages}
          isLoading={isLoading}
          error={error}
          onCopy={handleCopyClick}
        />
      </div>

      {/* Display upload status messages above input when chat is active */}
      {hasStartedChat && uploadError && (
        <div className="message assistant error-message status-message-inline">
          Upload Error: {uploadError}
        </div>
      )}
      {hasStartedChat && uploadSuccessMessage && (
        <div className="message assistant success-message status-message-inline">
          {uploadSuccessMessage}
        </div>
      )}

      <ChatInput
        input={input}
        onInputChange={handleInputChangeWrapper}
        onSendMessage={handleSendMessage}
        onKeyDown={handleKeyDown}
        onFileSelect={handleFileSelect}
        isLoading={isLoading}
        isUploading={isUploading}
      />
    </div>
  );
}

export default App;
