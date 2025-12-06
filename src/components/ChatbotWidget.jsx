import React, { useState, useRef, useEffect } from 'react';

export default function ChatbotWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hi! I am your AI assistant for this Physical AI & Robotics book. Ask me anything!' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const messagesEndRef = useRef(null);
  const API_URL = 'http://localhost:8000';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          session_id: sessionId || undefined
        })
      });

      const data = await response.json();
      
      if (!sessionId) setSessionId(data.session_id);
      
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: data.response,
        sources: data.sources 
      }]);
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, make sure the backend is running at http://localhost:8000' 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div style={{ position: 'fixed', bottom: '20px', right: '20px', zIndex: 9999 }}>
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          style={{
            backgroundColor: '#2563eb',
            color: 'white',
            borderRadius: '50%',
            width: '60px',
            height: '60px',
            border: 'none',
            cursor: 'pointer',
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
            fontSize: '28px'
          }}
        >
          💬
        </button>
      )}

      {isOpen && (
        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          boxShadow: '0 10px 25px rgba(0,0,0,0.2)',
          width: '384px',
          height: '600px',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <div style={{
            backgroundColor: '#2563eb',
            color: 'white',
            padding: '16px',
            borderTopLeftRadius: '12px',
            borderTopRightRadius: '12px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <div>
              <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 'bold' }}>AI Assistant</h3>
              <p style={{ margin: 0, fontSize: '12px', opacity: 0.9 }}>Physical AI & Robotics</p>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              style={{
                background: 'none',
                border: 'none',
                color: 'white',
                cursor: 'pointer',
                fontSize: '24px',
                padding: '0',
                width: '30px',
                height: '30px'
              }}
            >
              ✕
            </button>
          </div>

          <div style={{
            flex: 1,
            overflowY: 'auto',
            padding: '16px',
            backgroundColor: '#f9fafb'
          }}>
            {messages.map((msg, idx) => (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                  marginBottom: '16px'
                }}
              >
                <div
                  style={{
                    maxWidth: '80%',
                    padding: '12px',
                    borderRadius: '8px',
                    backgroundColor: msg.role === 'user' ? '#2563eb' : 'white',
                    color: msg.role === 'user' ? 'white' : '#1f2937',
                    boxShadow: msg.role === 'assistant' ? '0 1px 2px rgba(0,0,0,0.1)' : 'none'
                  }}
                >
                  <p style={{ margin: 0, fontSize: '14px', whiteSpace: 'pre-wrap' }}>{msg.content}</p>
                  {msg.sources && msg.sources.length > 0 && (
                    <div style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px solid #e5e7eb' }}>
                      <p style={{ margin: 0, fontSize: '11px', color: '#6b7280', fontWeight: 600 }}>Sources:</p>
                      {msg.sources.map((source, i) => (
                        <p key={i} style={{ margin: '4px 0', fontSize: '11px', color: '#6b7280' }}>
                          📚 {source.title}
                        </p>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                <div style={{
                  backgroundColor: 'white',
                  padding: '12px',
                  borderRadius: '8px',
                  boxShadow: '0 1px 2px rgba(0,0,0,0.1)'
                }}>
                  ⏳ Thinking...
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div style={{ 
            padding: '16px', 
            borderTop: '1px solid #e5e7eb', 
            backgroundColor: 'white',
            borderBottomLeftRadius: '12px',
            borderBottomRightRadius: '12px'
          }}>
            <div style={{ display: 'flex', gap: '8px' }}>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about the book..."
                disabled={loading}
                style={{
                  flex: 1,
                  border: '1px solid #d1d5db',
                  borderRadius: '8px',
                  padding: '10px 12px',
                  fontSize: '14px',
                  outline: 'none'
                }}
              />
              <button
                onClick={handleSendMessage}
                disabled={loading || !input.trim()}
                style={{
                  backgroundColor: '#2563eb',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '10px 20px',
                  cursor: loading || !input.trim() ? 'not-allowed' : 'pointer',
                  opacity: loading || !input.trim() ? 0.5 : 1,
                  fontSize: '18px'
                }}
              >
                ➤
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}