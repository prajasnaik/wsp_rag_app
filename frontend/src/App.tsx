import './App.css';
import ChatInput from './components/ChatInput/ChatInput';
import MessageList from './components/MessageList/MessageList';
import { useChat } from './hooks/useChat';
import { TbHexagonLetterP} from "react-icons/tb";
import { AuthProvider, useAuth } from './hooks/AuthContext'
import Login from './components/Login/Login';

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
  const {
    isAuthenticated,
    isLoading: authLoading,
    logout
  } = useAuth();

  const hasStartedChat = messages.length > 0;

  // Clear errors/messages when user starts typing
  const handleInputChangeWrapper = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    if (error) setError(null);
    if (uploadError) setUploadError(null);
    if (uploadSuccessMessage) setUploadSuccessMessage(null);
    handleInputChange(e);
  }

  // Show loading indicator while checking auth status
  if (authLoading) {
    return (
      <div className="loading-container">
        <TbHexagonLetterP className="ai-icon spinner" />
        <p>Loading...</p>
      </div>
    );
  }

  // Show login screen if not authenticated
  if (!isAuthenticated) {
    return <Login />;
  }

  return (
    <div className={`app-container ${hasStartedChat ? 'chat-active' : 'initial-state'}`}>
      {/* Add logout button in the top right */}
      <button style={{position:'absolute',top:20,right:20}} onClick={logout}>Logout</button>

      {!hasStartedChat && (
        <div className="initial-view">
          <TbHexagonLetterP className="ai-icon" />
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

export default function AppWithProvider() {
  return (
    <AuthProvider>
      <App />
    </AuthProvider>
  );
}
