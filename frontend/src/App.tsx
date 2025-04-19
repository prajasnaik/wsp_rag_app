import './App.css';
import ChatInput from './components/ChatInput/ChatInput';
import MessageList from './components/MessageList/MessageList';
import { useChat } from './hooks/useChat';

function App() {
  const {
    messages,
    input,
    isLoading,
    error,
    handleInputChange,
    handleSendMessage,
    handleKeyDown,
    handleCopyClick,
    handleUploadClick,
    setError // Get setError to potentially clear errors
  } = useChat();

  // Clear error when user starts typing
  const handleInputChangeWithErrorClear = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    if (error) {
      setError(null);
    }
    handleInputChange(e);
  }

  return (
    <>
      {/* Display general error if API URL is missing */}
      {error && messages.length === 0 && (
        <div className="message assistant error-message" style={{ backgroundColor: '#5a2a2a', margin: '1rem 0' }}>
          Error: {error}
        </div>
      )}
      <MessageList
        messages={messages}
        isLoading={isLoading}
        error={error} // Pass error to MessageList to display inline if needed
        onCopy={handleCopyClick}
      />
      <ChatInput
        input={input}
        onInputChange={handleInputChangeWithErrorClear} // Use the wrapper
        onSendMessage={handleSendMessage}
        onKeyDown={handleKeyDown}
        onUploadClick={handleUploadClick}
        isLoading={isLoading}
      />
    </>
  );
}

export default App;
