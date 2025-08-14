import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null); // Ref to scroll to the bottom

  // Function to automatically scroll to the latest message
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]); // Dependency array ensures this runs when messages change

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) return;

    const userMessage = {
      role: 'user',
      parts: [{ text: userInput }],
    };
    
    // Add user message to state and prepare for streaming
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setUserInput('');

    try {
      // The history sent to the backend excludes the latest user message,
      // which is sent separately in the `message` field.
      const history = messages.map(msg => ({
        role: msg.role,
        parts: msg.parts,
      }));

      const apiBaseUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${apiBaseUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userInput,
          history: history,
        }),
      });

      if (!response.body) return;

      // Prepare to handle the stream
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantResponse = '';

      // Add a placeholder for the assistant's message
      setMessages(prev => [...prev, { role: 'assistant', parts: [{ text: '' }] }]);

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        assistantResponse += chunk;

        // Update the last message (the assistant's) with the new chunk
        setMessages(prevMessages => {
          const updatedMessages = [...prevMessages];
          updatedMessages[updatedMessages.length - 1] = {
            ...updatedMessages[updatedMessages.length - 1],
            parts: [{ text: assistantResponse }],
          };
          return updatedMessages;
        });
      }
    } catch (error) {
      console.error('Failed to fetch:', error);
      setMessages(prev => [...prev, { role: 'assistant', parts: [{ text: "Error: Could not connect to the server." }] }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-box">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            <p>{msg.parts[0].text}</p>
          </div>
        ))}
        {isLoading && (
          <div className="message assistant">
            <p className="typing-indicator">...</p>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <form onSubmit={handleSubmit} className="chat-form">
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          placeholder="Ask me anything..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading}>
          Send
        </button>
      </form>
    </div>
  );
}

export default App;